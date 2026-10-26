### 12. Development and demonstration sequence

The proposed sequence spans 16 development weeks. Calendar dates will be aligned with hardware delivery and the academic schedule. Software work can begin before the sensor arrives; outdoor milestones depend on successful preceding tests.

| Phase | Indicative weeks | Work and exit evidence |
|---|---|---|
| Contracts and design | 1–2 | Freeze data schemas, frames, interfaces, BOM, mechanical layout and test definitions |
| Software demonstration | 3–5 | Synthetic baseline/current replay, public-data adapters, cloud ingest and preliminary report |
| Sensor commissioning | 6–7 | Identify supplied variant; capture real packets; characterize camera timing and fixed-target repeatability |
| Payload integration | 8–9 | Complete power, storage, mass, retention and calibration tests; verify recovery from interrupted capture |
| Controlled movement | 10–11 | Compare stationary and moving profiles against independent targets; establish operating limits |
| Flight integration | 12–13 | Demonstrate manual recovery, accepted survey coverage and repeat passes with the complete payload |
| Field evaluation | 14–15 | Held-out geometric and fusion tests; baseline/current comparison; error and false-positive analysis |
| Demonstration release | 16 | Reproducible report, architecture/BOM revision, documented limitations and final demonstration |

Work will be organized into flight/mechanical integration, sensing/calibration, acquisition/telemetry, processing/fusion, cloud/reporting, and verification/data stewardship. The six-student team will assign workstream owners and review shared interfaces together. Verification will include cross-review so the person preparing reference measurements does not silently reuse evaluation targets to tune alignment.

### 13. Evidence before hardware delivery

An analytic pavement fixture will generate unchanged and changed surfaces with declared step heights, depression dimensions, slopes, and sampling conditions. A simulated transverse scanner will produce timestamped profiles rather than an ideal dense surface alone. Experiments will inject pose errors, timing offsets, missing profiles, and registration errors. Ground-truth parameters will be saved independently of the processing output.

UAV-PDD2023 is the planned aerial-image source for testing image ingestion and distress-detection evaluation. The Stereo Pothole Datasets provide paired imagery and stereo-derived geometry for an initial fusion experiment. Their viewpoints and sensor physics differ from PaveWatch; stereo depth will be labeled accordingly. Synthetic profiles and unrelated aerial images will not be presented as a physically paired survey. [9, 10]

Every dataset will receive a source/version record, license review, checksum, and documented evaluation split before use. The software demonstration will show that the processing and reporting workflow operates on declared inputs. It will not establish picoScan150 flight performance.

### 14. Verification and acceptance

All thresholds below are proposed engineering gates. Tests that establish measurement limits will report observed results rather than replace missing evidence with a target value.

| Test | Proposed gate or evaluation |
|---|---|
| Sustained acquisition | 30-minute simultaneous sensor/image/pose bench recording; at least 99% expected profiles and frames; every gap identified; no unrecoverable files |
| Storage headroom | Maintain at least 20% free space; verify write performance above the measured peak acquisition demand |
| Replay integrity | All transferred file hashes match; decoded sequences and counts agree between live and replay paths |
| Timing | Measure offset and drift across a full session; accept only when timing-induced error fits the selected geometric/fusion error allowance |
| Camera quality | Test known detail targets and moving targets; report blur, distortion and usable ground sampling at each capture mode |
| Calibration | Independent target reprojection and profile residuals; recheck after remounting and representative vibration |
| Known geometry | Fixture matrix spanning approximately 20–100 mm height change and 0.2–1 m lateral extent; report error, detection probability and missed features by size |
| Unchanged surface | Repeat at least five passes; quantify apparent change, spatial repeatability and false candidates |
| Survey coverage | At least 90% of the planned evaluation area has accepted common support; map missing regions explicitly |
| Registration | Evaluate check targets excluded from alignment; reject quantitative comparisons whose residuals exceed the target measurement allowance |
| Fusion benefit | Compare image-only and image-plus-geometry precision/recall and localization on identical held-out groups; report uncertainty and failure cases |
| Failure recovery | Exercise interrupted upload, worker retry, full storage and power interruption; no silent loss or replacement of accepted results |
| Reporting | Every released candidate traces to source evidence, calibration, processing run and baseline; flags survive all exports |

The 20 mm fixture is a characterization point, not a promised flight detection capability. If the airborne system only supports larger changes, the demonstrated scope and report labels will reflect that result.

For each field run, the team will record surface condition, lighting, wind, height, speed, sensor settings, exposure, and accepted coverage. Results will include distributions and sample counts rather than a single favorable example. Processing duration and upload/storage volume will be measured alongside detection performance.

### 15. Risks and alternative demonstration paths

| Risk | Planned response |
|---|---|
| Moving 2D profiles cannot support accurate surface reconstruction | Isolate pose/timing errors with a controlled moving rig; demonstrate valid cross-section comparisons while improving motion estimation |
| Ordinary GNSS does not align repeated visits | Use site markers and stable geometry; test independent residuals; consider improved positioning only when evidence supports the need |
| Rolling shutter or vibration prevents fusion | Reduce speed and validate camera timing; revise mount or evaluate a global-shutter camera |
| Dark, wet or oblique pavement causes sparse returns | Characterize signal/echo behavior; adjust sector and operating envelope; publish coverage masks |
| Payload mass, power or mounting is unsuitable | Revise installation before flight; use measured current and vibration to set the operating envelope |
| Sensor variant lacks optional timing/IMU capabilities | Preserve device/host clocks and measure software offsets; maintain raw Ethernet acquisition |
| Cloud upload or processing is interrupted | Resume verified transfers, retry jobs safely and replay locally from retained evidence |
| Flight or sensor delivery is delayed | Continue synthetic/public-data work and controlled bench acquisition; label demonstration scope accurately |

The final project deliverables will include the integrated prototype, documented acquisition and cloud pipeline, repeatable survey procedure, evaluation dataset and provenance records, performance report, and maintenance-oriented interface. The final demonstration will identify which capabilities have passed controlled testing and which remain research work.
