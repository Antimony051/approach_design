"""Calibrate on validation images, then compare both detectors on the frozen holdout."""

import json
from dataclasses import asdict
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import numpy as np
from PIL import Image

from . import CLASSES, baseline
from .artifacts import sha256, write_json
from .datasets import Sample, load_manifest
from .images import ImageSettings, TilePredictor, overlay, resized_mask, scaled_image, tiled_scores
from .metrics import best_threshold, image_metrics
from .model import LearnedDetector, load_model
from .prediction import Inference, read_bundle
from .regions import RegionSettings, components

_METHODS = ("learned", "opencv")
_SEEDS = (0.08, 0.16, 0.28, 0.42, 0.58, 0.72, 0.84)
_AREAS = ((12, 32, 80), (50, 200, 600, 1600))
_MIN_FILL = (0.0, 0.16)


def _calibrate(
    method: str, detector: TilePredictor, samples: list[Sample], image: ImageSettings
) -> tuple[dict, dict]:
    grids = [list(product(_SEEDS, areas)) for areas in _AREAS]
    values = [np.zeros((len(samples), len(grid))) for grid in grids]
    for row, sample in enumerate(samples):
        rgb = scaled_image(sample.load()[0], image)
        maps = tiled_scores(rgb, image, detector)
        for channel, score_map in enumerate(maps):
            if sample.labels[channel] is None:
                continue
            offset = 0
            for seed in _SEEDS:
                stats = components(score_map, seed)
                for area in _AREAS[channel]:
                    keep = stats.supported(area, _MIN_FILL[channel])
                    values[channel][row, offset] = stats.means[keep].max(initial=0.0)
                    offset += 1
        if (row + 1) % 100 == 0:
            print(f"{method} calibration {row + 1}/{len(samples)}", flush=True)

    rules, results = {}, {}
    for channel, name in enumerate(CLASSES):
        known = np.array([row.labels[channel] is not None for row in samples])
        truth = [
            bool(sample.labels[channel]) for sample in samples if sample.labels[channel] is not None
        ]
        selected = None
        best = (-1.0, -1.0)
        for (seed, area), scores in zip(grids[channel], values[channel][known].T, strict=True):
            decision, f1, precision = best_threshold(scores, truth)
            if (f1, precision) > best:
                best = (f1, precision)
                selected = (RegionSettings(seed, area, decision, _MIN_FILL[channel]), scores)
        rule, scores = selected
        rules[name] = asdict(rule)
        results[name] = image_metrics(scores, truth, rule.decision)
    return rules, results


def _summarize(rows: list[dict], rules: tuple[RegionSettings, RegionSettings]) -> dict:
    scores = {}
    for index, name in enumerate(CLASSES):
        known = [row for row in rows if row["labels"][index] is not None]
        stats = image_metrics(
            [row["scores"][name] for row in known],
            [row["labels"][index] for row in known],
            rules[index].decision,
        )
        annotated = [row["pixels"][index] for row in known if row["pixels"][index] is not None]
        tp, fp, fn = np.sum(annotated, axis=0).tolist() if annotated else (0, 0, 0)
        stats["pixel_dice"] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
        stats["pixel_iou"] = tp / (tp + fp + fn) if tp + fp + fn else None
        scores[name] = stats
    return scores


def _save_example(
    output: Path, method: str, category: str, rgb: np.ndarray, predicted: tuple, actual: np.ndarray
) -> str:
    # Show the same image twice with reference masks on the left and predictions on the right.
    panels = []
    for masks in (actual, predicted):
        panel = Image.fromarray(overlay(rgb, masks))
        panel.thumbnail((680, 480))
        panels.append(panel)
    width, height = panels[0].size
    sheet = Image.new("RGB", (2 * width, height))
    sheet.paste(panels[0], (0, 0))
    sheet.paste(panels[1], (width, 0))
    relative = f"overlays/{method}-{category}.jpg"
    sheet.save(output / relative, quality=89)
    return relative


def _test(
    method: str, inference: Inference, samples: list[Sample], output: Path
) -> tuple[dict, list[dict]]:
    observations = []
    examples: dict[str, dict] = {}
    for index, sample in enumerate(samples, start=1):
        rgb, actual = sample.load()
        result, masks = inference.score(rgb)
        detected = result["detected_types"]
        pixels = []
        categories = []
        if sample.labels == (True, True):
            categories.append("both")
        if sample.kind == "background" and not detected:
            categories.append("clean")
        if sample.kind == "nuisance" and detected:
            categories.append("painted-marking-false-alarm")
        for channel, name in enumerate(CLASSES):
            label = sample.labels[channel]
            if label is True and name not in detected:
                categories.append(f"miss-{name}")
            if label is False and name in detected:
                categories.append(f"false-alarm-{name}")
            if sample.masks[channel] is None:
                pixels.append(None)
                continue
            mask = resized_mask(masks[channel], rgb.shape[:2])
            reference = actual[channel]
            pixels.append(
                [
                    int(np.count_nonzero(mask & reference)),
                    int(np.count_nonzero(mask & ~reference)),
                    int(np.count_nonzero(~mask & reference)),
                ]
            )

        for category in categories:
            if category not in examples:
                path = _save_example(output, method, category, rgb, masks, actual)
                examples[category] = {
                    "file": path,
                    "input_id": sample.id,
                    "labels": sample.labels,
                    **result,
                }
        observations.append(
            {
                "input_id": sample.id,
                "source": sample.source,
                "group": sample.group,
                "kind": sample.kind,
                "labels": sample.labels,
                "pixels": pixels,
                **result,
            }
        )
        if index % 200 == 0:
            print(f"{method} test {index}/{len(samples)}", flush=True)
    nuisance = [row for row in observations if row["kind"] == "nuisance"]
    sources = sorted({row["source"] for row in observations})
    return {
        "overall": _summarize(observations, inference.region_rules),
        "by_source": {
            source: _summarize(
                [row for row in observations if row["source"] == source], inference.region_rules
            )
            for source in sources
        },
        "painted_markings": {
            "images": len(nuisance),
            "with_false_alarm": sum(bool(row["detected_types"]) for row in nuisance),
            "by_class": {
                name: sum(name in row["detected_types"] for row in nuisance) for name in CLASSES
            },
        },
        "examples": examples,
    }, observations


def _number(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def _markdown(report: dict) -> str:
    lines = [
        "# PaveWatch camera version 0 benchmark",
        "",
        f"Model {report['model_version']} on {report['test_images']} held-out images.",
        (
            "Each metric uses images with known labels for its class. DeepCrack contributes "
            "crack labels only. The source-specific results are in report.json."
        ),
        "",
        "| Detector | Visual type | Known | TP | FP | FN | Precision | Recall | F1 | AP | Mask Dice |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method, result in report["test"].items():
        for name, values in result["overall"].items():
            counts = " | ".join(str(values[key]) for key in ("known_images", "tp", "fp", "fn"))
            metrics = " | ".join(
                _number(values[key])
                for key in ("precision", "recall", "f1", "average_precision", "pixel_dice")
            )
            lines.append(f"| {method} | {name} | {counts} | {metrics} |")
    lines.extend(["", "## Painted-marking challenge", ""])
    for method, result in report["test"].items():
        nuisance = result["painted_markings"]
        lines.append(
            f"- {method} flagged {nuisance['with_false_alarm']} of {nuisance['images']} "
            "reviewed background images with paint markings."
        )
    lines.extend(
        [
            "",
            "## Scope",
            "",
            (
                "Thresholds and component support were selected on the validation split. The test split "
                "holds out an entire annotated road, the released DeepCrack test partition, and an "
                "external clean-background subset. Its scores describe these public data sources."
            ),
            "",
            (
                "The project ground evaluation requires separately collected, size-qualified examples "
                "and object-level matching. The output scores rank visible evidence on a 0–1 scale."
            ),
            "",
            (
                "The overlay examples show labels on the left and predicted regions on the right. "
                "Orange marks cracks and blue marks potholes."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def benchmark(manifest: Path, model_dir: Path, output: Path, device: str) -> dict:
    rows = load_manifest(manifest)
    validation = [row for row in rows if row.split == "validation"]
    test = [row for row in rows if row.split == "test"]
    if not validation or not test:
        raise ValueError("Benchmarking requires nonempty validation and test splits")
    with (model_dir / "training.json").open(encoding="utf-8") as stream:
        training = json.load(stream)
    weights = model_dir / "weights.pt"
    manifest_hash = sha256(manifest)
    if training["status"] != "trained" or training["manifest_sha256"] != manifest_hash:
        raise ValueError("Benchmark requires a completed model trained with this frozen manifest")
    if training["weights_sha256"] != sha256(weights):
        raise ValueError("Model weights do not match the training record")
    image = ImageSettings(**training["image"])
    learned = LearnedDetector(load_model(weights, device), device)
    predictors = {"learned": learned, "opencv": baseline.predict_tiles}
    output.mkdir(parents=True, exist_ok=False)
    (output / "overlays").mkdir()
    if (model_dir / "config.json").exists():
        config = read_bundle(model_dir)
        if config["manifest_sha256"] != manifest_hash or config["weights_sha256"] != sha256(
            weights
        ):
            raise ValueError("The calibrated bundle belongs to a different manifest or checkpoint")
    else:
        rules, validation_metrics = {}, {}
        for method in _METHODS:
            rules[method], validation_metrics[method] = _calibrate(
                method, predictors[method], validation, image
            )
        config = {
            "schema_version": 1,
            "classes": CLASSES,
            "model_version": f"camera-v0-{training['weights_sha256'][:12]}",
            "image": asdict(image),
            "rules": rules,
            "validation": validation_metrics,
            "manifest_sha256": manifest_hash,
            "weights_sha256": training["weights_sha256"],
        }
        # Publish the frozen operating points before opening the held-out images.
        write_json(model_dir / "config.json", config)

    report = {
        "schema_version": 1,
        "model_version": config["model_version"],
        "manifest_sha256": manifest_hash,
        "utc_scored": datetime.now(timezone.utc).isoformat(),
        "test_images": len(test),
        "device": device,
        "validation": config["validation"],
        "test": {},
    }
    for method in _METHODS:
        rules = tuple(RegionSettings(**config["rules"][method][name]) for name in CLASSES)
        version = config["model_version"]
        if method == "opencv":
            version = f"{version}-opencv"
        inference = Inference(image, rules, predictors[method], version)
        result, predictions = _test(method, inference, test, output)
        report["test"][method] = result
        write_json(output / f"{method}-predictions.json", predictions)
    write_json(output / "report.json", report)
    (output / "REPORT.md").write_text(_markdown(report), encoding="utf-8")
    return report
