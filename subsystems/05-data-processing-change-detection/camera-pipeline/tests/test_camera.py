"""Focused checks for input errors, tiling, split leakage, and partial supervision."""

import json
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

from pavewatch import CLASSES
from pavewatch.cli import main
from pavewatch.datasets import DEEPCRACK, Sample, without_split_leakage
from pavewatch.images import ImageSettings, tiled_scores
from pavewatch.metrics import average_precision, best_threshold
from pavewatch.regions import RegionSettings, image_evidence
from pavewatch.training import masked_loss


def test_tiling_stitches_a_component_across_tile_boundaries():
    image = np.zeros((81, 139, 3), dtype=np.uint8)
    image[30:34, 25:120, 0] = 255
    settings = ImageSettings(tile_size=64, overlap=16, max_side=160)

    def detector(tiles):
        signal = np.stack(tiles)[..., 0].astype(np.float32) / 255
        return np.stack((signal, signal * 0), axis=1)

    maps = tiled_scores(image, settings, detector, batch_size=2)
    score, mask = image_evidence(maps[0], RegionSettings(0.5, 320))
    assert score == pytest.approx(1)
    assert mask.sum() == 380
    assert np.array_equal(mask, image[..., 0] > 0)


def test_isolated_pixel_has_no_image_score():
    scores = np.zeros((10, 10), dtype=np.float32)
    scores[2, 3] = 1.0
    score, mask = image_evidence(scores, RegionSettings(0.5, 3))
    assert score == 0
    assert not mask.any()


def test_unknown_mask_channel_does_not_contribute_gradient():
    logits = torch.zeros((1, 2, 8, 8), requires_grad=True)
    targets = torch.zeros_like(logits, dtype=torch.bool)
    targets[:, 0, 2:4, 3:5] = True
    valid = torch.zeros_like(targets)
    valid[:, 0] = True
    masked_loss(logits, targets, valid).backward()
    assert torch.count_nonzero(logits.grad[:, 1]) == 0
    assert torch.count_nonzero(logits.grad[:, 0]) > 0


def test_released_test_family_is_preserved():
    def sample(name, family, split, phash):
        return Sample(
            name,
            DEEPCRACK,
            family,
            split,
            Path(name),
            (None, None),
            width=544,
            height=384,
            phash=phash,
            image_sha256=name,
        )

    test = sample("test", "family-a", "test", "ffff")
    train_same_family = sample("train", "family-a", "train", "ffff")
    train_unrelated = sample("other", "family-b", "train", "0")
    kept, excluded = without_split_leakage([train_same_family, train_unrelated, test])
    assert [row.id for row in kept] == ["test", "other"]
    assert excluded[0]["kept_id"] == "test"


def test_threshold_selection_handles_ties_and_zero_evidence():
    assert average_precision([0.8, 0.8, 0.1], [True, False, False]) == 0.5
    assert best_threshold([0.8, 0.8, 0.1], [True, False, False])[0] == 0.8
    assert best_threshold([0.0, 0.0], [True, False]) == (1.0, 0.0, 0.0)


@pytest.mark.parametrize("extension", ("jpg", "png"))
def test_predict_open_cv_clean_image(tmp_path, capsys, extension):
    image = tmp_path / f"clean.{extension}"
    Image.new("RGB", (120, 80), (128, 128, 128)).save(image)
    config = {
        "schema_version": 1,
        "model_version": "fixture",
        "classes": CLASSES,
        "image": {"tile_size": 64, "overlap": 16, "max_side": 160},
        "rules": {"opencv": {name: {"seed": 0.2, "min_area": 12} for name in CLASSES}},
    }
    (tmp_path / "config.json").write_text(json.dumps(config))
    output = tmp_path / "overlay.png"
    args = ["predict", str(image), "--model-dir", str(tmp_path), "--detector", "opencv"]
    assert main([*args, "--overlay", str(output)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["scores"] == {name: 0.0 for name in CLASSES}
    assert result["detected_types"] == []
    with Image.open(output) as rendered:
        assert rendered.size == (120, 80)


@pytest.mark.parametrize("payload", (None, b"", b"this is not an image"))
def test_bad_input_fails_with_clear_error(tmp_path, capsys, payload):
    path = tmp_path / "bad.png"
    if payload is not None:
        path.write_bytes(payload)
    assert main(["predict", str(path)]) == 1
    captured = capsys.readouterr()
    assert "Cannot read image" in captured.err
    assert captured.out == ""
