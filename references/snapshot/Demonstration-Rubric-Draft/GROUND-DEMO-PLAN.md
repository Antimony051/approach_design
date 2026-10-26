# PaveWatch — Capstone I ground demonstration plan

This is the team's execution guide. The two-page `PaveWatch_Demonstration_Rubric.pdf` is the submission document. The rubric defines future acceptance checks; it does not record completed tests or passing results.

## Demonstration scope

Demonstrate Sensor Payload & Data Acquisition (SA), Data Processing & Change Detection (PC), and Diagnostics & Telemetry (DT) using the real applications and a ground-mounted payload. An assembled aircraft, working propulsion, flight controller, GNSS receiver, and flight authorization are not prerequisites for these checks.

Use a laptop as the recorder if the planned payload computer is unavailable. Use a compatible external SSD as payload storage. Poses can be measured stand positions/orientations or estimates obtained afterward from overlapping images with supporting references. Mark every pose as measured, estimated, emulated, or unavailable, and retain its coordinate convention. A local connection is sufficient for the operator display; long-range radio performance is outside this demonstration.

Live LiDAR/camera acquisition, physical range checks, and physical timestamp alignment still require the real sensors, compatible power, and appropriate interfaces. Replay supports processing, diagnostics, and repeatability; it does not substitute for evidence that live acquisition or timing works. A sensor delivery problem therefore remains a dependency, even though aircraft completion does not.

## Team responsibilities

| Team member | Work to return for Shisir's review |
| --- | --- |
| Abhinav Dhakal | A1–A3: sensor commissioning, recording configuration, timing experiment, range measurements, raw data, and acquisition results. |
| Aalok Uprety | P1–P4: coordinate transforms, frozen processing pipeline, held-out evaluation, error tables, and verified export results. |
| Pritam Adhikari | Implement and run D1–D3 with Shisir's review: local status transport, status display, latency logging, and controlled stream/pose faults. |
| Ankit Dhakal | Ground stand/carriage, measured poses and target layout, power/interface checks, and independently recorded physical references. Support A3 and P1/P2 without depending on aircraft assembly. |
| Saugat Karki | Dataset manifest, ground-truth labels and evidence packaging, integrity manifests, result display, and rehearsal records. Support P3/P4 and diagnostics evidence. |
| Shisir Baral | Overall reviewer; retain DT subsystem accountability, acceptance of test methods, scope and architecture decisions, budget/purchase decisions, and final document release. |

The three rubric owners remain Abhinav (SA), Aalok (PC), and Shisir (DT). Support assignments do not change subsystem ownership. All six members attend the demonstration, as required by the template.

## Minimum equipment and software

- Delivered picoScan, its correct cables/interfaces, and a manufacturer-compatible power supply.
- Camera, local recorder computer, storage, and operator display. One laptop can host both recorder and display as separate applications with a local connection.
- Stable stand and a manually indexed carriage or repeatable marked positions. Use a measured sweep to move the 2D scan plane across a surface; one stationary 2D profile is not a complete 3D surface survey.
- An approximately 8 m horizontal test space; matte targets; tape/ruler or a better reference; fixtures with measurable 100–150 mm offsets and at least 0.5 × 0.5 m extent.
- An independently timed target-transition fixture and event logger for A2. Its timing uncertainty must be measured and small enough to assess the 20 ms bound.
- A local status transport/display, fault-injection and replay tools, the processing application, an export tool, and file-hash checking.

The power supply and cables must match the delivered sensor. The owned 7.4 V packs are not automatically a suitable direct sensor supply. No propulsion is needed for this setup.

## Freeze the test definition before collecting scored data

Record the sensor variant, camera model and mode, frame/scan rates, timestamp semantics, computer, storage, software revision, calibration, frames, and units. Declare the accepted image classes as **crack-like** and **depression**, consistent with the current requirements. Record what counts as an independently observed target and how detections match labels.

Keep calibration/development data separate from scored data. Freeze detector settings before scoring. Do not tune on the held-out test set. Repeat a failed test after a documented change with a new run ID; preserve the failed run and the reason for the change.

For each weighted item, award its listed weight only when all its stated conditions pass. Leave `% Earned` blank in the draft. The three subsystem totals are 20% each; the template's fixed demonstration-readiness section is 40%, totaling 100%.

## A1 — Concurrent recording and continuity

1. Run both physical sensors and the normal recorder for at least 600 s. Save original data, timestamps, configuration, and a session manifest. Both streams must span the session; an empty file is not evidence of acquisition.
2. While recording, suppress only the input to the recorder for five separate 2 s intervals per stream. Do not deliberately interrupt the other stream. Log injection start/end on the same clock as the monitor, or retain a measured clock mapping.
3. Replay the recording through the normal inspection path. Verify both stream durations and match all ten introduced gaps to the gap records. Report all other observed gaps as well.
4. Retain sample counts and configured rates. Do not treat a file's first/last timestamps alone as proof of continuous useful data.

Evidence: raw stream files, session manifest, rate/count summary, injection log, and gap report. These same recordings can support D2 without running a separate physical experiment.

## A2 — Timestamp alignment

Use a moving matte target or edge that changes the LiDAR range and is visible to the camera. Independently log the relevant physical transition, for example with a separate event sensor/logger. Account for any offset between the independently detected transition and the transition observed by each sensor. The geometry and timing uncertainty of the fixture are part of the test.

Perform at least three transitions near the beginning, three near the middle, and three near the end of the same ≥600 s session. Use native scan/sample and image exposure timing where available. If a correction is necessary, derive it from separate calibration events; do not independently re-fit each scored event or stage. Test the correction across the whole session so drift is visible.

For each scored event, report the corrected camera-to-reference, LiDAR-to-reference, and camera-to-LiDAR residual. Include the uncertainty of the event time, exposure timing, scan phase, and clock mapping. The conservative bound is `abs(residual) + uncertainty ≤20 ms` for every evaluated comparison. Maintain the measured static pose/reference timeline for this run. The test does not establish aircraft motion-reference performance.

Computer receipt times alone cannot establish capture-time alignment. Check the delivered sensors' timing access and the camera mode early. If uncertainty exceeds the bound, record that limitation and adjust the timing method or camera configuration before the demonstration. A shorter demonstration or a passing processing result does not resolve an unmeasured timing error.

Evidence: fixture description and photograph, event log, timestamp definitions, calibration/correction, at least nine scored events, residual/uncertainty table, and drift plot.

## A3 — Physical range accuracy

Measure reference distances from the sensor's documented measurement origin to a matte target at 5, 6.5, and 8 m horizontally. No overhead mount or flight at these heights is needed. Record reference uncertainty and target geometry; ensure the scan plane intersects the target.

At each distance, acquire ten separate observations using a fixed, declared sampling rule. Reposition/reacquire between observations rather than selecting the ten best returns. Preserve the individual readings, rather than using averaging to hide failed observations. Calculate `abs(measured range − reference range)`. At least nine of ten must be ≤60 mm **at each distance**. Report reference uncertainty alongside the errors.

Evidence: target layout, references, 30 observations, per-distance pass counts, and raw returns. This is a static ground range test; moving-aircraft performance is assessed later.

## D1 — Status delivery

Use a ≥600 s run with at least 300 updates **per field**: battery, acquisition, storage, and mode. Battery and mode can come from an explicitly labeled, timestamped test publisher. Acquisition and storage status come from the actual recorder. Change test battery/mode values during the run so the receiver cannot pass by displaying one constant value.

Use one monotonic clock when processes share a computer, or retain a measured mapping between source and receiver clocks. Log source event ID/time and display-update ID/time. Measure until the new value reaches the operator display, rather than stopping at transport receipt. Count missing display updates as failures, not as excluded samples. At least 90% of generated updates must reach the display within 4 s, assessed separately for each field. Retain total, displayed, timely, late, and missing counts.

Evidence: source/display logs, clock mapping if applicable, display recording/screenshots, per-field latency results, and input-source labels. Emulated battery/mode data demonstrates the diagnostics path, not electrical measurement accuracy or real flight-state reporting.

## D2/D3 — Gaps, sensor loss, and invalid pose

For D2, replay A1 through the same normal stream-monitor code used live. Match each of the five LiDAR and five camera gap intervals to the injection log. The warning must identify the correct stream and interval. Report false alerts separately; do not hide extra faults observed during acquisition.

For D3, perform one real sensor disconnect while the monitor is running and four further independent losses by stopping replay input. Restore input between cases. Include loss of both sensor types across the five cases. Retain each loss, warning, recovery, and affected data interval.

For the ten pose cases, use a declared set such as four absent references, three stale references, and three malformed/invalid references. Record the stale-age rule and pose-validity checks before the test. Process and export the affected records. Each invalid record must remain explicitly invalid; substituted zeros must not silently become valid coordinates. Recovery must permit later valid data to be processed again.

Evidence: fault manifest with all 15 cases, warning log, exported validity flags, and recovery observations. P1 can reuse these ten pose cases.

## P1 — Image location and coordinate transforms

Collect overlapping images and actual LiDAR scans from at least three ground capture positions, using more images/positions as necessary for reconstruction. Two pose sources are accepted: independently measured stand/carriage poses, or poses estimated offline from the image sequence with supporting GPS, LiDAR, and ground-control references where available. The post-processing path reflects the user's approach in `hardware_planning/post_processing_for_location.md`; it does not require a flying aircraft.

Use one local metric coordinate system, such as X/Y along the test area and Z upward from a defined reference level. Document the origin, axes, scale, camera calibration, camera-to-LiDAR mounting transform, and time association. Save each image's ID/timestamp, capture X/Y/Z, orientation, pose source, and validity. Transform associated LiDAR measurements into that same frame. Z is a coordinate relative to the reference level; it is not automatically the instantaneous height above uneven ground.

For the image-based path, estimate relative camera positions/orientations from overlapping images, then constrain or align the reconstruction using independent control information. A launch coordinate can set an origin, but by itself does not resolve image-only reconstruction scale and orientation or establish its accuracy. Available GNSS, measured distances/control points, and appropriately calibrated LiDAR observations can provide additional constraints; their usefulness must be demonstrated, not assumed. There is no centimeter-accuracy promise in P1. LiDAR range is not automatically vertical camera height: mounting offsets, viewing direction, orientation, and the observed surface matter.

Keep ground **control points** used to establish scale/alignment separate from ground **checkpoints** used to score accuracy. Compare at least ten independent physical checkpoints withheld from camera calibration, pose estimation/bundle adjustment, and frame alignment. They may be reconstructed as ordinary scene features, but their measured reference coordinates must not be supplied to the estimator. Use observations spanning at least three capture positions. For each checkpoint record X/Y/Z reference, X/Y/Z estimate, and errors. A checkpoint passes only when all three bounds hold: `|ex| ≤1 m`, `|ey| ≤1 m`, `|ez| ≤0.2 m`. At least 90% must pass jointly: nine of ten if exactly ten are evaluated. Missing or invalid reconstructed checkpoints count as failures. Then verify all ten deliberately invalid-reference cases remain flagged in outputs.

These thresholds measure reconstructed **ground-point coordinates**. They do not directly establish that every camera capture position has the same accuracy. If reporting camera-position accuracy, compare estimated camera centers against separate measured capture positions and report those errors independently. Using measured poses exercises coordinate transformation and association; it does not demonstrate that the image-based pose estimator works. Label the path actually tested.

The looser P1 coordinate bounds do not prove P2's tighter height/centroid limits. Evaluate both separately. A single profile or perfect synthetic coordinates are insufficient evidence of physical reconstruction.

Method references: [COLMAP georegistration](https://colmap.github.io/faq.html#geo-registration) describes alignment of an image reconstruction to reference coordinates; [OpenDroneMap map accuracy](https://docs.opendronemap.org/map-accuracy/) distinguishes relative reconstruction accuracy from absolute geographic accuracy; [ground control guidance](https://docs.opendronemap.org/gcp/) describes control-based georeferencing. These references support the method, not a prediction that this project's hardware will meet its targets.

## P2 — Geometric detection and measurement

Use at least ten scored qualifying target instances, including raised and recessed surfaces, plus at least ten negative regions. Each scored target has a 100–150 mm measured height/depth and a footprint of at least 0.5 × 0.5 m. A recessed fixture can be formed by building a surrounding reference surface above a lower panel; excavation is unnecessary. Keep independently checked reference height uncertainty ≤10 mm.

Acquire LiDAR coverage with a measured manual sweep or indexed positions and calibrated poses. Separate fixture placements/scenes and retain sample IDs. Scan coverage, pose spacing, and sensor orientation must support the surface being measured. Fix one-to-one label matching before evaluation; count duplicate detections as false positives. Use ground-truth spatial regions to associate targets, and assess measurement errors after matching rather than using the accuracy threshold to discard bad measurements.

- `recall = TP / (TP + FN) ≥90%`.
- `precision = TP / (TP + FP) ≥80%`.
- Of the true-positive detections, at least 90% must jointly satisfy `|height error| ≤60 mm` and horizontal centroid error `≤0.5 m`.
- Missing/invalid measurements on detected targets fail the joint measurement check. Undetected targets remain false negatives in recall. Zero detections cannot pass.

Retain separate height and location errors, plus the joint count. Also scan measured inclined surfaces and report estimated gradients, reference gradients, and errors. The current requirements do not define a numerical gradient-accuracy threshold; the rubric requires the gradient report without inventing one.

This is a controlled ground-scene evaluation. It does not establish performance from a vehicle moving at 1–2 m/s or at 5–8 m above pavement.

## P3 — Visible-defect detection

Freeze a labeled ground-image dataset with at least ten positive instances per class, crack-like and depression, plus at least ten nuisance-only regions. Record physical dimensions or reference scale for size-qualified positives: crack-like width ≥20 mm and length ≥0.2 m; depression footprint ≥0.5 × 0.5 m. Include shadows, pavement seams, marks, and texture as appropriate negative examples. Keep repeat views of the same physical defect together when separating development and evaluation data.

Define region/object matching before scoring. Evaluate the actual detector, without supplying the ground-truth labels as detector inputs or manually replacing its predictions. Report TP, FP, FN, precision, and recall separately for each class, including false detections in nuisance-only regions. Both precision and recall must be ≥80% for each class. Zero predictions or zero qualifying labeled examples cannot pass. A previous survey is unnecessary.

Ground camera images are accepted. LiDAR-camera fusion is not a separate graded condition in this draft; image-only results satisfy P3. Report combined results separately if available, without replacing the required per-class evaluation.

## P4 — Survey export

Prepare three survey packages, each containing at least 1,000,000,000 bytes of actual recorded survey data. Collect longer or additional ground recordings as necessary; do not inflate packages using padding, synthetic filler, or duplicate files counted as new survey observations. Keep source recordings unchanged. Distinct packages can come from separate portions/sessions of the same ground campaign; they do not require three flights.

Place source packages on the payload recording device/storage. Export to a separate destination directory on the operator laptop. An external SSD used as payload storage is acceptable. When one computer serves both roles, use distinct source and destination storage devices and document this arrangement. An in-place rename or a second pointer to the source files is not a transfer.

Start timing at the export command and stop after the destination write completes. Each transfer must take ≤30 min. Compare complete source/destination file lists, per-file byte counts, and SHA-256 hashes. Include the integrity-check time in the saved report; the three recorded full runs can be reviewed at the demonstration rather than requiring a possible 90 min of live transfer time.

## Evidence package

Organize by run ID. Retain:

- Configuration, software revision, calibration, sensor/compute/storage identities, and input provenance.
- Raw LiDAR/images/pose/status logs, independent references, labels, and injection/event logs.
- Reproducible commands or scripts and dependency/version information.
- Per-item measured values, denominators, pass/fail, plots, and failure explanations.
- Export manifests, hashes, transfer timings, and representative output findings.

Label real measurements, recorded replay, measured static poses, and emulated status fields at their source. Save evidence while testing; do not reconstruct passing values from memory. Include failed and recovered runs. Follow the supplied test-report guide for the later report's methods, data, results, and interpretation.

## Demonstration sequence

Prepare full-duration recordings and all three transfer trials beforehand. The following is a suggested rehearsal sequence, not an instructor-provided slot length:

1. Show the mounted sensors, connections, recorder, operator display, and frozen test configuration.
2. Start a live ≥10 min acquisition/status session. During the run, demonstrate a physical sensor disconnect/recovery and operator warnings.
3. While that run continues, replay the labeled gap/pose cases and show their flags in exported records.
4. Process the frozen geometry and image datasets. Show reference overlays, TP/FP/FN counts, measurement errors, and per-class results.
5. Demonstrate one export workflow and open the three complete timed export reports and integrity results.
6. Close the live recording, inspect both stream durations, and show status-latency counts. Open the saved timing/range evidence and the item-by-item results.

Keep the full data and executable workflow available. If the assigned slot is shorter than the required run durations, arrange the live/saved-evidence presentation with the instructor before the final rubric. This draft does not assert that saved evidence has already been approved as a substitute for a timed live test.

## Relationship to the project requirements

| Rubric checks | Requirements exercised | Boundary of the demonstration |
| --- | --- | --- |
| A1 | SA1, S4 | Real ground recording; no loaded-flight endurance claim. |
| A2 | SA2 timing objective | Physical sensor alignment to a measured reference timeline; dynamic aircraft pose synchronization remains a later integration check. |
| A3 | SA3 numerical range bound | Static horizontal targets at the three specified ranges; representative moving-aircraft conditions remain later work. |
| D1 | DT1 latency objective | Emulated battery/mode sources and local transport; actual battery sensing, flight-mode integration, and site-radio operation remain later work. |
| D2/D3 | DT2/DT3 | Real sensor-loss behavior and replay of explicit gap/invalid-reference cases. |
| P1 | PC1, with explicit image-to-pose association | Ground scans/images with measured or post-processed poses; independently held-out ground checkpoints. Camera-position accuracy and global geographic accuracy require separate validation. |
| P2 | PC2, S2/S3 numerical targets | Controlled geometry/gradient evaluation; full survey envelope and broader scene diversity remain later work. |
| P3 | PC2, S5 | Two-class held-out ground imagery; airborne imagery and combined-sensor performance remain later work. |
| P4 | PC3 | Real payload-storage export; a laptop may host the recorder, so onboard-computer integration remains later work if substituted. |

Flight endurance/energy reserve, route following, attitude accuracy, operator takeover, long-range command links, and the full airborne operating envelope are not graded here. The project requirements remain unchanged; this rubric specifies the Capstone I test conditions.

## Review before final submission

The main technical feasibility item is A2: verify timestamp access and the event fixture early enough to make the 20 ms comparison meaningful. Sensor variant, exact camera/compute choices, test-space availability, and the instructor's allocated demonstration duration also need to be established during preparation. None requires a flying aircraft.

Shisir reviews results and scope changes before release. The final rubric is due November 20 according to the saved course schedule; course feedback on this draft should be incorporated before that release.
