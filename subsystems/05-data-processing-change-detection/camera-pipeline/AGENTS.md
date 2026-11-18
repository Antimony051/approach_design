# Data processing subsystem

Turn camera images and LiDAR data into traceable findings for the findings
presentation subsystem on its separate CPU VM. Keep data ingestion, validation,
processing and findings export as clear stages; keep algorithms separate from file I/O and configuration.

## Everyday development

- Use UV for Python packages and all Python execution, including one-off scripts:
  `uv add`, `uv add --dev`, `uv run`. Keep dependencies in pyproject.toml, commit
  uv.lock and use `uv sync --locked` to reproduce an existing environment.
- Follow existing project conventions. Use small functions, explicit configuration,
  types at module boundaries and useful errors. Keep reusable logic in modules;
  notebooks should call those modules. Keep credentials in environment/config.
- Document commands to run the pipeline and its checks. Test changed behavior on
  small representative fixtures, including missing, corrupt and empty inputs.
  State which checks ran and whether they exercised real GPU hardware.

## Data correctness and reproducibility

- Keep raw camera and LiDAR inputs immutable. Store derived data separately and
  keep large datasets, generated artifacts and environments out of Git.
- Validate inputs at ingestion: expected metadata, timestamps, units, coordinate
  frames and calibration references where applicable. Do not assume sensor
  alignment or silently convert unknown units. Record rejected samples/reasons.
- Record input IDs, run ID, configuration, code/model/calibration versions and
  relevant dependency versions with outputs. Use explicit time zones (UTC for
  interchange), deterministic ordering and random seeds where supported.
- Process in bounded batches/chunks, cap workers and checkpoint expensive stages.
  Make retries safe and write completed outputs atomically. Distinguish a valid
  run with no findings from failed or incomplete processing.
- Document a versioned findings format shared with the presentation subsystem:
  stable finding/source/run IDs, timestamps, provenance, units/coordinate frames
  and quality/confidence meaning where applicable. Validate exports, include an
  example payload and test consumer compatibility when changing that contract.
  Keep large sensor artifacts in storage and reference them from findings.

## GPU use on this workstation

- The default Standard_NC4as_T4_v3 has one NVIDIA T4 (16 GB GPU memory), 4 vCPUs
  and 28 GiB RAM. See [Azure's size reference](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/ncast4v3-series).
  This is shared capacity: check `nvidia-smi` or `nvtop` before large runs and
  leave headroom for other processing users. The portal runs on a separate CPU VM.
- After workstation setup/reboot, `~/check_gpu.sh` checks host and Docker GPU
  access. Also verify that the chosen Python library detects and uses the GPU;
  successful driver checks alone do not demonstrate pipeline acceleration.
- Install CUDA-enabled packages/images compatible with the installed driver and
  record their versions. Setup includes the driver and Docker NVIDIA runtime;
  the full CUDA compiler toolkit (nvcc) is not preinstalled. Coordinate driver
  changes and reboots with other users.
- Profile representative work before optimizing. Bound batches by actual GPU
  memory, avoid unnecessary host/device copies, and handle out-of-memory errors
  explicitly. Report unavailable GPU execution or CPU fallback clearly. Validate
  numerical/quality effects before changing precision or acceleration methods.

## Backup and restore: read when needed

When asked to back up important work to the bucket or restore files, read
`docs/backup-instructions.md` in the existing VM workspace and follow it.
It contains the storage configuration, authentication, dated archive procedure,
verification and restore commands. Backups are manual; keep original local data
and report the exact verified backup location.
