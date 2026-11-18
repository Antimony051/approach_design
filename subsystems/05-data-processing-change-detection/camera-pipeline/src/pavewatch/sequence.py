"""Replay frozen A/B/C camera variants without writing into a capture session."""

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
import torch

from .artifacts import sha256, write_json
from .prediction import open_inference, read_bundle
from .sequence_eval import evaluate, markdown, validate_labels
from .sequence_geometry import features, pairs
from .sequence_inputs import grid_frames, pixels, read_session
from .sequence_regions import agreement, context, crop_scan, grid, merge, scan
from .sequence_tracks import collate, consolidate, multiview, quality, save_finding


def checked_config(path):
    c = json.loads(path.read_text())
    if c["schema_version"] != 1 or not (
        2 <= c["max_views"] <= 3 and 0 < c["separation_intervals"] <= c["window_intervals"] <= 20
    ):
        raise ValueError("Invalid view window")
    for key in (
        "crop_width_fraction",
        "min_inlier_fraction",
        "min_valid_overlap",
        "merge_agreement",
        "link_agreement",
        "evaluation_box_iou",
    ):
        if not 0 < c[key] <= 1:
            raise ValueError(f"Invalid {key}")
    if not (
        0 <= c["grid_overlap"] < 1
        and c["grid_interval_s"] > 0
        and c["gap_factor"] > 1
        and c["registration_radius_fraction"] > 0
        and c["min_inliers"] >= 4
        and c["max_residual_at_960"] > 0
    ):
        raise ValueError("Invalid grid or registration settings")
    for p, w, s in zip(c["proposal_scores"], c["weak_scores"], c["strong_scores"], strict=True):
        if not 0 < p <= w <= s <= 1:
            raise ValueError("Invalid evidence thresholds")
    if len(c["weak_scores"]) != 2:
        raise ValueError("Expect two channel thresholds")
    return c


def candidates(frames, model, cfg):
    start = time.perf_counter()
    whole = [scan(f, [0, 0, f.width, f.height], "whole", model, cfg) for f in frames]
    whole_seconds = time.perf_counter() - start
    selected = grid_frames(frames, cfg["grid_interval_s"])
    expanded = []
    for f, first in zip(frames, whole, strict=True):
        seeds = list(first)
        if f.index in selected:
            for box in grid(f, cfg["crop_width_fraction"], cfg["grid_overlap"]):
                seeds.extend(scan(f, box, "grid", model, cfg))
        seeds = merge(seeds, cfg["merge_agreement"])
        evidence = list(seeds)
        # Overlapping proposals may request the same clipped context.
        crops = {}
        for seed in seeds:
            key = tuple(context(seed.box, f, cfg["crop_width_fraction"]))
            if key not in crops:
                crops[key] = crop_scan(f, seed.box, model, cfg)
            evidence.extend(
                r
                for r in crops[key]
                if r.channel == seed.channel and agreement(seed, r) >= cfg["link_agreement"]
            )
        expanded.append(merge(evidence, cfg["merge_agreement"]))
    return whole, expanded, selected, whole_seconds, time.perf_counter() - start


def replay(
    manifest: Path,
    config: Path,
    model_dir: Path,
    device: str,
    output: Path,
    labels: Path | None = None,
) -> dict:
    if output.exists():
        raise ValueError(f"Output already exists: {output}. Choose a fresh replay directory.")
    cfg = checked_config(config)
    model = open_inference(model_dir, device=device)
    if any(p > r.decision for p, r in zip(cfg["proposal_scores"], model.region_rules, strict=True)):
        raise ValueError("Proposal threshold would drop v0 detections")
    pixels.cache_clear()
    features.cache_clear()
    pairs.cache_clear()
    cv2.setRNGSeed(17)
    start = time.perf_counter()
    expected = sha256(manifest)
    session, frames, events = read_session(manifest, cfg["gap_factor"])
    period = 1e9 / session["nominal_fps"]
    validated = time.perf_counter() - start
    whole, expanded, selected, base_wall, extended_wall = candidates(frames, model, cfg)
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent, prefix=".sequence-") as tmp:
        folder = Path(tmp) / "result"
        folder.mkdir()
        report = {
            "schema_version": 1,
            "pass_id": session["pass_id"],
            "site_id": session["site_id"],
            "capture_profile": session["capture_profile"],
            "frames": len(frames),
            "events": events,
            "grid_frames": [frames[i].id for i in sorted(selected)],
            "manifest": str(manifest.resolve()),
            "manifest_sha256": expected,
            "config_sha256": sha256(config),
            "config": cfg,
            "model_version": model.version,
            "weights_sha256": read_bundle(model_dir)["weights_sha256"],
            "coordinates": "EXIF-upright source image pixels, xyxy half-open",
            "device": device,
            "torch_version": torch.__version__,
            "opencv_version": cv2.__version__,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "metrics": {},
            "modes": {},
        }
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
        )
        report["git_commit"] = commit.stdout.strip() if commit.returncode == 0 else None
        report["source_sha256"] = {
            p.name: sha256(p) for p in sorted(Path(__file__).parent.glob("*.py"))
        }
        annot = json.loads(labels.read_text()) if labels else None
        if annot is not None:
            validate_labels(annot, session, frames)
            report["annotations_sha256"] = sha256(labels)
        for mode in "ABC":
            features.cache_clear()
            pairs.cache_clear()
            pixels.cache_clear()
            t = time.perf_counter()
            proposals = whole if mode == "A" else expanded
            accepted = (
                proposals
                if mode == "C"
                else [
                    [r for r in row if r.score >= model.region_rules[r.channel].decision]
                    for row in proposals
                ]
            )
            tracks, rejected = collate(accepted, frames, cfg, period)
            findings = []
            decisions = []
            for track in tracks:
                if mode == "C":
                    result = multiview(track, frames, period, model, cfg, rejected)
                    if result is None:
                        continue
                    decisions.append((track, result))
                    continue
                else:
                    anchor = max(track.sightings, key=lambda r: r.score)
                    score, box, mask = anchor.score, anchor.box, anchor.mask
                    views = [
                        (
                            r,
                            None,
                            {"collated_for_evaluation": True},
                            quality(frames[r.frame], r.box, cfg),
                        )
                        for r in track.sightings
                    ]
                    used = views
                    reason = "single_frame_threshold"
                findings.append(
                    save_finding(
                        folder,
                        mode,
                        session,
                        frames,
                        track,
                        anchor,
                        views,
                        used,
                        box,
                        mask,
                        score,
                        reason,
                    )
                )
            for track, result, repeats in consolidate(decisions, cfg["merge_agreement"]):
                finding = save_finding(folder, mode, session, frames, track, *result)
                finding["merged_tracks"] = [
                    {
                        "agreement": overlap,
                        "decision": other.reason,
                        "sightings": [
                            {"frame_id": frames[r.frame].id, "box": r.box, "score": r.score}
                            for r in merged.sightings
                        ],
                        "evidence": [
                            dict(r.evidence(frames), registration=q) for r, H, q, qual in other.used
                        ],
                    }
                    for merged, other, overlap in repeats
                ]
                findings.append(finding)
            elapsed = (
                validated + (base_wall if mode == "A" else extended_wall) + time.perf_counter() - t
            )
            report["modes"][mode] = {
                "count": len(findings),
                "rejection_counts": dict(rejected),
                "seconds": elapsed,
                "seconds_per_100_frames": elapsed * 100 / len(frames),
            }
            write_json(
                folder / mode / "findings.json",
                {
                    "model_version": model.version,
                    "config_sha256": report["config_sha256"],
                    "pass_id": session["pass_id"],
                    "findings": findings,
                },
            )
            if annot is not None:
                report["metrics"][mode] = evaluate(
                    findings, proposals, tracks, frames, annot, session, cfg, elapsed
                )
        for name, rows in (("whole", whole), ("expanded", expanded)):
            write_json(
                folder / f"{name}-proposals.json",
                [
                    {"frame_id": f.id, "regions": [r.evidence(frames) for r in row]}
                    for f, row in zip(frames, rows, strict=True)
                ],
            )
        if sha256(manifest) != expected or any(sha256(f.path) != f.digest for f in frames):
            raise ValueError("Session changed during replay")
        write_json(folder / "report.json", report)
        (folder / "REPORT.md").write_text(markdown(report))
        os.rename(folder, output)
    return {
        "output": str(output),
        "frames": len(frames),
        "findings": {k: v["count"] for k, v in report["modes"].items()},
    }
