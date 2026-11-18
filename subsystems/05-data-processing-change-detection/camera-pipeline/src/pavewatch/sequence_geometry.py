"""Direct, candidate-local registration between EXIF-upright source images."""

from functools import lru_cache

import cv2
import numpy as np

from .sequence_inputs import pixels


def quad(box):
    x, y, X, Y = box
    return np.float32([[x, y], [X, y], [X, Y], [x, Y]])


def warp(points, H):
    return cv2.perspectiveTransform(np.float32(points).reshape(-1, 1, 2), H).reshape(-1, 2)


def bounds(points):
    lo, hi = points.min(axis=0), points.max(axis=0)
    return [float(lo[0]), float(lo[1]), float(hi[0]), float(hi[1])]


def intersection(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def area(a):
    return max(0, a[2] - a[0]) * max(0, a[3] - a[1])


def iou(a, b):
    both = intersection(a, b)
    return both / max(1, area(a) + area(b) - both)


@lru_cache(maxsize=24)
def features(frame):
    gray = cv2.cvtColor(pixels(frame), cv2.COLOR_RGB2GRAY)
    scale = min(1, 960 / max(gray.shape))
    gray = cv2.resize(
        gray,
        (round(frame.width * scale), round(frame.height * scale)),
        interpolation=cv2.INTER_AREA,
    )
    keys, desc = cv2.ORB_create(nfeatures=2200).detectAndCompute(gray, None)
    points = np.float32([k.pt for k in keys]).reshape(-1, 2)
    points *= [frame.width / gray.shape[1], frame.height / gray.shape[0]]
    return points, desc


@lru_cache(maxsize=64)
def pairs(first, second):
    a, da = features(first)
    b, db = features(second)
    if da is None or db is None or min(len(da), len(db)) < 2:
        return a[:0], b[:0]
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)

    def good(x, y):
        return {
            p.queryIdx: p.trainIdx
            for p, q in matcher.knnMatch(x, y, k=2)
            if p.distance < 0.76 * q.distance
        }

    ab, ba = good(da, db), good(db, da)
    ij = [(i, j) for i, j in ab.items() if ba.get(j) == i]
    return a[[i for i, j in ij]], b[[j for i, j in ij]]


def register(first, second, box, cfg):
    quality = {"from": first.id, "to": second.id}

    def reject(reason):
        return None, dict(quality, accepted=False, reason=reason)

    if first.segment != second.segment:
        return reject("discontinuity")
    a, b = pairs(first, second)
    x, y, X, Y = box
    center = np.float32([(x + X) / 2, (y + Y) / 2])
    margin = max(first.width * cfg["registration_radius_fraction"], (X - x) / 2, (Y - y) / 2)
    local = (np.abs(a - center) <= [margin + (X - x) / 2, margin + (Y - y) / 2]).all(axis=1)
    inside = (a[:, 0] > x) & (a[:, 0] < X) & (a[:, 1] > y) & (a[:, 1] < Y)
    use = local & ~inside
    a, b = a[use], b[use]
    minimum = cfg["min_inliers"]
    if len(a) < minimum:
        return reject("too_few_surrounding_matches")
    tolerance = cfg["max_residual_at_960"] * max(1, second.width / 960)
    H, mask = cv2.findHomography(a, b, cv2.RANSAC, tolerance, maxIters=1500, confidence=0.995)
    if H is None or mask is None or not np.isfinite(H).all():
        return reject("fit_failed")
    keep = mask.ravel().astype(bool)
    quality.update(inliers=int(keep.sum()), inlier_fraction=float(keep.mean()))
    if keep.sum() < minimum or keep.mean() < cfg["min_inlier_fraction"]:
        return reject("insufficient_inliers")
    hull = cv2.convexHull(a[keep])
    support = cv2.contourArea(hull) / max(1, margin * margin)
    residual = np.linalg.norm(warp(a[keep], H) - b[keep], axis=1)
    quality.update(spread=float(support), p90_residual_px=float(np.percentile(residual, 90)))
    if (
        support < cfg["min_spread"]
        or cv2.pointPolygonTest(hull, tuple(map(float, center)), True) < -margin * 0.15
        or quality["p90_residual_px"] > tolerance
    ):
        return reject("poor_local_support")
    corners = quad(box)
    mapped = warp(corners, H)
    ratios = np.linalg.norm(mapped - np.roll(mapped, 1, axis=0), axis=1) / np.maximum(
        1, np.linalg.norm(corners - np.roll(corners, 1, axis=0), axis=1)
    )
    if (
        not np.isfinite(mapped).all()
        or not cv2.isContourConvex(mapped)
        or cv2.contourArea(mapped, oriented=True) <= 0
        or min(ratios) < 0.65
        or max(ratios) > 1.5
    ):
        return reject("implausible_warp")
    clip = quad([0, 0, second.width, second.height])
    overlap = cv2.intersectConvexConvex(mapped, clip)[0] / max(1, cv2.contourArea(mapped))
    quality["valid_overlap"] = float(overlap)
    if overlap < cfg["min_valid_overlap"]:
        return reject("outside_view")
    quality.update(accepted=True, homography=H.tolist())
    return H, quality
