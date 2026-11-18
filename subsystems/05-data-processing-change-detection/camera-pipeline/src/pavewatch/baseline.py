"""A small OpenCV baseline for the same two visual classes."""

from collections.abc import Sequence

import cv2
import numpy as np

from .images import Rgb, Scores


def predict_tiles(tiles: Sequence[Rgb]) -> Scores:
    predictions = []
    contrast = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    crack_kernels = [
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size)) for size in (5, 9, 17)
    ]
    coarse_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    for tile in tiles:
        gray = contrast.apply(cv2.cvtColor(tile, cv2.COLOR_RGB2GRAY))
        smoothed = cv2.medianBlur(gray, 3)
        crack = np.maximum.reduce(
            [cv2.morphologyEx(smoothed, cv2.MORPH_BLACKHAT, kernel) for kernel in crack_kernels]
        )
        nearby = cv2.GaussianBlur(gray, (0, 0), 14)
        surface = cv2.GaussianBlur(gray, (0, 0), 4)
        depression = cv2.morphologyEx(cv2.subtract(nearby, surface), cv2.MORPH_CLOSE, coarse_close)
        predictions.append(np.clip(np.stack((crack / 80.0, depression / 45.0)), 0, 1))
    return np.asarray(predictions, dtype=np.float32)
