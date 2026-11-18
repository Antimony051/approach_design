"""Generate labeled, translated crops of deterministic large pavement-like stills."""

import argparse
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
import numpy as np
from PIL import Image

from pavewatch.artifacts import sha256, write_json


def build(output, control=False):
    if output.exists():
        raise ValueError(f"Fixture destination exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as tmp:
        work = Path(tmp) / "pass"
        work.mkdir()
        rng = np.random.default_rng(711 if control else 710)
        w, h = 1920, 1100
        grit = rng.normal(104, 15, (h, w))
        coarse = cv2.resize(
            rng.normal(0, 7, (35, 60)).astype("float32"), (w, h), interpolation=cv2.INTER_CUBIC
        )
        gray = np.uint8(np.clip(grit + coarse, 0, 255))
        for _ in range(9500):
            x, y = rng.integers([0, 0], [w, h])
            cv2.circle(
                gray, (int(x), int(y)), int(rng.integers(1, 4)), int(rng.integers(45, 170)), -1
            )
        # Keep truth independent of detector proposals and registration.
        trace = np.array(
            [
                (580, 530),
                (605, 548),
                (619, 536),
                (650, 558),
                (685, 552),
                (710, 571),
                (756, 564),
                (797, 580),
            ],
            np.int32,
        )
        cv2.polylines(gray, [trace], False, 31, 7, cv2.LINE_AA)
        objects = [("crack-1", "crack_like", [576, 526, 802, 585])]
        if not control:
            cv2.ellipse(gray, (1110, 365), (117, 67), -12, 0, 360, 55, -1, cv2.LINE_AA)
            cv2.ellipse(gray, (1110, 365), (110, 59), -12, 0, 360, 72, 8, cv2.LINE_AA)
            objects.append(("depression-1", "pothole_like", [994, 294, 1227, 437]))
        cv2.line(gray, (500, 820), (770, 790), 200, 18, cv2.LINE_AA)
        cv2.line(gray, (880, 610), (1200, 650), 65, 10, cv2.LINE_AA)
        nuisances = [
            ("paint-1", "paint", [488, 778, 783, 832]),
            ("repair-1", "sealed_joint", [873, 601, 1207, 659]),
        ]
        sheet = Image.fromarray(gray).convert("RGB")
        sheet.save(work / "source.png")
        pid = "translated-crack-control" if control else "translated-mixed"
        session = {
            "schema_version": 1,
            "site_id": pid,
            "pass_id": pid,
            "timestamp_unit": "ns",
            "clock_basis": "synthetic_exposure_clock",
            "nominal_fps": 5,
            "capture_profile": "Synthetic translated 1440 x 840 crops from a 1920 x 1100 still",
            "measured_path_m": None,
            "frames": [],
            "source_sha256": sha256(work / "source.png"),
        }
        truth = {
            "schema_version": 1,
            "pass_id": pid,
            "site_id": pid,
            "objects": [{"id": n, "class_name": k, "views": {}} for n, k, b in objects],
            "nuisances": [{"id": n, "kind": k, "views": {}} for n, k, b in nuisances],
        }
        transforms = {}
        for i in range(9):
            name = f"frame-{i:03}"
            t = i * 200000000
            if control and i == 7:
                session["frames"].append({"id": name, "timestamp": t, "missing": True})
                continue
            x, y = 72 + 31 * i, 88 + 2 * i
            frame = sheet.crop((x, y, x + 1440, y + 840))
            if i == 3:
                frame = Image.fromarray(cv2.GaussianBlur(np.array(frame), (9, 9), 2.0))
            file = work / (name + ".jpg")
            frame.save(file, quality=94)
            session["frames"].append(
                {
                    "id": name,
                    "timestamp": t,
                    "path": file.name,
                    "sha256": sha256(file),
                    "width": 1440,
                    "height": 840,
                    "exif_orientation": 1,
                    "exposure_us": None,
                    "gain": None,
                    "lens_position": None,
                }
            )
            transforms[name] = [x, y]
            for refs, items in ((objects, truth["objects"]), (nuisances, truth["nuisances"])):
                for (_, _, (a, b, A, B)), item in zip(refs, items, strict=True):
                    item["views"][name] = [a - x, b - y, A - x, B - y]
        write_json(work / "session.json", session)
        write_json(work / "labels.json", truth)
        write_json(work / "source-origins.json", transforms)
        os.rename(work, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    build(args.output, args.control)
