# PC — Data Processing & Change Detection

Lead: **Aalok Uprety**. Charter support: **Shisir Baral**. Requirements: **PC1–PC3; S2, S3, S5, S6**.

Updated November 16, 2026. **Status: post-flight workflow and independent geometry/image branches selected in SRC-034 §3.3.5; execution platform and models remain open.**

## Required function

Validate referenced observations, reconstruct pavement geometry in one documented frame, identify geometry/visible concerns, preserve uncertainty/gaps, and export inspectable findings. A current survey stands on its own; earlier-survey comparison is optional.

## Selected processing workflow

**ImportValidator → TimeMapper → PoseResolver → FrameTransformer**, then **GeometryAnalyzer** and **VisualDetector** in parallel, followed by **FindingAssembler → ReportExporter**. Import checks manifests, checksums, completeness, readable records and gaps. Retain native times/clock maps and original aircraft poses even if later alignment refines them. Unsupported timing/pose prevents quantitative use; interrupted packages remain marked incomplete.

Use LiDAR beam directions, acquisition-time pose, sensor-to-body lever arms/rotations, and versioned camera intrinsics/distortion/extrinsics to place measurements in a defined local frame. Geometry uses surrounding pavement as a local reference for raised areas, depressions, steps, and rise-over-run gradients; a road's normal slope is not itself a defect. Image candidates remain available without geometry. Associate branches only where timing, pose, coverage and calibration support it; separately report image-only and jointly supported results.

Earlier-survey change detection requires common-frame registration, overlap and uncertainty checks. Missing comparable coverage means unavailable comparison, not unchanged pavement. S3 and PC1 remain separate acceptance tests; neither ordinary GNSS nor the approximate mapping preference establishes final surface accuracy.

## Deployment, pose, and optional fusion

Processing runs **after collection**, preserving recorder capacity. **Laptop/workstation versus cloud execution remains undecided**; hosted reporting is selected independently. Inventory actual compute/storage/backup, measure runtime and 6–10 GB/run input demand, and price any cloud transfers/services.

Recorded MAVLink poses are original evidence. Overlapping images with GPS/LiDAR/control support are candidates for refinement; measured ground poses/surveyed references support calibration/demo checks. A known launch coordinate alone does not establish scale/orientation/geographic accuracy. Calibration controls and scored checkpoints remain separate.

The [November 3 RGB/depth proposal](rgb-depth-fusion-proposal.md) remains an **optional experimental branch**, with representation/model and training resources unselected (D-011/Q-16). It must retain independent geometry/image paths and observed-versus-estimated depth provenance. No learned fusion performance is assumed.

## Handoff and verification

Send findings/evidence/quality warnings to RD's ingestion API. Use valid geographic GeoJSON geometry only when registration supports it; keep metric local XYZ and frame/datum/transform separately identified (IF-16/Q-20). Preserve source/configuration/software/calibration IDs, units, measurement uncertainty, and image/scan links through reruns and reports.

Ground-demo P1 permits measured or post-processed poses. Its ≥10 independent checkpoint bounds do not establish every camera-center position, S3 accuracy, or flight performance. Complete independent timing/projection/height/centroid and held-out detection checks before quantitative claims. Historical leads: SRC-006/007/013/025/026/029.

## Shared design records

Maintain one owning row per component in [the BOM](../../procurement/bom.csv), exact connections in [interfaces](../../integration/interfaces.csv), and affected [power](../../integration/power-budget.csv), [mass/fit](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), [verification](../../verification/plan.md), and [decisions](../../decisions/decision-log.md). Design selection is not purchase authorization or test evidence. Blank installed/price values remain unknown.

Current source: [SRC-034 final approach](../../references/new-evidence/2026-11-16-final-approach/PaveWatch_Approach_Final.docx), [readable text SRC-035](../../references/new-evidence/2026-11-16-final-approach/approach-text.txt), and [reconciliation](../../references/new-evidence/2026-11-16-final-approach.md). Earlier source IDs resolve through [the source index](../../references/source-index.md).
