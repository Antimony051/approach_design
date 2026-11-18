"""Translate a pinned validation photograph and its two separated annotated potholes."""

import argparse
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
from PIL import Image

from pavewatch.artifacts import sha256, write_json
from pavewatch.datasets import load_manifest

SOURCE = "cracks_potholes_v4/1051753_DF_020_020BDF0070_01649"


def build(output):
    if output.exists():
        raise ValueError("Choose a new fixture directory")
    sample = next(r for r in load_manifest(Path("data/camera-v0/manifest.json")) if r.id == SOURCE)
    if (
        sha256(sample.image) != sample.image_sha256
        or sha256(sample.masks[1]) != sample.mask_sha256[1]
    ):
        raise ValueError("Photographic source or mask hash mismatch")
    rgb, labels = sample.load()
    boxes = cv2.connectedComponentsWithStats(labels[1].astype("uint8"), connectivity=8)[2][1:]
    if len(boxes) != 2 or labels[0].any():
        raise ValueError("Unexpected annotation in pinned validation image")
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as tmp:
        work = Path(tmp) / "pass"
        work.mkdir()
        session = {
            "schema_version": 1,
            "pass_id": "photo-DF020",
            "site_id": sample.group,
            "capture_profile": "Translated 930 x 578 crops of one public 1024 x 630 road photograph",
            "timestamp_unit": "ns",
            "clock_basis": "synthetic_exposure_clock",
            "nominal_fps": 5,
            "measured_path_m": None,
            "source_id": SOURCE,
            "source_sha256": sample.image_sha256,
            "frames": [],
        }
        objects = [
            {"id": f"pothole-{i}", "class_name": "pothole_like", "views": {}}
            for i in range(len(boxes))
        ]
        for i in range(9):
            x, y = 8 + 7 * i, 20 + 2 * i
            name = f"frame-{i:03}"
            file = work / (name + ".jpg")
            Image.fromarray(rgb[y : y + 578, x : x + 930]).save(file, quality=95)
            session["frames"].append(
                {
                    "id": name,
                    "path": file.name,
                    "timestamp": 200000000 * i,
                    "width": 930,
                    "height": 578,
                    "sha256": sha256(file),
                    "exif_orientation": 1,
                }
            )
            for obj, (u, v, w, h, _) in zip(objects, boxes, strict=True):
                obj["views"][name] = [int(u - x), int(v - y), int(u + w - x), int(v + h - y)]
        write_json(work / "session.json", session)
        write_json(
            work / "labels.json",
            {
                "schema_version": 1,
                "pass_id": session["pass_id"],
                "site_id": sample.group,
                "objects": objects,
                "nuisances": [],
            },
        )
        os.rename(work, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build(parser.parse_args().output)
