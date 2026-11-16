# Requirements carried into hardware design

Updated November 16, 2026. This is a working summary of SRC-002, with the user-confirmed FP4 correction from SRC-001. SRC-034 supplies the current implementation, not a silent amendment of acceptance criteria. Consult the original and its readable extract for exact wording, constraints, standards, and evaluation details. Numerical values are acceptance targets, not achieved performance. Ground-demo adaptations in SRC-006/SRC-007 do not replace final airborne requirements.

| ID | Required capability / bound | Hardware consequence |
| --- | --- | --- |
| S1 / FP1 | ≥10 min loaded flight with acquisition active; ≥20% calibrated usable energy remains; three authorized flights | Complete mass, propulsion, energy, and battery monitoring plan |
| S2 | 100–150 mm raised/depressed/step features in ≥0.5 × 0.5 m regions; recall ≥90%, precision ≥80%; report gradients | Range sampling, coverage, reference fixtures, independent evaluation |
| S3 | ≥90% of detected targets jointly meet absolute height error ≤60 mm and horizontal centroid error ≤0.5 m; reference height uncertainty ≤10 mm | Total pose/timing/range/calibration budget, not a sensor-only specification |
| S4 / SA1 | Concurrent range and image recording ≥10 min; identify gaps >1 s | Sustained recorder/storage operation and observable sequence loss |
| S5 | Per-class precision and recall ≥80%; crack-like targets ≥20 mm wide × 0.2 m long; depression-like regions ≥0.5 × 0.5 m | Actual lens, capture mode, exposure, height, and lighting must support usable imagery |
| S6 | Timestamped 3D position and orientation ≥10 min; associate every quantitatively used image/profile with acquisition-time pose; flag unusable references | Pose source, capture timing, clock mapping, frames, mounting transforms |
| FP2 | ≥90% straight-leg samples within 2 m horizontal route error and ±1 m commanded height at 5–8 m, 1–2 m/s; five passes | Navigation/control and independent route/height reference |
| FP3 | Mode changes within ≤1 s in 10/10 operator-takeover trials | RC/control path and acknowledgement measurement |
| FP4 | Roll and pitch absolute errors ≤5° for ≥90% independently evaluated samples, plus timestamped pose and conventions | User-resolved bound; source test's 1° is superseded; this does not prove S3 |
| SA2 | Residual timing offset between acquisition streams and motion reference ≤20 ms throughout ≥10 min, including drift | Timestamp/trigger/clock access and independent timing fixture |
| SA3 | ≥90% independently checked range observations within ≤60 mm; 5, 6.5, 8 m with ≥10 observations/condition | Physical references and test space; representative motion/lighting for final evaluation |
| DT1 | Battery/acquisition/storage/mode reaches display ≤4 s for ≥90% updates over ≥10 min; ≥300 updates per field in demo | Observable health source and end-to-display link |
| DT2–3 | Identify >1 s sensor-stream gaps, sensor loss, and invalid/missing pose | Fault detection, timestamps, persisted validity |
| GC1 | Define, transfer, verify ≥10-waypoint route within ≤10 min over five trials | Compatible GCS/controller and route readback |
| GC2 | Command acknowledgement ≤2 s for ≥90% commands; tests at 10, 50, 100 m with ≥100 commands per stated test setup | Site-link and measured acknowledgement plan |
| GC3 | Store up to 60 s stream data on link loss; send buffered stream before current stream after reconnect | Stream, rates, buffer location, and ordering unresolved; do not silently reinterpret or route stale safety commands |
| PC1 | Common frame; ≥90% independent reference points within ≤1 m X/Y and ≤0.2 m Z; flag invalid pose | Frame/pose contract and independent controls/checkpoints; looser than S3 |
| PC2 | Geometry and visual detection meets S2/S3/S5; prior survey unnecessary | Offboard resources and valid raw evidence; fusion comparison where paired data exist |
| PC3 | Store completed survey onboard; three exports ≥1 GB each to laptop, each ≤30 min with integrity | Storage, transfer hardware, export verification |
| RD1 | Show findings with images, available geometry, units, gap/reference warnings | Processing-to-report schema and operator hardware |

S2 evaluation includes ≥10 geometric cases and ≥10 negatives held out from tuning. S5 demo uses ≥10 positives per class and ≥10 nuisance-only regions. Do not use calibration/control points as scored checkpoints. A previous survey is optional. No numerical gradient-error acceptance limit is settled.

## Constraints inherited from the documents

- C1–C3: aircraft/site/pilot/airspace/registration/Remote ID and campus authorization are operating-plan inputs. The saved requirements describe Part 107, VLOS, <55 lb, ≤400 ft AGL, weather minima, and campus requests ≥3 weeks before flight. These are carried references, not a current legal determination or an approval. Later operational research should check applicability to the selected aircraft/site.
- C4–C5: picoScan Ethernet is described as 10/100 Mbit/s with four-pin D-coded M12; supply 9–30 V DC. Verify the delivered variant, plug, pinout, supply transients, and cables before releasing a connection design.
- C6: preserve the manufacturer's optical assembly, labeling, and operating conditions; sensor classification is not certification of the integrated UAV. A presentation omission of IEC 60825-1 did not remove the requirement-document context.
- Referenced standards: IEEE 802.3-2022, IEC 60825-1:2014, RFC 7946 for valid WGS84 geographic exports, and RFC 8446/TLS 1.3 where network transfer/access applies. Local metric coordinates must remain explicitly identified.

See [the verification plan](../verification/plan.md) and SRC-007 for bench/full-system boundaries. GC3 meaning, gradient acceptance, and total error allocation remain [open decisions](../decisions/open-questions.md).

## Final approach reconciliation — SRC-034

| Topic | Current design input | Requirement / remaining action |
| --- | --- | --- |
| Survey speed | §§3.1.1/3.3.1 plan approximately 0.25–1 m/s at 5–8 m; user confirmed speed November 16 (D-019) | Operating-range choice settled; Q-17 tracks alignment of older FP2 1–2 m/s test wording while preserving original-source provenance |
| Flight energy | §3.3.1 estimates ~8.5 min at a 2.25 kg all-up target under assumed usable energy | S1/FP1 remains ≥10 min with ≥20% calibrated usable energy; revise the design and validate, Q-18 |
| Budgets | $1,000 whole-design limit; $447.09 pre-fee aircraft estimate | Keep strictly under-$700 aircraft constraint; reconcile delivered totals, scope, and funding, Q-10 |
| Sampling/camera/storage | Conditional ~50 Hz/0.25°–0.33° scan mode; 11.9 MP at 3 fps and ≤1 ms exposure; USB survey card | Planning inputs for S2/S4/S5/SA1–SA3, not acceptance bounds or measured performance |
| Operator alerts | Pocket critical-alert display; laptop detailed status on separate telemetry | DT1–DT3 need full recorder→PX4→ELRS→Pocket fault/latency checks; bridge compatibility remains open |
| Reporting | Hosted portal/PostgreSQL/PostGIS/cloud files primary; local SQLite fallback | RD1 evidence/warnings persist; RFC 7946 geometry uses geographic longitude/latitude, with local metric coordinates separate |

## Timing development goals — SRC-036

[The timing plan](../integration/camera-lidar-timing.md) adds row/beam acquisition-time models, software PTP/native-clock maps, and independent optical/encoder tests. Its **P95 absolute camera/LiDAR residual ≤3 ms**, **signed median within ±1 ms**, and **drift ≤1 ms/10 min** are proposed bench goals. They do not replace SA2's ≤20 ms sensor-to-motion-reference timing bound, prove its required coverage, or demonstrate S3. Report maximum residual, reference uncertainty, valid coverage and gaps separately. The 3 m/binned 10–15 fps/SSD bench configuration does not amend flight height/speed/storage or set new camera/detection acceptance criteria.

The final approach reports sensor receipt/Ethernet streaming only. That does not satisfy concurrent recording, timing, range, loaded flight, detection, or export acceptance. Retain NOT_RUN in the verification matrix until attributable test artifacts support results.
