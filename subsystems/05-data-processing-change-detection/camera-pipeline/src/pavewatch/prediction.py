"""Run either detector using the calibrated camera model bundle."""

import json
from dataclasses import dataclass
from pathlib import Path

from . import CLASSES, baseline
from .artifacts import sha256
from .images import ImageSettings, Mask, Rgb, TilePredictor, scaled_image, tiled_scores
from .regions import RegionSettings, image_evidence


@dataclass(frozen=True)
class Inference:
    image: ImageSettings
    region_rules: tuple[RegionSettings, RegionSettings]
    predictor: TilePredictor
    version: str

    def score(self, image: Rgb) -> tuple[dict, tuple[Mask, Mask]]:
        scaled = scaled_image(image, self.image)
        maps = tiled_scores(scaled, self.image, self.predictor)
        scores = {}
        types = []
        masks = []
        for name, score_map, rule in zip(CLASSES, maps, self.region_rules, strict=True):
            score, mask = image_evidence(score_map, rule)
            scores[name] = score
            if score >= rule.decision:
                types.append(name)
            masks.append(mask)
        return {
            "model_version": self.version,
            "scores": scores,
            "detected_types": types,
        }, (masks[0], masks[1])


def read_bundle(model_dir: Path) -> dict:
    path = model_dir / "config.json"
    if not path.is_file():
        raise ValueError(f"Calibrated model bundle is missing {path}")
    with path.open(encoding="utf-8") as stream:
        config = json.load(stream)
    if config["schema_version"] != 1 or tuple(config["classes"]) != CLASSES:
        raise ValueError(f"Unsupported model bundle: {path}")
    return config


def open_inference(model_dir: Path, method: str = "learned", device: str = "cpu") -> Inference:
    config = read_bundle(model_dir)
    rules = tuple(RegionSettings(**config["rules"][method][name]) for name in CLASSES)
    version = config["model_version"]
    if method == "learned":
        from .model import LearnedDetector, load_model

        weights = model_dir / "weights.pt"
        if not weights.is_file() or sha256(weights) != config["weights_sha256"]:
            raise ValueError(f"Model weights are missing or do not match the bundle: {weights}")
        predictor = LearnedDetector(load_model(weights, device), device)
    else:
        predictor = baseline.predict_tiles
        version = f"{version}-opencv"
    return Inference(ImageSettings(**config["image"]), rules, predictor, version)
