"""Pass-local association and evidence fusion. Each vote is from a distinct exposure."""

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import NamedTuple

import cv2
import numpy as np

from . import CLASSES
from .sequence_geometry import bounds, quad, register, warp
from .sequence_inputs import crop_quality, pixels
from .sequence_regions import Region, agreement, canvas, context, crop_scan, raster


@dataclass
class Track:
    sightings: list
    edges: list


class Decision(NamedTuple):
    anchor: Region
    views: list
    used: list
    box: list
    stitched: np.ndarray
    score: float
    reason: str


def collate(proposals, frames, cfg, period):
    tracks, active = [], []
    rejected = Counter()
    for f, regions in zip(frames, proposals, strict=True):
        active = [
            t
            for t in active
            if frames[t.sightings[-1].frame].segment == f.segment
            and f.time - frames[t.sightings[-1].frame].time <= cfg["window_intervals"] * period
        ]
        edges = []
        for j, track in enumerate(active):
            ref = track.sightings[-1]
            if not any(r.channel == ref.channel for r in regions):
                continue
            H, q = register(frames[ref.frame], f, ref.box, cfg)
            if H is None:
                rejected[q["reason"]] += 1
                continue
            for k, r in enumerate(regions):
                if ref.channel == r.channel:
                    overlap = agreement(ref, r, H)
                    if overlap >= cfg["link_agreement"]:
                        edges.append((overlap, j, k, q))
        used_tracks, used_rows = set(), set()
        for overlap, j, k, q in sorted(edges, key=lambda e: (-e[0], e[1], e[2])):
            if j in used_tracks or k in used_rows:
                continue
            active[j].sightings.append(regions[k])
            active[j].edges.append(dict(q, mask_agreement=overlap))
            used_tracks.add(j)
            used_rows.add(k)
        for k, r in enumerate(regions):
            if k not in used_rows:
                track = Track([r], [])
                active.append(track)
                tracks.append(track)
    return tracks, rejected


def quality(f, box, cfg):
    return cached_quality(f, tuple(context(box, f, cfg["crop_width_fraction"])))


@lru_cache(maxsize=4096)
def cached_quality(f, crop):
    x, y, X, Y = crop
    return crop_quality(pixels(f)[y:Y, x:X])


def acceptable(sharp, clipped, cfg):
    return sharp >= cfg["min_crop_sharpness"] and clipped <= cfg["max_clipped"]


def multiview(track, frames, period, model, cfg, rejected):
    qualities = [quality(frames[r.frame], r.box, cfg) for r in track.sightings]
    anchor_index = max(
        range(len(qualities)),
        key=lambda i: (acceptable(*qualities[i], cfg), track.sightings[i].score, qualities[i][0]),
    )
    anchor = track.sightings[anchor_index]
    ref = frames[anchor.frame]
    # An initial proposal may be weak, yet still identifies a place to inspect.
    views = [
        (
            anchor,
            np.eye(3),
            {"from_frame": ref.id, "to_frame": ref.id, "anchor": True},
            qualities[anchor_index],
        )
    ]
    options = []
    for k in range(
        max(0, ref.index - cfg["window_intervals"]),
        min(len(frames), ref.index + cfg["window_intervals"] + 1),
    ):
        f = frames[k]
        delta = abs(f.time - ref.time)
        if (
            f.segment != ref.segment
            or not cfg["separation_intervals"] * period <= delta <= cfg["window_intervals"] * period
        ):
            continue
        H, q = register(ref, f, anchor.box, cfg)
        if H is None:
            rejected[q["reason"]] += 1
            continue
        target = bounds(warp(quad(anchor.box), H))
        sharp, clipped = quality(f, target, cfg)
        if not acceptable(sharp, clipped, cfg):
            rejected["crop_blurry_or_clipped"] += 1
            continue
        options.append((sharp * (1 - clipped), k, target, H, q, (sharp, clipped)))
    selected_times = [ref.time]
    for _, k, target, H, q, qual in sorted(options, key=lambda v: (-v[0], v[1])):
        f = frames[k]
        if any(abs(t - f.time) < cfg["separation_intervals"] * period for t in selected_times):
            continue
        selected_times.append(f.time)
        matches = []
        for r in crop_scan(f, target, model, cfg):
            if r.channel == anchor.channel:
                similarity = agreement(anchor, r, H)
                if similarity >= cfg["link_agreement"]:
                    matches.append((r, similarity))
        if matches:
            r, sim = max(matches, key=lambda item: item[0].score)
            views.append((r, H, dict(q, mask_agreement=sim), qual))
        else:
            rejected["no_aligned_crop_region"] += 1
        if len(selected_times) >= cfg["max_views"]:
            break
    eligible = [v for v in views if acceptable(*v[3], cfg)]
    ranked = sorted(eligible, key=lambda v: -v[0].score)
    strong = bool(ranked and ranked[0][0].score >= cfg["strong_scores"][anchor.channel])
    agreeing = [v for v in ranked if v[0].score >= cfg["weak_scores"][anchor.channel]]
    if len(agreeing) < 2 and not strong:
        return None
    used = agreeing if len(agreeing) >= 2 else [ranked[0]]
    # Store the union of aligned masks in the anchor frame for one spatial finding.
    outlines = [warp(quad(r.box), np.linalg.inv(H)) for r, H, q, qual in used]
    box = bounds(np.concatenate(outlines))
    box = [
        max(0, int(np.floor(box[0]))),
        max(0, int(np.floor(box[1]))),
        min(ref.width, int(np.ceil(box[2]))),
        min(ref.height, int(np.ceil(box[3]))),
    ]
    size = canvas(box)
    stitched = np.zeros(size[::-1], np.uint8)
    for r, H, q, qual in used:
        stitched |= raster(r, box, size, np.linalg.inv(H))
    score = float(np.mean([v[0].score for v in used[:2]]))
    return Decision(
        anchor,
        views,
        used,
        box,
        stitched,
        score,
        ("aligned_views" if len(used) > 1 else "strong_single"),
    )


def consolidate(decisions, minimum):
    """Re-inspection can rediscover a region already accepted in the same exposure."""
    occupied = defaultdict(list)
    kept = []
    for track, result in sorted(decisions, key=lambda pair: (-len(pair[1].used), -pair[1].score)):
        best_overlap, owner = 0.0, None
        for r, H, q, qual in result.used:
            for other, index in occupied[r.frame, r.channel]:
                overlap = agreement(r, other)
                if overlap >= minimum and overlap > best_overlap:
                    best_overlap, owner = overlap, index
        if owner is None:
            owner = len(kept)
            kept.append((track, result, []))
        else:
            kept[owner][2].append((track, result, best_overlap))
        for r, H, q, qual in result.used:
            occupied[r.frame, r.channel].append((r, owner))
    return kept


def identifier(pass_id, mode, anchor, frames):
    material = f"{pass_id}/{mode}/{frames[anchor.frame].id}/{anchor.channel}/{anchor.box}"
    return hashlib.sha256(material.encode()).hexdigest()[:20]


def save_finding(
    folder, mode, session, frames, track, anchor, views, used, box, mask, score, reason
):
    import base64

    from PIL import Image

    fid = identifier(session["pass_id"], mode, anchor, frames)
    chosen = {v[0].frame for v in used}
    evidence = [
        dict(
            r.evidence(frames),
            registration=q,
            crop_sharpness=qual[0],
            clipped_fraction=qual[1],
            used_for_decision=r.frame in chosen,
        )
        for r, H, q, qual in views
    ]
    best = max(used, key=lambda v: v[0].score)[0]
    f = frames[best.frame]
    rgb = pixels(f)
    x, y, X, Y = context(best.box, f, 0.35)
    local = rgb[y:Y, x:X].copy()
    actual = raster(best, [x, y, X, Y], (X - x, Y - y)) > 0
    color = (255, 85, 40) if best.channel == 0 else (35, 205, 255)
    local[actual] = (0.5 * local[actual] + 0.5 * np.array(color)).astype(np.uint8)
    path = folder / mode / (fid + ".jpg")
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(local)
    im.thumbnail((800, 800))
    im.save(path, quality=88)
    return {
        "id": fid,
        "pass_id": session["pass_id"],
        "class_name": CLASSES[anchor.channel],
        "score": score,
        "decision": reason,
        "reference_frame": frames[anchor.frame].id,
        "reference_box": box,
        "reference_mask_png": base64.b64encode(cv2.imencode(".png", mask)[1]).decode(),
        "best_overlay": str(path.relative_to(folder)),
        "overlay_frame": f.id,
        "overlay_crop": [x, y, X, Y],
        "sightings": [
            {"frame_id": frames[r.frame].id, "box": r.box, "score": r.score}
            for r in track.sightings
        ],
        "track_registration": track.edges,
        "evidence": evidence,
    }
