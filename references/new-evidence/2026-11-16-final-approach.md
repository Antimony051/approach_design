# Final approach alignment — November 16, 2026

Source: `final_docs/PaveWatch_Approach_Final.docx`, supplied in the project workspace and explicitly requested as the basis for this update. Portable [verbatim DOCX, SRC-034](2026-11-16-final-approach/PaveWatch_Approach_Final.docx) and [readable text, SRC-035](2026-11-16-final-approach/approach-text.txt) are recorded in the [source manifest](../source-manifest.csv) with hashes. This is a review of the supplied document, not new manufacturer research or a hardware test. Its cited URLs and historical access dates were not rechecked.

## Decisions carried into PW-APPROACH-01

| Source section | Design choice / reported state | Working records affected |
| --- | --- | --- |
| §3.1 | Supervised UAV selected over wheeled rover; 5–8 m, 0.25–1 m/s | Project state, architecture, FP/GC, Q-17 |
| §§3.3.1/3.4.1 | Custom 500 mm hybrid frame; carbon-fiber plates/tubes, PA6-CF fittings; X500 v2 CAD reference only | FP, assembly, mass/fit; BOM-001/030/031 |
| §§3.3.1/3.4.1 | MicoAir H743v2-AIO-35A, integrated four-channel ESC; PX4 1.16.0/MicoAir743v2; QGroundControl; M10G GNSS/compass | FP/GC; IF-01/02/03/09/10; BOM-002/005 |
| §3.3.1 | Four SunnySky X2216 880 KV; Master Airscrew MR 10 × 4.5-inch props; 4S 14.8 V 5,200 mAh pack; $447.09 pre-fee aircraft estimate | FP, procurement, power, energy screen; BOM-003/030/031 |
| §§3.3.2/3.4.1 | Pocket 2.4 GHz ELRS/RP1 V2; intended payload critical alerts on handset; separate laptop MAVLink telemetry | DT/GC, IF-11/12/13, COMP-19; BOM-006/007/032/033 |
| §3.3.3 | Reports picoScan150 Pro received and streaming Ethernet | State, Q-01, BOM-009; does not establish acceptance tests |
| §§3.2.1/3.3.3/3.4.1 | Pi 4 Model B; standard Camera Module 3 CSI; separate SanDisk Extreme 128 GB survey microSD in USB 3 reader; Python capture | SA, storage/power/fit, IF-05–09/15; BOM-011–015/034 |
| §§3.3.3/3.4.1 | RecorderSupervisor, LidarCapture, CameraCapture, PoseLogger, HealthMonitor, ManifestWriter, ExportService; bounded queues; timing/sequence/gap records; checksums; complete/incomplete packages | SA/DT, timing, assembly, export checks |
| §3.3.4 | Plan Run / Extract Data / Upload Data; mission upload/readback, deliberate launch, separate recording/arming; pause/resume/takeover/return/land events | GC and prior operating notes |
| §3.3.5 | Post-flight processing; laptop/cloud execution undecided; independent geometry/image branches, compatible association, original poses retained | PC, IF-16/20; learned RGB-D remains an optional experiment |
| §§3.3.6/3.4.1 | Hosted reporting primary; PostgreSQL/PostGIS and cloud files; login, map/filter/evidence dashboard, PDF export; local SQLite fallback | RD, API/schema, ground resources and recurring costs |
| §3.4.2 | Rigid removable common sensor plate; isolation of whole plate if needed; ventilated PETG/ASA cover; strain relief; non-magnetic GNSS mast | Assembly, IF-18, mass/fit |

## Estimates and unresolved contradictions

- **Requirements:** retain SRC-002 and the user's ≤5° FP4 correction. The final approach's 0.25–1 m/s plan differs from FP2's 1–2 m/s condition (Q-17). Its ~8.5 min energy estimate falls short of ≥10 min with reserve (Q-18). Neither is silently treated as an amendment.
- **Propulsion:** 2.25 kg all-up is a design target. The 563 gf hover / 1,125 gf 2:1 screen and ~326 W propulsion estimate use an APC 10 × 4.7 reference, while selected props are Master Airscrew MR 10 × 4.5. This is proxy data, not matched performance. See [energy calculations](../../integration/flight-energy-screen.md).
- **Budget:** the opening paragraph states a $1,000 whole-design limit. Carry it alongside the prior under-$700 aircraft constraint. The $447.09 aircraft figure, $109 Pi, ~$25 camera, ~$55 card/reader, and $71.50 Pocket are source estimates, with no fresh availability/delivered quotes. Aircraft inclusions and recurring/ground/fabrication boundaries remain unresolved (Q-10); do not add the Pocket twice if it is already in the aircraft estimate.
- **Sampling:** ~50 Hz at 0.25°–0.33° is explicitly conditional on an available scanner profile. Idealized 5 m near-nadir spacing of ~22–29 mm across and 5–20 mm along track is not guaranteed over the full scan/height range. The typical 20 mm range-error statement is not SA3 evidence.
- **Images/storage:** 11.9 MP JPEG at 3 fps, ≤1 ms exposure, fixed survey focus, 9–15 MB/s image writes, <1 MB/s other streams, 6–10 GB per ten minutes, and ~60–90 MB/s storage throughput are planning estimates. Encoding benchmark extrapolation, card speed, blur/rolling-shutter correction, image detail, capacity, and the ten-minute combined run require measurement. A known speed alone does not validate rolling-shutter correction.
- **Power/mass/fit:** 20 W combined non-propulsion demand, 80% usable-energy factor, 440–550 g payload, 650 g target, ~4 g survey storage, and sensor/recorder envelopes are unverified inputs. Source mass wording excludes aircraft, battery, and power distribution; reconcile regulators, mounts, harnesses, cooling, and all-up mass before claiming margin.
- **Clock/alerts:** the source proposes PTP or NTP for LiDAR/recorder mapping, but exact feature/configuration and residual error need checking. Recorder faults do not automatically appear on Pocket; PX4/receiver/ELRS/EdgeTX forwarding and display remain unresolved (Q-19). Cited Lua/Yaapu material does not establish compatibility.
- **Geographic handoff:** source prose combines local metric positions with GeoJSON. RFC 7946 geographic geometry must use WGS84 longitude/latitude; carry local XYZ as explicitly identified properties or a separate local product. Without reliable geographic registration, retain local findings and flag/unset geographic geometry. A best-effort GPS position remains labeled uncertain (Q-20).
- **Earlier work:** October supervised-interruption/proximity intent is retained, but the final approach does not select proximity hardware or establish its PX4 implementation. November 3 RGB-D work remains an optional experiment alongside the final approach's independent branches. Historical ArduPilot examples are not selected PX4 behavior.

The source contains the unfinished sentence “so talk about the weight limits that this configuration will support.” It is an unresolved editorial item, not evidence of a payload rating. No new payload capacity is invented here. The DOCX remains unchanged.

## Extraction and evidence limits

The text extract reads OOXML body paragraphs and table cells in order; table boundaries are marked. It does not reproduce embedded figures, dimensions inside images, rendered pagination, or layout. The original DOCX is retained for those details. Initial snapshots/extracts and previous evidence notes are preserved. No acceptance result is marked passed by this reconciliation.
