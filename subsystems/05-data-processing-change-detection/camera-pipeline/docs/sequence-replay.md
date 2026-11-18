# Offline camera sequence replay

Run from /home/dev_admin/data_processing_subsystem. The camera-v0 weights and bundle determine the tile size, overlap, per-class region seed, minimum area and v0 decision threshold. The sequence experiment is pinned in configs/sequence-v1.json. GPU and CPU use the same weights. Allow a fresh output directory for each run.

```bash
export UV_PROJECT_ENVIRONMENT=.venv-cuda
.tools/uv run --offline --no-sync pavewatch sequence /path/to/session.json \
  --config configs/sequence-v1.json --model-dir models/camera-v0 --device cuda \
  --labels /path/to/labels.json --output runs/my-pass
```

Omit --labels for inference on an unlabeled strip. Mode C findings live in C/findings.json. A and B have parallel exports for comparison. An empty findings list is a successful replay with zero alerts. A failed replay exits nonzero and never publishes a completed output directory.

## Replay fixtures

The deterministic generators write originals, SHA-256 digests, exposure manifests and separate labels. The first two generate 1920 × 1100 textured stills with hand-specified defect and nuisance geometry, then produce overlapping 1440 × 840 JPEGs. The crack-only control includes a missing exposure. The photo generator uses the pinned source image and masks from Passos et al., Cracks and Potholes in Road Images, v4 (CC BY 4.0, https://data.mendeley.com/datasets/t576ydh9v8/4). It translates one photograph from the v0 validation road DF_020. Its two separated pothole mask components supply the two fixture IDs. All motion in these fixtures is synthesized.

```bash
export UV_PROJECT_ENVIRONMENT=.venv-cuda
.tools/uv run --offline --no-sync python tools/sequence_fixture.py data/sequence-fixtures/mixed
.tools/uv run --offline --no-sync python tools/sequence_fixture.py data/sequence-fixtures/control --control
.tools/uv run --offline --no-sync python tools/sequence_photo_fixture.py data/sequence-fixtures/photo
for pass in mixed control photo; do
  .tools/uv run --offline --no-sync pavewatch sequence data/sequence-fixtures/$pass/session.json \
    --labels data/sequence-fixtures/$pass/labels.json --config configs/sequence-v1.json \
    --output runs/my-sequence-replay/$pass --device cuda || exit 1
done
```

## Field inputs

Supply one JSON manifest per pass. A fresh pass ID identifies each traversal. Use a persistent site ID for all repeats at the same location and keep that site within one development or test partition. Frames are listed in exposure order. The source pixel system is EXIF-upright RGB with half-open [left, top, right, bottom] rectangles. Width and height refer to that decoded orientation. EXIF orientation 1 also covers a JPEG without an orientation tag. Store actual capture metadata and the native integer timestamp from the same request. Supported units are ns, us and ms. A declared missing exposure or an interval greater than 1.6 nominal periods splits a segment. Set discontinuity on the next exposure for a known break. Start a new manifest after a clock reset. Duplicate IDs, timestamps, image contents or failed validation stop the replay.

```json
{
  "schema_version": 1, "site_id": "strip-01", "pass_id": "strip-01-traverse-01",
  "capture_profile": "Pi Camera Module 3 standard, measured 3 m, full-field JPEG",
  "clock_basis": "record the verified native camera clock", "timestamp_unit": "ns",
  "nominal_fps": 5, "measured_path_m": null,
  "frames": [
    {"id": "f0001", "timestamp": 8200000000, "path": "originals/f0001.jpg",
     "sha256": "replace with 64 hex digits", "exif_orientation": 1, "width": 4608, "height": 2592,
     "exposure_us": null, "gain": null, "lens_position": null},
    {"id": "f0002", "timestamp": 8400000000, "missing": true}
  ]
}
```

Keep the module, applied sensor mode, lens, crop, height, orientation, exposure/gain/focus and any metadata sidecar with the session. Measured path length is optional. A null length leaves per-distance rates undefined. Preserve the original files at their recorded paths or replay the manifest after relocating the entire session.

## Findings and comparison

A thresholds each connected region with v0 settings. B includes A and adds an independent overlapping original-image grid on the best frame in each one-second segment bin. It fits each context into one model input and also runs detail tiles over candidate crops. A nominal crop is 25.6% of the frame width, enlarged around wider candidates. This corresponds to about a metre only for the proposed calibrated footprint. Both modes collate thresholded sightings for evaluation. Their scores remain the best observed single-frame score.

C directly registers the pavement surrounding a candidate with reciprocal ORB matches and a local RANSAC homography. Short links use inlier fraction, hull spread, residual, orientation, scale and visible-area gates. A gap breaks links. Up to three crop views spaced by three to five nominal intervals around the anchor are inspected, with crop-local sharpness and clipping gates. Two spatially aligned weak views or a strong single view can survive. The score is the mean of the two highest supporting scores, or the strong single-view score. All are uncalibrated evidence scores. Re-inspections that reuse an overlapping decision mask in the same frame are consolidated. A persistent seam may satisfy the same tests as a real defect.

Findings carry pass-local IDs, source paths/hashes and timestamps, per-view masks, class, crop bounds, model scale, registration diagnostics, reference rectangle and stitched mask, and the best original-image overlay. Decode each base64 PNG as an 8-bit mask and resize it with nearest-neighbor interpolation into its accompanying box. Each evidence crop and scale identify the highest-scoring contributor when observations from multiple crop types merge. Rejected weak single regions remain in the proposal files. A/B/C findings documents carry model and configuration identifiers. report.json records the frozen configuration, input hashes, model/implementation versions, timing, registration rejection counts and per-class evaluation.

Labels use the same pass_id and site_id, an objects list of {id, class_name, views}, and a nuisances list of {id, kind, views}. Each views object maps frame IDs to independently drawn source rectangles. Record physical dimensions and the depression-to-pothole mapping during annotation. Include all visible observations of each target; unlabeled portions of partially annotated field passes can invalidate false-positive counts. See the generated labels.json for a working example.

For each variant the evaluator matches each predicted finding to at most one same-class physical ID and vice versa. At least one contributing frame must overlap its reference box with IoU ≥0.25. The match maximizes the number of object matches. Extra eligible alerts count as duplicates and false positives. Proposal recall counts targets with any matching proposal. Link coverage requires a matching track or contributing views on at least two labeled exposures. False-positive nuisance categories can overlap. Per-100-frame runtime includes the processing required by that mode in the shared replay.

Freeze config, model, scale, site partitions and matching before scoring field test passes. Tune registration limits on manually matched development pairs, including shadows, low texture, blur and rim parallax. P3 needs ten measured positives per class and ten nuisance-only regions, per-class precision and recall ≥80%, crack width ≥20 mm and length ≥0.2 m, and depressions ≥0.5 × 0.5 m. Keep recorded distance and class eligibility with each pass.
