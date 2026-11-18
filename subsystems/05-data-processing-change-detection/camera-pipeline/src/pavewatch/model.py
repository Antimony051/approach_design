"""Load and run the version 0 two-channel DeepLabV3 model."""

from collections.abc import Sequence
from pathlib import Path

import numpy as np
import torch
from torch import Tensor, nn
from torchvision.models.segmentation import (
    DeepLabV3_MobileNet_V3_Large_Weights,
    deeplabv3_mobilenet_v3_large,
)

from . import CLASSES
from .images import Rgb, Scores

PRETRAINED = DeepLabV3_MobileNet_V3_Large_Weights.COCO_WITH_VOC_LABELS_V1
_MEAN = (0.485, 0.456, 0.406)
_STD = (0.229, 0.224, 0.225)


def build_model(pretrained: bool = False) -> nn.Module:
    model = deeplabv3_mobilenet_v3_large(
        weights=PRETRAINED if pretrained else None, weights_backbone=None
    )
    last = model.classifier[-1]
    model.classifier[-1] = nn.Conv2d(last.in_channels, len(CLASSES), kernel_size=1)
    model.aux_classifier = None
    return model


def normalized_input(images: Sequence[Rgb]) -> Tensor:
    rgb = torch.from_numpy(np.stack(images)).permute(0, 3, 1, 2).float().div_(255)
    mean = rgb.new_tensor(_MEAN).view(1, 3, 1, 1)
    std = rgb.new_tensor(_STD).view(1, 3, 1, 1)
    return rgb.sub_(mean).div_(std)


def load_model(weights: Path, device: str = "cpu") -> nn.Module:
    if not weights.is_file():
        raise ValueError(f"Model weights are missing: {weights}")
    model = build_model()
    model.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
    return model.to(device).eval()


class LearnedDetector:
    def __init__(self, model: nn.Module, device: str) -> None:
        self.model = model
        self.device = device

    @torch.inference_mode()
    def __call__(self, tiles: Sequence[Rgb]) -> Scores:
        inputs = normalized_input(tiles).to(self.device)
        return self.model(inputs)["out"].sigmoid().cpu().numpy()
