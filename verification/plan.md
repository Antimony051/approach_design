# Verification planning

Updated November 16, 2026 for PW-APPROACH-01 / SRC-034. No tests have been executed by this documentation update. The final approach reports Pro receipt/Ethernet streaming, but supplies no attributable acceptance records; all matrix results remain NOT_RUN. [requirements-matrix.csv](requirements-matrix.csv) tracks intended evidence, not pass results. Use the final requirements extract plus the current demo rubric and detailed ground plan in references; those sources retain sample counts and scoring rules.

## Design review evidence

Check exact component revisions/kit contents, firmware support, all port/connector pin assignments, voltage/current bounds, shared bus demand, mass/CG, actual installed dimensions/clearance, delivered costs, and owned/supplied equipment. Documentation checks establish on-paper compatibility only. Resolve missing evidence in procurement/compatibility.csv rather than marking a physical pass.

## Final approach qualification checks

- **Flight feasibility:** reproduce the [energy screen](../integration/flight-energy-screen.md), obtain matched X2216 880 KV / MR10×4.5 / 4S thrust-current data, and calibrate usable battery energy with actual installed mass. Source ~8.5 min fails the ≥10 min screening target; no requirement is relaxed. Reconcile planned 0.25–1 m/s with FP2's 1–2 m/s condition before claiming a flight pass.
- **Capture/storage:** inventory the received Pro and supported profile; test conditional ~50 Hz/0.25°–0.33° without assuming availability. Benchmark Pi4/Camera3 11.9 MP JPEG at 3 fps, ≤1 ms exposure/locked focus, and the actual Extreme128GB/USB3 reader under concurrent LiDAR/pose/health capture for ≥10 min. Measure write/encode rates, queues/drops, actual package size/free space, power/thermal limits, mechanical retention, and power-loss recovery. The 9–15 MB/s and 6–10 GB/run source figures are estimates, not acceptance evidence.
- **Timing/quality:** verify proposed LiDAR PTP/NTP and camera native timestamps against independent events, including beam/readout phase and drift; preserve the ≤20 ms bound and uncertainty. Validate blur/rolling-shutter handling, usable image detail and actual sampling at the selected envelope. A published benchmark or typical 20 mm sensor error is not a system pass.
- **Alerts/communications:** inject sensor/pose/storage faults and recorder-heartbeat loss through the actual recorder→PX4→RP1/ELRS→Pocket bridge (COMP-19), and test the separate laptop MAVLink status path. Measure source-to-display latency, stale/reconnect behavior, and simultaneous RC/handset-telemetry loss. Verify firmware/protocol/display support before assuming a Lua script works. Keep laptop telemetry loss distinct from the shared RC/handset failure.
- **Reporting:** exercise hosted ingestion validation/rejection/retry/duplicate handling, evidence links/units/versions, PostgreSQL/PostGIS records, dashboard filters/map/detail and PDF. Verify gap/partial-run/invalid-pose/alignment/missing-geometry warnings persist. Separate metric local coordinates from geographic GeoJSON; unknown registration must not produce an apparently precise map point. Test local fallback and delayed upload without blocking onboard capture/export. Processing execution location remains open.
- **Cost/fit:** reconcile source estimates with exact BOM, both budget ceilings, fabrication/service costs and available funds. Confirm dimensioned CF/PA6-CF structure, common plate rigidity/isolation, cable/ribbon bends, retained reader/card, PETG/ASA airflow, non-magnetic mast, installed mass/CG and landing/prop/optical clearance. Reserved envelopes and source payload estimates are not physical passes.

These are qualification tasks derived from the final approach, not additional numerical requirement approvals. The [source note](../references/new-evidence/2026-11-16-final-approach.md) and Q-01–20 track unresolved evidence.

## Ground commissioning and Capstone I

SRC-006/SRC-007 define future tests for three workstreams. Actual hardware needs include a compatible sensor supply/cables, camera, recorder/storage, approximately 8 m horizontal target space, stand/manual carriage, independent range/pose references, known geometry/image targets, and an independently timed transition fixture. Put unavailable tools in the BOM; do not assume borrowed equipment is assigned.

- A1–A3: real concurrent ≥10 min sensor recording, five 2 s injected gaps per stream, timing checks at start/middle/end with ≥3 events at each stage and uncertainty within the 20 ms bound, and 9/10 range observations within 60 mm at each of 5, 6.5, 8 m.
- D1–D3: ≥300 updates per field over ≥10 min, ≥90% source-to-display latency ≤4 s; all stream-gap cases; five sensor-loss and ten invalid-pose cases. Explicitly label emulated battery/mode and local-link conditions.
- P1–P4: real scans/overlapping images from ≥3 ground positions with measured or post-processed poses; ≥10 independent checkpoints, ≥90% jointly within X/Y 1 m and Z 0.2 m; held-out geometry/visible-class targets; three distinct packages of ≥1,000,000,000 actual recorded bytes, each exported within 30 min with full file/hash integrity.

Control points used for calibration/alignment are separate from evaluation checkpoints. Measured ground poses do not demonstrate an image pose estimator; P1 checkpoint bounds do not demonstrate every camera position's accuracy or S3. Saved evidence is not presumed approved as a substitute for a live test. All current rubric checks are proposed acceptance checks.

## Full integrated and airborne evaluation

### Optional RGB/depth processing checks — November 3 (D-011)

The [PC fusion proposal](../subsystems/05-data-processing-change-detection/rgb-depth-fusion-proposal.md) adds optional future evaluation details alongside the final approach's independent geometry/image branches for S2/S3/S5/S6 and PC1/PC2; it does not replace acceptance targets or establish a pass. Check projection against independent physical targets, coverage at the selected speed/height/mode, scan/exposure motion compensation, depth units/frame, and numerical preservation. Inject missing depth, wrong timing, calibration errors, invalid pose, occlusion, and interrupted processing; verify warnings, RGB-only fallback, and retained raw evidence. Keep observed and estimated depth distinguishable through RD1 reports.

Compare RGB-only, geometry-only, and fused models on identical held-out site/defect/sequence groups; keep neighboring frames, repeated views, crops, and augmentations within their original group. Report per-class precision/recall, applicable geometry height/centroid errors, coverage, nuisance false positives, and IoU where segmentation labels exist. Evaluate synthetic/public inputs separately from real project data. Learned depth completion, if introduced, needs independent geometric error checks before quantitative use. No minimum fusion improvement or new gradient-error limit is implied.

### Supervised interruption checks — October 29 planning additions

The [supervised mission design](../subsystems/04-ground-control-communications/supervised-mission-operation.md) adds the following future checks. Map historical ArduPilot examples to the selected PX4 stack. Numeric limits, exact modes, proximity hardware, and independent references remain to be selected; these checks do not replace FP3 or other existing acceptance targets.

- Proximity event interrupts mission progression and requests stopping; measure event-to-response time, loaded stopping distance, residual motion, clearance, and achieved hold. Verify each applicable mode and failure if position is invalid. No aircraft motion toward real obstacles is authorized merely by this documentation.
- Pilot takeover is visible and acknowledged; neutral sticks, sensor clearing, and telemetry reconnect do not restart the mission. Confirm an explicit resume and selected target; reject stale/duplicate requests.
- Rejoin after a detour does not blindly return to an obstructed waypoint or rewind through the obstacle. Test waypoint/altitude/heading/acquisition-command effects and wrong-target selection in simulation first.
- Skipped sections and early ending preserve recordings and produce partial-coverage/outcome records. Ending a survey does not command airborne disarming; return/landing is checked separately.
- Test sensing blind areas, stale/missing/false sensor reports, mode changes, positioning loss, RC/GCS loss, combined failures, and protection priorities. Evaluate vertical coverage and return-path obstruction where relevant.
- Distinguish attitude stabilization from position holding in estimator-loss checks. Do not pass an IMU-only hover claim based on a level aircraft. Reassess energy/reserve after detours and prolonged holds.

Bench/simulation evidence demonstrates software behavior only; real sensor coverage and loaded flight performance need separate controlled tests and independent measurements.

The October 28 [GC workflow review](../subsystems/04-ground-control-communications/operational-gap-review.md) adds proposed bench/simulation scenarios for mission identity/readback, changed launch position, reboot, duplicate commands, recording readiness, stale/replayed telemetry, link/recorder loss, and interrupted data transfers. They are future checks, not executed tests or new numeric acceptance criteria. Define the user's provisional mapping-reference accuracy convention before evaluating it; verify flight navigation, acquisition-time pose, and final findings separately.

Final evaluation still needs loaded flight duration/energy in three authorized flights; five route/height passes; takeover latency; independent roll/pitch reference using the corrected 5° bound; motion-reference timing; sensor performance under representative motion/lighting; actual site command-link tests; and the complete S2/S3/S5 evaluation. Unloaded manufacturer hover figures, synthetic/replay tests, or static sensor ranges cannot establish those results.

For every run save configuration/revisions, exact input provenance, raw data, reference uncertainty, calibration, commands/software version, denominators, injected faults, residuals/errors, pass/fail rule, output manifests/hashes, and failures/recovery. Keep dataset tuning separate from scored cases. A changed build may require repeated fit, power, timing, and calibration checks.
