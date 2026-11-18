"""Per-component evidence from whole images, context crops and tiled detail."""

import base64
from dataclasses import dataclass, replace

import cv2
import numpy as np

from . import CLASSES
from .images import scaled_image, tiled_scores
from .regions import components
from .sequence_geometry import bounds, intersection, iou, quad, warp
from .sequence_inputs import pixels


@dataclass
class Region:
    frame: int
    channel: int
    box: list
    mask: np.ndarray
    score: float
    sources: tuple
    crop: list
    scale: list

    def evidence(self, frames):
        f = frames[self.frame]
        return {
            "frame_id": f.id,
            "frame_sha256": f.digest,
            "source": str(f.path),
            "timestamp_ns": f.time,
            "class_name": CLASSES[self.channel],
            "box": self.box,
            "score": self.score,
            "sources": self.sources,
            "crop": self.crop,
            "model_px_per_source_px": self.scale,
            "mask_png": base64.b64encode(cv2.imencode(".png", self.mask)[1]).decode(),
        }


def raster(region, target, size, H=None):
    x, y, X, Y = region.box
    w, h = size
    a, b, A, B = target

    def affine(sx, sy, tx, ty):
        return np.array([[sx, 0, tx], [0, sy, ty], [0, 0, 1]], dtype=float)

    source = affine((X - x) / region.mask.shape[1], (Y - y) / region.mask.shape[0], x, y)
    dest = affine(w / (A - a), h / (B - b), -a * w / (A - a), -b * h / (B - b))
    matrix = dest @ (np.eye(3) if H is None else H) @ source
    return cv2.warpPerspective(region.mask, matrix, (w, h), flags=cv2.INTER_NEAREST)


def canvas(box):
    w, h = box[2] - box[0], box[3] - box[1]
    scale = min(1, 400 / max(w, h))
    return max(1, round(w * scale)), max(1, round(h * scale))


def agreement(a, b, H=None):
    mapped = bounds(warp(quad(a.box), H)) if H is not None else a.box
    if not intersection(mapped, b.box):
        return 0.0
    union = [
        min(mapped[0], b.box[0]),
        min(mapped[1], b.box[1]),
        max(mapped[2], b.box[2]),
        max(mapped[3], b.box[3]),
    ]
    size = canvas(union)
    left = raster(a, union, size, H) > 0
    right = raster(b, union, size) > 0
    # Permit small rasterization or registration error for thin cracks.
    kernel = np.ones((3, 3), np.uint8)
    shared = min(
        np.count_nonzero(left & (cv2.dilate(right.astype(np.uint8), kernel) > 0)),
        np.count_nonzero(right & (cv2.dilate(left.astype(np.uint8), kernel) > 0)),
    )
    return (
        float(shared / max(1, min(left.sum(), right.sum()))) if iou(mapped, b.box) >= 0.08 else 0.0
    )


def combine(a, b):
    box = [
        min(a.box[0], b.box[0]),
        min(a.box[1], b.box[1]),
        max(a.box[2], b.box[2]),
        max(a.box[3], b.box[3]),
    ]
    size = canvas(box)
    return replace(
        max((a, b), key=lambda r: r.score),
        box=box,
        mask=raster(a, box, size) | raster(b, box, size),
        sources=tuple(sorted(set(a.sources + b.sources))),
    )


def merge(regions, minimum):
    result = []
    for item in sorted(regions, key=lambda r: -r.score):
        hits = [
            i
            for i, r in enumerate(result)
            if r.channel == item.channel and agreement(item, r) >= minimum
        ]
        for i in reversed(hits):
            item = combine(item, result.pop(i))
        result.append(item)
    return result


def context(box, frame, fraction):
    side = max(
        64, round(frame.width * fraction), round(1.6 * max(box[2] - box[0], box[3] - box[1]))
    )
    w, h = min(side, frame.width), min(side, frame.height)
    x = int(np.clip((box[0] + box[2] - w) / 2, 0, frame.width - w))
    y = int(np.clip((box[1] + box[3] - h) / 2, 0, frame.height - h))
    return [x, y, x + w, y + h]


def scan(frame, box, mode, model, cfg):
    x, y, X, Y = box
    rgb = pixels(frame)[y:Y, x:X]
    if mode in ("grid", "context"):
        # Letterbox preserves rim shape when a context window fits only on one axis.
        size = model.image.tile_size
        scale = size / max(rgb.shape[:2])
        w, h = max(1, round((X - x) * scale)), max(1, round((Y - y) * scale))
        small = cv2.resize(
            rgb, (w, h), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
        )
        padded = cv2.copyMakeBorder(small, 0, size - h, 0, size - w, cv2.BORDER_REPLICATE)
        maps = model.predictor([padded])[0, :, :h, :w]
    else:
        small = scaled_image(rgb, model.image)
        maps = tiled_scores(small, model.image, model.predictor)
    h, w = maps.shape[1:]
    sx, sy = w / (X - x), h / (Y - y)
    regions = []
    for channel, (scores, rule) in enumerate(zip(maps, model.region_rules, strict=True)):
        stats = components(scores, rule.seed)
        keep = stats.supported(rule.min_area, rule.min_fill) & (
            stats.means >= cfg["proposal_scores"][channel]
        )
        boxes = stats.boxes
        for idx in np.flatnonzero(keep):
            u, v, dw, dh, _ = boxes[idx]
            mask = np.uint8(stats.labels[v : v + dh, u : u + dw] == idx) * 255
            region = [
                int(x + np.floor(u / sx)),
                int(y + np.floor(v / sy)),
                min(X, int(x + np.ceil((u + dw) / sx))),
                min(Y, int(y + np.ceil((v + dh) / sy))),
            ]
            regions.append(
                Region(
                    frame.index,
                    channel,
                    region,
                    mask,
                    float(stats.means[idx]),
                    (mode,),
                    box,
                    [sx, sy],
                )
            )
    return regions


def grid(frame, fraction, overlap):
    side = max(64, round(frame.width * fraction))
    w, h = min(side, frame.width), min(side, frame.height)

    def origins(length, size):
        return sorted(
            {*range(0, length - size + 1, max(1, round(size * (1 - overlap)))), length - size}
        )

    for y in origins(frame.height, h):
        for x in origins(frame.width, w):
            yield [x, y, x + w, y + h]


def crop_scan(frame, box, model, cfg):
    region = context(box, frame, cfg["crop_width_fraction"])
    return merge(
        scan(frame, region, "context", model, cfg) + scan(frame, region, "detail", model, cfg),
        cfg["merge_agreement"],
    )
