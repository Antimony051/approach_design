# Verification planning

No tests have been executed by this workspace. [requirements-matrix.csv](requirements-matrix.csv) tracks intended evidence, not pass results. Use the final requirements extract plus the current demo rubric and detailed ground plan in references; those sources retain sample counts and scoring rules.

## Design review evidence

Check exact component revisions/kit contents, firmware support, all port/connector pin assignments, voltage/current bounds, shared bus demand, mass/CG, actual installed dimensions/clearance, delivered costs, and owned/supplied equipment. Documentation checks establish on-paper compatibility only. Resolve missing evidence in procurement/compatibility.csv rather than marking a physical pass.

## Ground commissioning and Capstone I

SRC-006/SRC-007 define future tests for three workstreams. Actual hardware needs include a compatible sensor supply/cables, camera, recorder/storage, approximately 8 m horizontal target space, stand/manual carriage, independent range/pose references, known geometry/image targets, and an independently timed transition fixture. Put unavailable tools in the BOM; do not assume borrowed equipment is assigned.

- A1–A3: real concurrent ≥10 min sensor recording, five 2 s injected gaps per stream, timing checks at start/middle/end with ≥3 events at each stage and uncertainty within the 20 ms bound, and 9/10 range observations within 60 mm at each of 5, 6.5, 8 m.
- D1–D3: ≥300 updates per field over ≥10 min, ≥90% source-to-display latency ≤4 s; all stream-gap cases; five sensor-loss and ten invalid-pose cases. Explicitly label emulated battery/mode and local-link conditions.
- P1–P4: real scans/overlapping images from ≥3 ground positions with measured or post-processed poses; ≥10 independent checkpoints, ≥90% jointly within X/Y 1 m and Z 0.2 m; held-out geometry/visible-class targets; three distinct packages of ≥1,000,000,000 actual recorded bytes, each exported within 30 min with full file/hash integrity.

Control points used for calibration/alignment are separate from evaluation checkpoints. Measured ground poses do not demonstrate an image pose estimator; P1 checkpoint bounds do not demonstrate every camera position's accuracy or S3. Saved evidence is not presumed approved as a substitute for a live test. All current rubric checks are proposed acceptance checks.

## Full integrated and airborne evaluation

Final evaluation still needs loaded flight duration/energy in three authorized flights; five route/height passes; takeover latency; independent roll/pitch reference using the corrected 5° bound; motion-reference timing; sensor performance under representative motion/lighting; actual site command-link tests; and the complete S2/S3/S5 evaluation. Unloaded manufacturer hover figures, synthetic/replay tests, or static sensor ranges cannot establish those results.

For every run save configuration/revisions, exact input provenance, raw data, reference uncertainty, calibration, commands/software version, denominators, injected faults, residuals/errors, pass/fail rule, output manifests/hashes, and failures/recovery. Keep dataset tuning separate from scored cases. A changed build may require repeated fit, power, timing, and calibration checks.
