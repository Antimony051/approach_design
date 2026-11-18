"""Audit public camera datasets and persist a frozen, group-wise split."""

import json
import os
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from . import CLASSES
from .artifacts import sha256, write_json
from .images import Mask, Rgb, read_mask, read_rgb

DEEPCRACK = "deepcrack"
JOINT = "cracks_potholes_v4"
BACKGROUND = "pavedistress_v1"
JOINT_REVISION = "1f200541d2e88596fb9dcd91f4262c1ac5f6202e"
_SPLIT_PRIORITY = {"test": 0, "validation": 1, "train": 2}
_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
_SOURCES = {
    DEEPCRACK: {
        "url": "https://github.com/yhlleo/DeepCrack/tree/master/dataset",
        "terms": "Noncommercial research and education",
        "archive": "DeepCrack.zip",
    },
    JOINT: {
        "url": "https://data.mendeley.com/datasets/t576ydh9v8/4",
        "terms": "CC BY 4.0",
        "author_repository_revision": JOINT_REVISION,
        "archive": f"cracks-potholes-{JOINT_REVISION}.zip",
    },
    BACKGROUND: {
        "url": "https://data.mendeley.com/datasets/f46zt2g83x/1",
        "terms": "CC BY 4.0",
        "archive": "PaveDistress-v1.rar",
    },
}


@dataclass(frozen=True)
class Candidate:
    id: str
    source: str
    group: str
    split: str
    image: Path
    masks: tuple[Path | None, Path | None]
    kind: str = "annotated"


@dataclass(frozen=True)
class Sample(Candidate):
    labels: tuple[bool | None, bool | None] = (None, None)
    width: int = 0
    height: int = 0
    image_sha256: str = ""
    mask_sha256: tuple[str | None, str | None] = (None, None)
    phash: str = ""

    def load(self) -> tuple[Rgb, Mask]:
        image = read_rgb(self.image)
        if image.shape[:2] != (self.height, self.width):
            raise ValueError(f"Image dimensions changed after audit: {self.image}")
        masks = [
            read_mask(path, image.shape[:2]) if path else np.zeros(image.shape[:2], dtype=bool)
            for path in self.masks
        ]
        return image, np.stack(masks)


def _files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        raise ValueError(f"Required dataset directory is missing: {folder}")
    return sorted(
        p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in _IMAGE_SUFFIXES
    )


def _family(stem: str) -> str:
    return re.sub(r"-[0-9]+$", "", stem).casefold()


def _deepcrack(root: Path) -> list[Candidate]:
    training = _files(root / "train_img")
    test = _files(root / "test_img")
    test_families = {_family(path.stem) for path in test}
    train_families = sorted(
        {_family(path.stem) for path in training} - test_families,
        key=lambda group: (sum(1 for p in training if _family(p.stem) == group), group),
    )
    # Pick reproducible validation families across the range of family sizes.
    validation = set(train_families[2::5])
    rows = []
    for partition, paths in (("train", training), ("test", test)):
        for path in paths:
            family = _family(path.stem)
            split = "validation" if partition == "train" and family in validation else partition
            rows.append(
                Candidate(
                    f"{DEEPCRACK}/{partition}/{path.stem}",
                    DEEPCRACK,
                    family,
                    split,
                    path,
                    (root / f"{partition}_lab" / f"{path.stem}.png", None),
                )
            )
    return rows


def _joint(root: Path) -> list[Candidate]:
    if not root.is_dir():
        raise ValueError(f"Required dataset directory is missing: {root}")
    rows = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        name = folder.name
        fields = name.split("_")
        if len(fields) < 5 or not fields[0].isdigit() or not fields[2].isdigit():
            raise ValueError(f"Cannot derive a route from {folder}")
        road = f"{fields[1]}_{fields[2]}"
        split = {"RS_386": "test", "DF_080": "validation", "DF_020": "validation"}.get(
            road, "train"
        )
        rows.append(
            Candidate(
                f"{JOINT}/{name}",
                JOINT,
                road,
                split,
                folder / f"{name}_RAW.jpg",
                (folder / f"{name}_CRACK.png", folder / f"{name}_POTHOLE.png"),
            )
        )
    return rows


def _background(root: Path, nuisance_names: set[str]) -> list[Candidate]:
    paths = _files(root)
    unknown = nuisance_names - {path.name for path in paths}
    if unknown:
        raise ValueError(f"Unknown reviewed nuisance images: {sorted(unknown)}")
    return [
        Candidate(
            f"{BACKGROUND}/{path.stem}",
            BACKGROUND,
            "S315",
            "test",
            path,
            (None, None),
            "nuisance" if path.name in nuisance_names else "background",
        )
        for path in paths
    ]


def _perceptual_hash(image: Rgb) -> str:
    gray = cv2.cvtColor(
        cv2.resize(image, (32, 32), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY
    )
    band = cv2.dct(gray.astype(np.float32))[:8, :8].ravel()[1:]
    bits = band > np.median(band)
    return f"{sum(int(bit) << shift for shift, bit in enumerate(bits)):016x}"


def _audit(candidate: Candidate) -> Sample:
    image = read_rgb(candidate.image)
    height, width = image.shape[:2]
    labels = []
    mask_hashes = []
    for path in candidate.masks:
        labels.append(bool(read_mask(path, (height, width)).any()) if path else None)
        mask_hashes.append(sha256(path) if path else None)
    if candidate.source == BACKGROUND:
        labels = [False, False]
    return Sample(
        **asdict(candidate),
        labels=tuple(labels),
        width=width,
        height=height,
        image_sha256=sha256(candidate.image),
        mask_sha256=tuple(mask_hashes),
        phash=_perceptual_hash(image),
    )


def without_split_leakage(samples: list[Sample]) -> tuple[list[Sample], list[dict[str, str]]]:
    # Keep the higher-priority split and remove any overlapping DeepCrack family.
    groups: dict[tuple[str, str], Sample] = {}
    higher: list[tuple[Sample, int]] = []
    dropped: dict[str, dict[str, str]] = {}
    family_drops: dict[tuple[str, str, str], Sample] = {}
    ordered = sorted(samples, key=lambda row: (_SPLIT_PRIORITY[row.split], row.id))
    for sample in ordered:
        group = (sample.source, sample.group)
        first = groups.setdefault(group, sample)
        image_hash = int(sample.phash, 16)
        match = first if first.split != sample.split else None
        if match is None:
            for other, other_hash in higher:
                if other.split == sample.split:
                    continue
                same_image = sample.image_sha256 == other.image_sha256
                similar_shape = (
                    abs(sample.width / sample.height - other.width / other.height) < 0.05
                )
                if same_image or (similar_shape and (image_hash ^ other_hash).bit_count() <= 5):
                    match = other
                    break
        if match is None:
            higher.append((sample, image_hash))
            continue
        dropped[sample.id] = {
            "id": sample.id,
            "reason": "Cross-split source family or perceptual duplicate candidate",
            "kept_id": match.id,
        }
        if sample.source == DEEPCRACK:
            family_drops[(sample.source, sample.group, sample.split)] = match
    for sample in ordered:
        match = family_drops.get((sample.source, sample.group, sample.split))
        if match is not None:
            dropped.setdefault(
                sample.id,
                {"id": sample.id, "reason": "Overlapping DeepCrack family", "kept_id": match.id},
            )
    return [sample for sample in ordered if sample.id not in dropped], list(dropped.values())


def _serialize(sample: Sample, relative_to: Path) -> dict:
    row = asdict(sample)
    row["image"] = os.path.relpath(sample.image, relative_to)
    row["masks"] = [os.path.relpath(path, relative_to) if path else None for path in sample.masks]
    return row


def prepare(data_dir: Path, output: Path, nuisance_names: set[str]) -> dict:
    raw = data_dir / "raw"
    candidates = [
        *_deepcrack(raw / "deepcrack"),
        *_joint(raw / "joint"),
        *_background(raw / "background", nuisance_names),
    ]
    audited = []
    rejected = []
    for index, candidate in enumerate(candidates, start=1):
        try:
            audited.append(_audit(candidate))
        except ValueError as error:
            rejected.append({"id": candidate.id, "reason": str(error)})
        if index % 500 == 0:
            print(f"Audited {index}/{len(candidates)} images", flush=True)
    samples, duplicates = without_split_leakage(audited)
    for split in _SPLIT_PRIORITY:
        subset = [sample for sample in samples if sample.split == split]
        for index, name in enumerate(CLASSES):
            if not any(row.labels[index] is True for row in subset) or not any(
                row.labels[index] is False for row in subset
            ):
                raise ValueError(f"The {split} split requires positive and negative {name} labels")
    if not any(sample.source == BACKGROUND for sample in samples):
        raise ValueError("The clean-background challenge is empty")
    sources = {
        name: {**source, "archive_sha256": sha256(data_dir / "archives" / source["archive"])}
        for name, source in _SOURCES.items()
    }
    counts = Counter(f"{sample.split}/{sample.source}" for sample in samples)
    document = {
        "schema_version": 1,
        "classes": CLASSES,
        "sources": sources,
        "counts": dict(sorted(counts.items())),
        "excluded": rejected + duplicates,
        "samples": [_serialize(sample, output.parent) for sample in samples],
    }
    write_json(output, document)
    return {"counts": document["counts"], "excluded": len(document["excluded"])}


def load_manifest(path: Path) -> list[Sample]:
    with path.open(encoding="utf-8") as stream:
        document = json.load(stream)
    if document["schema_version"] != 1 or tuple(document["classes"]) != CLASSES:
        raise ValueError(f"Unsupported dataset manifest: {path}")
    rows = []
    for row in document["samples"]:
        row["image"] = path.parent / row["image"]
        row["masks"] = tuple(path.parent / value if value else None for value in row["masks"])
        row["labels"] = tuple(row["labels"])
        rows.append(Sample(**row))
    if not rows:
        raise ValueError(f"Dataset manifest contains no images: {path}")
    return rows
