"""Image decoding, bounded tiling, and mapping back to image coordinates."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageOps

Rgb = NDArray[np.uint8]
Mask = NDArray[np.bool_]
Scores = NDArray[np.float32]
TilePredictor = Callable[[Sequence[Rgb]], Scores]


@dataclass(frozen=True)
class ImageSettings:
    tile_size: int = 320
    overlap: int = 64
    max_side: int = 960

    def __post_init__(self) -> None:
        if self.tile_size < 64 or not 0 <= self.overlap < self.tile_size:
            raise ValueError(
                "Expected a tile size of at least 64 and overlap smaller than the tile"
            )
        if self.max_side < self.tile_size:
            raise ValueError("The maximum image side must be at least the tile size")


def read_rgb(path: Path) -> Rgb:
    try:
        with Image.open(path) as image:
            if image.format not in {"JPEG", "PNG"}:
                raise ValueError(f"Expected a JPEG or PNG image: {path}")
            return np.array(ImageOps.exif_transpose(image).convert("RGB"), dtype=np.uint8)
    except (OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise ValueError(f"Cannot read image {path}: {error}") from error


def read_mask(path: Path, shape: tuple[int, int]) -> Mask:
    try:
        with Image.open(path) as image:
            values = np.asarray(image.convert("L"), dtype=np.uint8)
    except (OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise ValueError(f"Cannot read mask {path}: {error}") from error
    if values.shape != shape:
        raise ValueError(f"Mask {path} has shape {values.shape}, expected {shape}")
    return values >= 128


def scaled_image(image: Rgb, settings: ImageSettings) -> Rgb:
    height, width = image.shape[:2]
    scale = min(1.0, settings.max_side / max(height, width))
    if scale == 1.0:
        return image
    size = max(1, round(width * scale)), max(1, round(height * scale))
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def resized_mask(mask: Mask, shape: tuple[int, int]) -> Mask:
    if mask.shape == shape:
        return mask
    height, width = shape
    return cv2.resize(mask.astype(np.uint8), (width, height), interpolation=cv2.INTER_NEAREST) > 0


def _tile_origins(length: int, size: int, overlap: int) -> list[int]:
    last = length - size
    origins = list(range(0, last + 1, size - overlap))
    if origins[-1] != last:
        origins.append(last)
    return origins


def tiled_scores(
    image: Rgb, settings: ImageSettings, predict_tiles: TilePredictor, batch_size: int = 8
) -> Scores:
    if batch_size < 1:
        raise ValueError("Tile batch size must be positive")
    size = settings.tile_size
    height, width = image.shape[:2]
    padded = cv2.copyMakeBorder(
        image, 0, max(0, size - height), 0, max(0, size - width), cv2.BORDER_REPLICATE
    )
    padded_height, padded_width = padded.shape[:2]
    origins = list(
        product(
            _tile_origins(padded_height, size, settings.overlap),
            _tile_origins(padded_width, size, settings.overlap),
        )
    )
    taper = np.maximum(np.hanning(size).astype(np.float32), 0.2)
    blend = np.outer(taper, taper)
    total = np.zeros((2, padded_height, padded_width), dtype=np.float32)
    weight = np.zeros((padded_height, padded_width), dtype=np.float32)
    for start in range(0, len(origins), batch_size):
        positions = origins[start : start + batch_size]
        tiles = [padded[y : y + size, x : x + size] for y, x in positions]
        maps = predict_tiles(tiles)
        if maps.shape != (len(tiles), 2, size, size):
            raise ValueError(f"Detector returned an unexpected tile score shape: {maps.shape}")
        for (y, x), scores in zip(positions, maps, strict=True):
            total[:, y : y + size, x : x + size] += scores * blend
            weight[y : y + size, x : x + size] += blend
    return (total / weight)[:, :height, :width]


def overlay(image: Rgb, masks: Sequence[Mask]) -> Rgb:
    shaded = image.copy()
    for mask, color in zip(masks, ((255, 85, 40), (35, 205, 255)), strict=True):
        region = resized_mask(mask, image.shape[:2])
        shaded[region] = (0.48 * shaded[region] + 0.52 * np.array(color)).astype(np.uint8)
    return shaded
