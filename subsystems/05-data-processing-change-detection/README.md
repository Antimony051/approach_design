# PC — Data Processing & Change Detection

Lead: **Aalok Uprety**. Charter support: **Shisir Baral**. Requirements: **PC1–PC3; S2, S3, S5, S6**.

## Required function

Transform referenced measurements into one documented frame, assess current-survey geometry and visible defects, preserve invalidity, and export inspectable results. Prior-survey comparison is optional.

## Existing direction and evidence

Existing research offers offline geometric reconstruction and image detection, with optional paired-fusion and repeat-survey experiments. Historical cloud-first and local-first plans disagree on deployment; neither selects required processing hardware today. The user proposed camera pose estimation after collection using overlapping imagery with GPS/LiDAR support (SRC-013); its numerical accuracy assurances are not validated.

Ground-demo P1 permits measured stand/carriage poses or post-processed poses. Its reference-point thresholds do not establish every camera-center position error, global centimeter accuracy, S3 surface accuracy, or moving-aircraft performance.

## Work for the design agent

- Specify required raw data, camera calibration, pose/time mapping, sensor transforms, units, quality flags, and retained uncertainty with SA/FP.
- Decide local processing workstation vs optional cloud path based on actual data volumes/software, including storage/transfer/backup hardware and recurring costs.
- Define offline camera-position estimation inputs if used: image overlap/modes, scale/orientation constraints, control references, and independent checkpoints.
- Select reference tools, geometry/gradient targets, stand/indexing equipment, visible-detail fixtures, and independent timing equipment with the physical owners.
- Define output/result contract with RD, export path with SA/GC, and measurable end-to-end checks. Do not treat a software choice as proof the capture hardware meets accuracy.

## Required design handoff

Use [the research template](../../templates/research-note.md) for options/evidence, then maintain the selected implementation here. Include exact parts and configuration, rationale, inputs/outputs, installed mass/power/dimensions where applicable, interfaces, failure behavior, assembly/calibration needs, verification, and open decisions. Mark the design status explicitly; the initial status is **implementation unresolved**.

Write purchasing lines into [the shared BOM](../../procurement/bom.csv); write connection details into [interfaces](../../integration/interfaces.csv). Update [power](../../integration/power-budget.csv), [fit/mass](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), and [decisions](../../decisions/decision-log.md) when this subsystem changes them. Cross-reference shared components instead of duplicating them.

## Starting references

- SRC-006: locate in [the source index](../../references/source-index.md).
- SRC-007: locate in [the source index](../../references/source-index.md).
- SRC-013: locate in [the source index](../../references/source-index.md).
- SRC-025: locate in [the source index](../../references/source-index.md).
- SRC-026: locate in [the source index](../../references/source-index.md).
- SRC-029: locate in [the source index](../../references/source-index.md).
