# PaveWatch — Demonstration Rubric

PaveWatch — Capstone I ground demonstration. All graded checks use a stand/manual carriage, local recording, measured reference poses, and labeled replay; no flight is required. Live acquisition and range/timing checks use real sensors. Each item is pass/fail at its listed weight; saved full-run evidence and a live workflow are presented.

## Sensor Payload & Data Acquisition — Abhinav Dhakal

Requirements (20%):

- A1. Record LiDAR and camera streams concurrently for ≥10 min. Retain timestamps and identify every deliberately introduced gap >1 s. [8%]
- A2. Residual timing error between the two streams and the reference timeline is ≤20 ms at the start, middle, and end of that session, including drift and reference uncertainty. [6%]
- A3. At each of 5, 6.5, and 8 m, ≥9 of 10 independent matte-target range observations have absolute error ≤60 mm. [6%]

Demonstration setup:

- A1. Mount the real LiDAR and camera on a fixed stand or manual carriage. Record to local payload storage using a laptop or payload computer. Inspect both files; suppress each stream five times for 2 s and compare logged gaps with the injection log.
- A2. Use an independently timed target transition visible to both sensors, with ≥3 events at each session stage. Compare acquisition times after correction; every tested residual, with uncertainty, must meet the bound. Arrival timestamps alone do not establish alignment.
- A3. Place a measured target at each horizontal distance. Take 10 separate observations per distance; retain raw returns, reference measurements, and errors.

## Diagnostics & Telemetry — Shisir Baral

Requirements (20%):

- D1. Battery, acquisition, storage, and mode status reaches the operator within ≤4 s for ≥90% of ≥300 updates per field over ≥10 min. [8%]
- D2. Identify all five introduced gaps >1 s in each of the LiDAR and camera streams, with the affected stream and interval. [6%]
- D3. Flag all five sensor-loss and all ten missing/invalid-pose cases. Invalid references remain flagged in exported data. [6%]

Demonstration setup:

- D1. Run the real diagnostics application on a local link. Inject a timestamped battery/mode test feed and use actual acquisition/storage status. Use one clock or measured clock correction. Compute latency separately for each field; label emulated inputs.
- D2. Replay the A1 recording through the normal stream monitor. Match each reported interval against the injection log; report missed events and extra alerts separately.
- D3. Disconnect the live sensor once and inject four further losses via replay. Supply ten absent, stale, or malformed pose references. Inspect operator warnings and exported validity flags against all 15 cases.

## Data Processing & Change Detection — Aalok Uprety

Requirements (20%):

- P1. Assign each usable image a capture position/orientation and transform LiDAR measurements into the same local X/Y/Z frame using measured or post-processed poses. At ≥90% of ≥10 independent ground checkpoints, |X error| and |Y error| ≤1 m and |Z error| ≤0.2 m. Flag all ten invalid-reference cases. [5%]
- P2. On ≥10 qualifying geometric targets and ≥10 negative regions, achieve recall ≥90% and precision ≥80%. For ≥90% of detected targets, both height error ≤60 mm and centroid error ≤0.5 m. Report measured gradients. [5%]
- P3. For crack-like and depression image classes, achieve precision and recall ≥80% per class on ≥10 labeled positives per class and ≥10 nuisance-only regions. [5%]
- P4. Export three survey packages, each ≥1 GB, from payload storage to an operator laptop. Each transfer completes within ≤30 min with no missing or corrupted files. [5%]

Demonstration setup:

- P1. Collect overlapping images and LiDAR scans from ≥3 ground positions. Use measured poses or estimate them offline from images with available GPS, LiDAR and control references. Compare checkpoints withheld from calibration, pose estimation and alignment; inject ten invalid poses.
- P2. Use held-out measured raised/recessed fixtures or ground scenes, 100–150 mm in height/depth and ≥0.5 × 0.5 m in extent. Retain reference height uncertainty ≤10 mm. Use a manual measured sweep for surface coverage. Freeze detection settings and match each detection to at most one labeled target. Compute TP, FP, FN and joint measurement success; retain misses.
- P3. Run the image detector on a frozen, held-out ground-image set: crack-like targets ≥20 mm wide × 0.2 m long; depressions ≥0.5 × 0.5 m. Include nuisance-only images; retain labels and per-class counts. No earlier survey is required.
- P4. Time three separate exports of ≥1,000,000,000 actual recorded-data bytes each. Compare complete file lists, byte counts, and SHA-256 hashes. Saved full-run evidence accompanies the live workflow demonstration.

## Fixed course provisions

Demo |  All three high-risk subsystems are ready to demo at the time scheduled. Each requirement and corresponding demonstration setups written above have been attempted . [40 %]  | 40% | 
Total: | 100% | 

NOTE: All team members must be present. If a team member is not present for this demonstration. Their score shall be 0% while the other team members will receive the grade allocated in this rubric. This is acknowledged by the team and all team members upon submission.
