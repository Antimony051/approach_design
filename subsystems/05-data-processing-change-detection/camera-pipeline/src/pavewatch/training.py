"""Fine-tune the pretrained segmenter on labelled pavement tiles."""

import os
import random
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

import cv2
import numpy as np
import torch
from torch import Tensor, nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision import __version__ as torchvision_version

from . import CLASSES
from .artifacts import sha256, write_json
from .datasets import Sample, load_manifest
from .images import ImageSettings, resized_mask, scaled_image
from .model import PRETRAINED, build_model, normalized_input


@dataclass(frozen=True)
class TrainingSettings:
    epochs: int = 6
    batch_size: int = 12
    workers: int = 2
    seed: int = 17
    max_batches: int | None = None

    def __post_init__(self) -> None:
        if self.epochs < 1 or self.batch_size < 1 or not 0 <= self.workers <= 4:
            raise ValueError("Expected positive epochs and batch size and at most four workers")
        if self.max_batches is not None and self.max_batches < 1:
            raise ValueError("Batch limit must be positive")


def select_device(requested: str) -> str:
    if requested == "auto":
        requested = "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA was requested but PyTorch cannot access it")
    torch.set_num_threads(min(3, os.cpu_count() or 1))
    cv2.setNumThreads(1)
    return requested


class TrainingTiles(Dataset):
    def __init__(self, samples: list[Sample], settings: ImageSettings, augment: bool) -> None:
        self.samples = samples
        self.settings = settings
        self.augment = augment

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[Tensor, Tensor, Tensor]:
        sample = self.samples[index]
        image, ground_truth = sample.load()
        image = scaled_image(image, self.settings)
        height, width = image.shape[:2]
        masks = np.stack([resized_mask(mask, (height, width)) for mask in ground_truth])
        size = self.settings.tile_size
        rng = np.random.default_rng(int(np.random.randint(2**31)) if self.augment else index)
        y_limit, x_limit = max(0, height - size), max(0, width - size)
        y, x = int(rng.integers(y_limit + 1)), int(rng.integers(x_limit + 1))
        positive = masks.reshape(len(CLASSES), -1).any(axis=1).nonzero()[0]
        if positive.size and rng.random() < 0.8:
            channel = int(rng.choice(positive))
            center = int(rng.choice(np.flatnonzero(masks[channel])))
            row, col = divmod(center, width)
            offset = size // 4
            y = int(np.clip(row - size // 2 + rng.integers(-offset, offset + 1), 0, y_limit))
            x = int(np.clip(col - size // 2 + rng.integers(-offset, offset + 1), 0, x_limit))

        rgb = image[y : y + size, x : x + size]
        targets = masks[:, y : y + size, x : x + size]
        tile_height, tile_width = rgb.shape[:2]
        pad_y, pad_x = size - tile_height, size - tile_width
        rgb = cv2.copyMakeBorder(rgb, 0, pad_y, 0, pad_x, cv2.BORDER_REPLICATE)
        targets = np.pad(targets, ((0, 0), (0, pad_y), (0, pad_x)))
        valid_pixels = np.zeros((size, size), dtype=bool)
        valid_pixels[:tile_height, :tile_width] = True
        known = np.asarray([label is not None for label in sample.labels])
        valid = known[:, None, None] & valid_pixels[None, :, :]

        if self.augment:
            turns = int(rng.integers(4))
            rgb = np.rot90(rgb, turns)
            targets = np.rot90(targets, turns, axes=(1, 2))
            valid = np.rot90(valid, turns, axes=(1, 2))
            if rng.random() < 0.5:
                rgb, targets, valid = rgb[:, ::-1], targets[:, :, ::-1], valid[:, :, ::-1]
            gain = rng.uniform(0.85, 1.15)
            offset = rng.uniform(-12, 12)
            rgb = np.clip(rgb.astype(np.float32) * gain + offset, 0, 255).astype(np.uint8)

        return (
            normalized_input([rgb])[0],
            torch.from_numpy(np.ascontiguousarray(targets)),
            torch.from_numpy(np.ascontiguousarray(valid)),
        )


def masked_loss(logits: Tensor, targets: Tensor, valid: Tensor) -> Tensor:
    logits = logits.float()
    targets = targets.float()
    weights = valid.float()
    axes = (0, 2, 3)
    counts = weights.sum(dim=axes)
    active = counts > 0
    class_weights = logits.new_tensor((4.0, 2.5)).view(len(CLASSES), 1, 1)
    bce = F.binary_cross_entropy_with_logits(
        logits, targets, reduction="none", pos_weight=class_weights
    )
    class_bce = (bce * weights).sum(dim=axes) / counts.clamp_min(1)
    predictions = logits.sigmoid() * weights
    observed = targets * weights
    intersection = (predictions * observed).sum(dim=axes)
    dice = (2 * intersection + 1) / (predictions.sum(dim=axes) + observed.sum(dim=axes) + 1)
    return (class_bce[active] + 1 - dice[active]).mean()


def _epoch(
    model: nn.Module,
    batches: DataLoader,
    device: str,
    limit: int | None,
    optimizer: torch.optim.Optimizer | None,
    scaler: torch.amp.GradScaler,
) -> float:
    training = optimizer is not None
    model.train(training)
    # Preserve the pretrained running statistics, including in one-image batches.
    if training:
        for layer in model.modules():
            if isinstance(layer, nn.BatchNorm2d):
                layer.eval()
    losses = []
    with torch.set_grad_enabled(training):
        for step, (images, targets, valid) in enumerate(batches, start=1):
            images, targets, valid = (
                tensor.to(device, non_blocking=device == "cuda")
                for tensor in (images, targets, valid)
            )
            if optimizer is not None:
                optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device, dtype=torch.float16, enabled=device == "cuda"):
                logits = model(images)["out"]
                loss = masked_loss(logits, targets, valid)
            if optimizer is not None:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            losses.append(loss.detach())
            if step % 50 == 0 and training:
                print(f"  trained {step} batches", flush=True)
            if limit is not None and step >= limit:
                break
    return float(torch.stack(losses).mean().item())


def _save_weights(model: nn.Module, path: Path) -> None:
    with NamedTemporaryFile(dir=path.parent, prefix=".weights.", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        torch.save(
            {name: value.detach().cpu() for name, value in model.state_dict().items()}, temporary
        )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def train(
    manifest: Path,
    output: Path,
    image_settings: ImageSettings,
    settings: TrainingSettings,
    device: str,
) -> dict:
    manifest_hash = sha256(manifest)
    rows = load_manifest(manifest)
    if sha256(manifest) != manifest_hash:
        raise ValueError("The manifest changed while training inputs were being read")
    train_rows = [row for row in rows if row.split == "train"]
    validation_rows = [row for row in rows if row.split == "validation"]
    if not train_rows or not validation_rows:
        raise ValueError("Training requires nonempty train and validation splits")
    output.mkdir(parents=True, exist_ok=False)
    random.seed(settings.seed)
    np.random.seed(settings.seed)
    torch.manual_seed(settings.seed)
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)
    revision = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"], capture_output=True, text=True, check=False
    )
    packages = subprocess.run(
        ["git", "status", "--porcelain", "--", "src", "pyproject.toml", "uv.lock"],
        capture_output=True,
        text=True,
        check=False,
    )
    model = build_model(pretrained=True).to(device)
    print(
        f"Training device {torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'}",
        flush=True,
    )
    train_loader = DataLoader(
        TrainingTiles(train_rows, image_settings, augment=True),
        batch_size=settings.batch_size,
        shuffle=True,
        num_workers=settings.workers,
        pin_memory=device == "cuda",
        persistent_workers=settings.workers > 0,
    )
    val_loader = DataLoader(
        TrainingTiles(validation_rows, image_settings, augment=False),
        batch_size=settings.batch_size,
        num_workers=settings.workers,
        pin_memory=device == "cuda",
        persistent_workers=settings.workers > 0,
    )
    optimizer = torch.optim.AdamW(
        [
            {"params": model.backbone.parameters(), "lr": 1e-4},
            {"params": model.classifier.parameters(), "lr": 4e-4},
        ],
        weight_decay=1e-4,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, settings.epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=device == "cuda")
    weights = output / "weights.pt"
    history = []
    best_loss = float("inf")
    selected_epoch = 0
    for epoch in range(1, settings.epochs + 1):
        train_loss = _epoch(model, train_loader, device, settings.max_batches, optimizer, scaler)
        val_loss = _epoch(model, val_loader, device, settings.max_batches, None, scaler)
        if not np.isfinite(train_loss) or not np.isfinite(val_loss):
            raise ValueError(f"Nonfinite training or validation loss in epoch {epoch}")
        history.append({"epoch": epoch, "train_loss": train_loss, "validation_loss": val_loss})
        print(
            f"Epoch {epoch}/{settings.epochs} train {train_loss:.4f} validation {val_loss:.4f}",
            flush=True,
        )
        if val_loss < best_loss:
            best_loss, selected_epoch = val_loss, epoch
            _save_weights(model, weights)
        write_json(output / "history.json", history)
        scheduler.step()

    record = {
        "schema_version": 1,
        "status": "trained" if settings.max_batches is None else "smoke_test",
        "utc_completed": datetime.now(timezone.utc).isoformat(),
        "classes": CLASSES,
        "architecture": "deeplabv3_mobilenet_v3_large",
        "pretrained_weights": PRETRAINED.name,
        "pretrained_url": PRETRAINED.url,
        "training": asdict(settings),
        "image": asdict(image_settings),
        "manifest_sha256": manifest_hash,
        "code_revision": revision.stdout.strip() or None,
        "training_source_sha256": sha256(Path(__file__)),
        "source_worktree_dirty": bool(packages.stdout.strip()),
        "torch": str(torch.__version__),
        "torchvision": torchvision_version,
        "device": device,
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "peak_gpu_mib": round(torch.cuda.max_memory_allocated() / 2**20, 1)
        if device == "cuda"
        else None,
        "selected_epoch": selected_epoch,
        "weights_sha256": sha256(weights),
    }
    write_json(output / "training.json", record)
    return record
