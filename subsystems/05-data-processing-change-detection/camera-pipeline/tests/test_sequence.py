"""Sequence mechanics have known pixel geometry independent of the learned weights."""

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from pavewatch.artifacts import sha256
from pavewatch.sequence import checked_config
from pavewatch.sequence_eval import match
from pavewatch.sequence_geometry import register, warp
from pavewatch.sequence_inputs import grid_frames, read_session
from pavewatch.sequence_regions import Region, agreement, grid, merge
from pavewatch.sequence_tracks import Track, collate, multiview


@pytest.fixture
def cfg():
    return checked_config(Path("configs/sequence-v1.json"))


@pytest.fixture
def session(tmp_path):
    rng = np.random.default_rng(22)
    source = rng.integers(40, 210, (350, 660, 3), dtype=np.uint8)
    rows = []
    for i in range(7):
        f = tmp_path / f"{i}.png"
        Image.fromarray(source[:, 12 * i : 12 * i + 500]).save(f)
        rows.append(
            {
                "id": str(i),
                "timestamp": 200 * i,
                "sha256": sha256(f),
                "path": f.name,
                "width": 500,
                "height": 350,
                "exif_orientation": 1,
            }
        )
    doc = {
        "schema_version": 1,
        "pass_id": "test",
        "site_id": "test",
        "clock_basis": "fixture",
        "timestamp_unit": "ms",
        "nominal_fps": 5,
        "capture_profile": "fixture",
        "frames": rows,
    }
    path = tmp_path / "session.json"
    path.write_text(json.dumps(doc))
    return path, doc


def region(i, score=0.46):
    return Region(
        i,
        0,
        [230 - 12 * i, 150, 290 - 12 * i, 190],
        np.full((40, 60), 255, np.uint8),
        score,
        ("whole",),
        [0, 0, 500, 350],
        [1, 1],
    )


@pytest.mark.parametrize(
    "bad", ["duplicate_id", "order", "unit", "empty", "dimension", "content", "missing", "corrupt"]
)
def test_invalid_session(session, bad):
    path, doc = session
    rows = doc["frames"]
    if bad == "duplicate_id":
        rows[1]["id"] = rows[0]["id"]
    elif bad == "order":
        rows[1]["timestamp"] = 0
    elif bad == "unit":
        doc["timestamp_unit"] = "seconds-ish"
    elif bad == "empty":
        rows.clear()
    elif bad == "dimension":
        rows[0]["width"] += 1
    elif bad == "content":
        rows[1].update(path=rows[0]["path"], sha256=rows[0]["sha256"])
    elif bad == "missing":
        rows[0]["path"] = "absent.jpg"
    else:
        image = path.parent / rows[0]["path"]
        image.write_bytes(b"invalid image")
        rows[0]["sha256"] = sha256(image)
    path.write_text(json.dumps(doc))
    with pytest.raises((ValueError, OSError)):
        read_session(path, 1.6)


def test_registration_gap_and_unique_tracks(session, cfg):
    path, doc = session
    doc["frames"][4] = {"id": "4", "timestamp": 800, "missing": True}
    path.write_text(json.dumps(doc))
    _, frames, events = read_session(path, 1.6)
    H, q = register(frames[0], frames[3], region(0).box, cfg)
    assert q["accepted"] and q["inliers"] >= 8
    point = warp([[260, 170]], H)[0]
    assert np.linalg.norm(point - [224, 170]) < 2
    assert register(frames[3], frames[4], region(3).box, cfg)[0] is None
    assert events[0]["reason"] == "missing"
    assert grid_frames(frames, 1) & {4, 5}
    props = []
    for f in frames:
        r = region(int(f.id))
        r.frame = f.index
        props.append([r])
    tracks, _ = collate(props, frames, cfg, 200000000)
    assert sorted(len(t.sightings) for t in tracks) == [2, 4]


def test_single_missing_interval_and_hash(session):
    path, doc = session
    doc["frames"].pop(2)
    path.write_text(json.dumps(doc))
    _, frames, events = read_session(path, 1.6)
    assert frames[1].segment != frames[2].segment and events[0]["reason"] == "timestamp_gap"
    doc["frames"][0]["sha256"] = "0" * 64
    path.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="SHA-256"):
        read_session(path, 1.6)


def test_grid_merge_and_duplicate_accounting(session):
    frames = read_session(session[0], 1.6)[1]
    cover = np.zeros((350, 500), bool)
    for x, y, X, Y in grid(frames[0], 0.256, 0.25):
        cover[y:Y, x:X] = True
    assert cover.all()
    a, b = region(0), region(0, 0.40)
    b.sources = ("grid",)
    combined = merge([a, b], 0.55)
    assert len(combined) == 1 and set(combined[0].sources) == {"grid", "whole"}
    assert agreement(a, combined[0]) == 1
    assert len(match([[(0, 0.9)], [(0, 0.8)]])) == 1
    assert len(match([[(0, 0.8), (1, 0.7)], [(0, 0.9)]])) == 2


def test_multiview_promotes_and_keeps_strong_single(session, cfg, monkeypatch):
    frames = read_session(session[0], 1.6)[1]
    reference = region(3, 0.48)
    track = Track([reference], [])

    def rescore(f, target, model, cfg):
        return [region(f.index, 0.46)]

    monkeypatch.setattr("pavewatch.sequence_tracks.crop_scan", rescore)
    found = multiview(track, frames, 200000000, None, cfg, Counter())
    assert found[-1] == "aligned_views" and len(found[2]) == 3
    assert {r.frame for r, H, q, qual in found[2]} == {0, 3, 6}
    assert found[4].any()
    assert (
        multiview(Track([region(0, 0.46)], []), frames[:1], 200000000, None, cfg, Counter()) is None
    )
    single = multiview(Track([region(0, 0.89)], []), frames[:1], 200000000, None, cfg, Counter())
    assert single[-1] == "strong_single"


def test_reject_uniform_frames(session, cfg):
    path, doc = session
    for i, row in enumerate(doc["frames"]):
        p = path.parent / row["path"]
        Image.fromarray(np.full((350, 500, 3), 100 + i, np.uint8)).save(p)
        row["sha256"] = sha256(p)
    path.write_text(json.dumps(doc))
    frames = read_session(path, 1.6)[1]
    H, q = register(frames[0], frames[1], region(0).box, cfg)
    assert H is None and not q["accepted"]


def test_shared_crop_cannot_emit_two_findings(session, cfg):
    from pavewatch.sequence_tracks import consolidate

    frames = read_session(session[0], 1.6)[1][:1]
    t = Track([region(0, 0.89)], [])
    result = multiview(t, frames, 200000000, None, cfg, Counter())
    kept = consolidate([(t, result), (t, result)], cfg["merge_agreement"])
    assert len(kept) == 1 and len(kept[0][2]) == 1
