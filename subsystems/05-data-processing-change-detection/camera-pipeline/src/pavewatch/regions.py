"""Aggregate a class score map into spatially supported image evidence."""

from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray

from .images import Mask, Scores


@dataclass(frozen=True)
class RegionSettings:
    seed: float
    min_area: int
    decision: float = 0.5
    min_fill: float = 0.0

    def __post_init__(self) -> None:
        if not 0 < self.seed <= 1 or not 0 < self.decision <= 1:
            raise ValueError("Seed and decision thresholds must be in (0, 1]")
        if self.min_area < 1 or not 0 <= self.min_fill <= 1:
            raise ValueError("Invalid component area or bounding-box fill rule")


@dataclass(frozen=True)
class Components:
    labels: NDArray[np.int32]
    areas: NDArray[np.int32]
    means: NDArray[np.float64]
    fill: NDArray[np.float64]
    boxes: NDArray[np.int32]

    def supported(self, min_area: int, min_fill: float) -> Mask:
        keep = (self.areas >= min_area) & (self.fill >= min_fill)
        keep[0] = False
        return keep


def components(scores: Scores, seed: float) -> Components:
    binary = np.ascontiguousarray(scores >= seed, dtype=np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    area = stats[:, cv2.CC_STAT_AREA]
    area_sum = np.bincount(labels.ravel(), weights=scores.ravel(), minlength=count)
    means = area_sum / np.maximum(area, 1)
    boxes = stats[:, cv2.CC_STAT_WIDTH].astype(np.float64) * stats[:, cv2.CC_STAT_HEIGHT]
    fill = area / np.maximum(boxes, 1)
    return Components(labels, area, means, fill, stats)


def image_evidence(scores: Scores, settings: RegionSettings) -> tuple[float, Mask]:
    regions = components(scores, settings.seed)
    keep = regions.supported(settings.min_area, settings.min_fill)
    score = float(regions.means[keep].max(initial=0.0))
    return score, keep[regions.labels]
