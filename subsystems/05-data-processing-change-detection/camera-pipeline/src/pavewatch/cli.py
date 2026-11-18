"""PaveWatch camera version 0 command-line application."""

import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import cv2
from PIL import Image

from .images import ImageSettings, overlay, read_rgb
from .prediction import open_inference


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score crack-like and pothole-like evidence in RGB photos"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    common_model = argparse.ArgumentParser(add_help=False)
    common_model.add_argument("--model-dir", type=Path, default=Path("models/camera-v0"))
    common_model.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    manifest = argparse.ArgumentParser(add_help=False)
    manifest.add_argument("--manifest", type=Path, default=Path("data/camera-v0/manifest.json"))

    predict = commands.add_parser("predict", parents=[common_model], help="Score one JPEG or PNG")
    predict.add_argument("image", type=Path)
    predict.add_argument("--detector", choices=("learned", "opencv"), default="learned")
    predict.add_argument("--overlay", type=Path)

    sequence = commands.add_parser(
        "sequence", parents=[common_model], help="Replay a camera pass in A/B/C modes"
    )
    sequence.add_argument("session", type=Path)
    sequence.add_argument("--config", type=Path, default=Path("configs/sequence-v1.json"))
    sequence.add_argument("--labels", type=Path, help="Optional independently labeled pass")
    sequence.add_argument("--output", type=Path, required=True)

    prepare = commands.add_parser(
        "prepare", parents=[manifest], help="Audit datasets and freeze splits"
    )
    prepare.add_argument("--data-dir", type=Path, default=Path("data"))
    prepare.add_argument(
        "--nuisance-list", type=Path, help="Reviewed background filenames, one per line"
    )

    train = commands.add_parser(
        "train", parents=[common_model, manifest], help="Fine-tune DeepLabV3"
    )
    train.add_argument("--epochs", type=int, default=6)
    train.add_argument("--batch-size", type=int, default=12)
    train.add_argument("--workers", type=int, default=2)
    train.add_argument("--seed", type=int, default=17)
    train.add_argument("--tile-size", type=int, default=320)
    train.add_argument("--overlap", type=int, default=64)
    train.add_argument("--max-side", type=int, default=960)
    train.add_argument(
        "--max-batches", type=int, help="Limit each epoch and mark the result as a smoke test"
    )

    evaluate = commands.add_parser(
        "evaluate", parents=[common_model, manifest], help="Calibrate and compare both detectors"
    )
    evaluate.add_argument("--output", type=Path, required=True)
    return parser


def _write_overlay(path: Path, image: Image.Image) -> None:
    suffix = path.suffix.lower()
    if suffix not in {".png", ".jpeg", ".jpg"}:
        raise ValueError("Overlay path must end in .png, .jpg, or .jpeg")
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        dir=path.parent, prefix=".overlay.", suffix=suffix, delete=False
    ) as stream:
        temporary = Path(stream.name)
    try:
        image.save(temporary)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    cv2.setNumThreads(1)
    try:
        if args.command == "prepare":
            from .datasets import prepare

            names = (
                set(args.nuisance_list.read_text().splitlines()) if args.nuisance_list else set()
            )
            result = prepare(args.data_dir, args.manifest, names)
        elif args.command == "sequence":
            from .sequence import replay
            from .training import select_device

            result = replay(
                args.session,
                args.config,
                args.model_dir,
                select_device(args.device),
                args.output,
                args.labels,
            )
        elif args.command == "predict":
            rgb = read_rgb(args.image)
            if args.overlay and args.overlay.resolve() == args.image.resolve():
                raise ValueError("Choose an overlay path different from the input image")
            device = "cpu"
            if args.detector == "learned":
                from .training import select_device

                device = select_device(args.device)
            predictor = open_inference(args.model_dir, args.detector, device)
            result, masks = predictor.score(rgb)
            if args.overlay:
                _write_overlay(args.overlay, Image.fromarray(overlay(rgb, masks)))
        elif args.command == "train":
            from .training import TrainingSettings, select_device, train

            settings = TrainingSettings(
                args.epochs, args.batch_size, args.workers, args.seed, args.max_batches
            )
            image = ImageSettings(args.tile_size, args.overlap, args.max_side)
            result = train(
                args.manifest, args.model_dir, image, settings, select_device(args.device)
            )
        else:
            from .benchmark import benchmark
            from .training import select_device

            report = benchmark(
                args.manifest, args.model_dir, args.output, select_device(args.device)
            )
            result = {
                "model_version": report["model_version"],
                "test_images": report["test_images"],
                "report": str(args.output / "REPORT.md"),
            }
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print(f"pavewatch: {error}", file=sys.stderr)
        return 1
