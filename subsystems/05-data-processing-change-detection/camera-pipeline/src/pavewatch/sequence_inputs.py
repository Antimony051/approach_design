"""Verified pass metadata and bounded image access, in EXIF-upright coordinates."""

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import cv2
from PIL import Image

from .artifacts import sha256
from .images import read_rgb


@dataclass(frozen=True)
class Frame:
    index: int
    id: str
    path: Path
    digest: str
    time: int
    segment: int
    width: int
    height: int


@lru_cache(maxsize=2)
def pixels(frame: Frame):
    return read_rgb(frame.path)


def crop_quality(rgb):
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    return (
        float(cv2.Laplacian(gray, cv2.CV_32F).var()),
        float(((gray <= 3) | (gray >= 252)).mean()),
    )


def number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"Expected positive finite {name}")
    return value


def read_session(path: Path, gap_factor: float) -> tuple[dict, list[Frame], list[dict]]:
    doc = json.loads(path.read_text())
    units = {"ns": 1, "us": 1000, "ms": 1000000}
    if (
        doc["schema_version"] != 1
        or doc["timestamp_unit"] not in units
        or not doc["clock_basis"]
        or not doc["pass_id"]
        or not doc["capture_profile"]
    ):
        raise ValueError("Invalid session identity, timestamp unit, clock basis or profile")
    period = 1e9 / number(doc["nominal_fps"], "nominal_fps")
    if doc.get("measured_path_m") is not None:
        number(doc["measured_path_m"], "measured_path_m")
    frames, events, seen, hashes, paths = [], [], set(), set(), set()
    segment, previous, broken, last_size = -1, None, True, None
    for row in doc["frames"]:
        name, timestamp = row["id"], row["timestamp"]
        if (
            not isinstance(name, str)
            or not name
            or name in seen
            or type(timestamp) is not int
            or timestamp < 0
        ):
            raise ValueError(f"Invalid/duplicate frame ID or native timestamp: {name}")
        seen.add(name)
        tick = timestamp * units[doc["timestamp_unit"]]
        if previous is not None and tick <= previous:
            raise ValueError(f"Duplicate or out-of-order exposure: {name}")
        gap = previous is not None and tick - previous > gap_factor * period
        if gap:
            events.append(
                {"frame": name, "reason": "timestamp_gap", "interval_ns": tick - previous}
            )
        previous = tick
        if row.get("missing", False):
            events.append({"frame": name, "reason": "missing"})
            broken = True
            continue
        original = (path.parent / row["path"]).resolve()
        if not original.is_file():
            raise ValueError(f"Missing original for {name}; declare missing exposures explicitly")
        digest = sha256(original)
        if original in paths or digest in hashes or digest != row["sha256"]:
            raise ValueError(f"Duplicate original or SHA-256 mismatch: {name}")
        paths.add(original)
        hashes.add(digest)
        with Image.open(original) as im:
            orientation = im.getexif().get(274, 1)
            if orientation != row["exif_orientation"] or orientation not in range(1, 9):
                raise ValueError(f"EXIF orientation mismatch: {name}")
        w, h = row["width"], row["height"]
        if type(w) is not int or type(h) is not int or min(w, h) < 1:
            raise ValueError(f"Invalid upright size: {name}")
        if last_size and last_size != (w, h, orientation):
            events.append({"frame": name, "reason": "geometry_change"})
            broken = True
        if broken or gap or row.get("discontinuity", False):
            segment += 1
        frame = Frame(len(frames), name, original, digest, tick, segment, w, h)
        if pixels(frame).shape[:2] != (h, w):
            raise ValueError(f"Decoded dimensions mismatch: {name}")
        frames.append(frame)
        broken, last_size = False, (w, h, orientation)
    if not frames:
        raise ValueError("No available exposures in this session")
    return doc, frames, events


def grid_frames(frames, interval):
    chosen, starts = {}, {}
    for frame in frames:
        start = starts.setdefault(frame.segment, frame.time)
        slot = frame.segment, int((frame.time - start) // (interval * 1e9))
        small = cv2.resize(pixels(frame), (320, 180), interpolation=cv2.INTER_AREA)
        sharp, clipped = crop_quality(small)
        quality = (sharp * (1 - clipped), -frame.index)
        if slot not in chosen or quality > chosen[slot][0]:
            chosen[slot] = quality, frame.index
    return {v[1] for v in chosen.values()}
