# PaveWatch camera pipeline

Version 0 scores one JPEG or PNG for visible crack-like and pothole-like features. Use the fine-tuned DeepLabV3 model for prediction and the OpenCV detector for comparison. Each output score ranks visual evidence on a 0–1 scale. Both classes can be detected in the same image. Physical measurements require a calibrated survey.

## Set up from this checkout

Run these commands from the root of the shared design checkout with UV installed.

```bash
cd subsystems/05-data-processing-change-detection/camera-pipeline
uv sync --locked
uv run --locked pytest -q
```

The commands below use the workstation's existing standalone copy and its trained bundle. For inference from this checkout, use `uv` in place of `.tools/uv` and pass the workstation's bundle with `--model-dir`.

## Predict on one image

Run this command on the Azure processing workstation.

```bash
cd /home/dev_admin/data_processing_subsystem
.tools/uv run --locked pavewatch predict /path/to/photo.jpg \
    --model-dir models/camera-v0 --overlay runs/photo-overlay.png
```

A machine with UV on PATH can use `uv run --locked` from the camera pipeline directory. Once installed, use `uv run --offline --no-sync pavewatch predict ...` for offline prediction. By default, the command uses CPU inference. The optional overlay shows supported candidate regions in the image's displayed orientation. Orange indicates crack evidence and blue indicates pothole evidence. Use `--detector opencv` to score with the classical baseline. A successful response includes `model_version`, both `scores`, and `detected_types`. Missing or corrupt inputs return an error and exit nonzero.

For the first run, the trained model bundle is in `models/camera-v0/`. It includes the weights, the device and training record, and frozen validation thresholds. The benchmark is in `runs/camera-v0/`. It includes the report, per-image results, and paired label and prediction overlays. Large files are kept outside Git.

## Reproduce the benchmark

The frozen input manifest is `data/camera-v0/manifest.json`. It records each image, mask, label coverage, source group, split, hash, and exclusion. The first benchmark uses these releases.

- Liu et al. DeepCrack. Use the authors' training and test image and mask folders. Validation uses training families only. Potholes are unknown on these images. The provided test partition is preserved. [DeepCrack repository and terms](https://github.com/yhlleo/DeepCrack)
- Passos et al. Cracks and Potholes in Road Images. This run used the authors' GitHub snapshot at `1f200541d2e88596fb9dcd91f4262c1ac5f6202e`. RS_386 is held out and DF_080 and DF_020 are used for validation. [Author snapshot](https://github.com/biankatpas/Cracks-and-Potholes-in-Road-Images-Dataset/tree/1f200541d2e88596fb9dcd91f4262c1ac5f6202e/Dataset), [dataset record and terms](https://data.mendeley.com/datasets/t576ydh9v8/4)
- PaveDistress v1. A route-spaced subset of 120 published background images is a separate held-out challenge. Forty-two images were tagged by contact-sheet review for visible markings. [Dataset and terms](https://data.mendeley.com/datasets/f46zt2g83x/1)

To rebuild the manifest, put the original archives in `data/archives/` and the images under `data/raw/deepcrack`, `data/raw/joint`, and `data/raw/background`. The expected layout matches the authors' folders. The initial background selection and reviewed names are saved in `.tools/background-files.txt` and `runs/audit/nuisance-images.txt` on Azure. Use a new manifest path for a changed data selection.

```bash
.tools/uv sync --locked
.tools/uv run --locked pavewatch prepare --manifest data/camera-v0/manifest.json \
    --nuisance-list runs/audit/nuisance-images.txt
.tools/uv run --locked pytest -q
.tools/uv run --locked ruff check src tests
```

The workstation's separate CUDA environment uses PyTorch 2.9.1 and TorchVision 0.24.1 CUDA 12.6 wheels. The CPU project stays locked for ordinary inference. Use the host driver check before a CUDA run. [Official PyTorch wheel matrix](https://pytorch.org/get-started/previous-versions/)

```bash
nvidia-smi
UV_PROJECT_ENVIRONMENT=.venv-cuda .tools/uv sync --locked
.tools/uv pip install --python .venv-cuda/bin/python \
    --index https://download.pytorch.org/whl/cu126 \
    'torch==2.9.1+cu126' 'torchvision==0.24.1+cu126'
```

Use a fresh output path for each training run and benchmark. Run long jobs in tmux to retain logs if the SSH connection drops. The first training run used six epochs and a batch size of 12 on the T4. Select the epoch by validation loss and the component and image thresholds by validation F1. The test split is scored after those settings are frozen.

```bash
export TORCH_HOME="$PWD/data/torch"
export CUBLAS_WORKSPACE_CONFIG=:4096:8
UV_PROJECT_ENVIRONMENT=.venv-cuda .tools/uv run --no-sync pavewatch train \
    --device cuda --model-dir models/camera-rerun
UV_PROJECT_ENVIRONMENT=.venv-cuda .tools/uv run --no-sync pavewatch evaluate \
    --device cuda --model-dir models/camera-rerun --output runs/camera-rerun
```

The held-out results measure image-level performance on the named public sets. The Capstone I ground evaluation will use team images with physical size references and object-level matching. The image pipeline can later consume RGB frames from a survey export through the same prediction entry point.

## Multi-frame camera replay

Run `pavewatch sequence` to compare whole-frame, original-crop and registered multi-view findings on a pass. See [sequence replay](docs/sequence-replay.md) for the session and annotation formats, frozen configuration, fixture generators and GPU command.
