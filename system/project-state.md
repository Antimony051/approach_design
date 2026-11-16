# Current project state

Updated November 16, 2026 from **SRC-034, PaveWatch_Approach_Final.docx** at the user's request. This is a document alignment, with no new external research, purchases, or tests. [The source note](../references/new-evidence/2026-11-16-final-approach.md) records provenance and conflicts. October 22–23 inventory statements remain historical where the final approach provides newer information.

## Status and constraints

- PaveWatch / Aerovengers, ECE 4512, Mississippi State University; advisor Jingdao Chen. Supervised UAV pavement inspection supports human maintenance review. A rover was considered and not chosen (SRC-034 §3.1).
- **SRC-034 §3.3.3 reports that the SICK$10K Challenge picoScan150 Pro was received and streams scans over Ethernet.** Its reference [20] names PICS150-01000 Pro, part 1134610; confirm the received label rather than treating a cited datasheet as inventory. Firmware/licenses, plug, accessories, scan profile, and test logs remain unrecorded. No acceptance results were supplied with this update.
- October 22–23 confirmed two owned **2S** packs and chargers: each 5,200 mAh, 50C, 7.4 V nominal, 38.48 Wh. Connectors, dimensions/mass, condition, and charger cell support remain unknown. The design calls for a **4S** battery; neither series use nor 4S charger compatibility is established.
- The final approach selects a design but does not establish purchase/receipt of its other components. Receiver/charger ownership checks remain open. The earlier no-orders statement describes October status, not a verified November inventory.
- Retain the user-confirmed **strictly under $700 complete-aircraft ceiling**, including flight battery, RC, and navigation, excluding supplied LiDAR and recording payload. Keep telemetry and usable charging visible. SRC-034 states a **$1,000 whole-design budget limit**; use it for planning and reconcile scope and actual funds. It is no longer merely an old budget reference.
- FP4 remains **≤5° for ≥90% independently evaluated roll/pitch samples**, per user correction. The final requirements' ≤1° test text is stale.

## Current design baseline — PW-APPROACH-01

| Area | Selection in SRC-034 | Remaining qualification |
| --- | --- | --- |
| Airframe | Custom 500 mm hybrid X; carbon-fiber plates/tubes, PA6-CF fittings; X500 v2 CAD reference | Fabrication drawings, strength, clearance, mass/CG |
| Propulsion/control | MicoAir H743v2-AIO-35A with integrated ESCs; PX4 1.16.0/MicoAir743v2; QGroundControl; 4 × SunnySky X2216 880 KV; Master Airscrew MR 10 × 4.5 in | Exact build/port map and matched motor/prop/voltage evidence |
| Energy/navigation | 4S 14.8 V 5,200 mAh LiPo; M10G GNSS/compass | Battery SKU, charging, sensing, navigation/reference accuracy |
| Pilot/status | RadioMaster Pocket 2.4 GHz ELRS and RP1 V2; separate MAVLink laptop telemetry | Receiver/cell inventory, protocols/radios/ports, payload-alert bridge |
| Acquisition | picoScan150 Pro Ethernet; Pi 4 Model B; standard Camera Module 3 CSI; Python recorder | Pi memory/OS/library versions, scan mode, capture rate, timing, cooling/power |
| Storage | SanDisk Extreme 128 GB microSD in USB 3 reader; separate OS card | Exact card/reader, sustained writes, retention, integrity/recovery |
| Processing | Offboard after collection; independent geometry/image branches with evidence-based association | Laptop/workstation versus cloud execution; optional learned fusion |
| Reporting | Hosted portal; PostgreSQL/PostGIS; cloud evidence storage; login/dashboard/PDF | Provider/resources, schema, backups, secure access/cost; local SQLite fallback |

Older X500/Kakute, S500/Pixhawk, F450/SpeedyBee, Orange Pi/InnoMaker, Pi Zero, and SSD proposals are alternatives, not the active BOM. Prior user operating decisions remain in force.

## Planning estimates and conflicts

- Survey plan: dry daylight, **5–8 m**, **0.25–1 m/s**. FP2 still specifies **1–2 m/s**; Q-17 tracks reconciliation. Slower collection does not automatically pass the original condition.
- Capture plan: roughly 50 Hz at 0.25°–0.33° **if supported**, Camera Module 3 11.9 MP JPEG at 3 fps, ≤1 ms exposure and locked focus. Source estimates: 9–15 MB/s image writes, <1 MB/s other data, 6–10 GB per ten minutes. Exact scan profile and simultaneous performance are unverified.
- Mass/space: **440–550 g estimated sensing payload**, **650 g target**, older **800 g stress case**, **2.25 kg all-up target**. Reserved envelopes: sensor **120 × 100 × 130 mm**, recorder **120 × 90 × 60 mm**. Source payload wording excludes aircraft, battery, and power distribution; reconcile shared mounts/regulators before comparing totals.
- Energy: the source's assumed usable-energy/reserve model yields **~8.5 min**, below S1/FP1. APC 10 × 4.7 data are a proxy for the selected 10 × 4.5 prop. See [energy screening](../integration/flight-energy-screen.md) and Q-18.
- Cost: **$447.09 aircraft hardware before fees** is an unreconciled source estimate. Recorder ~$109, camera ~$25, and survey storage bundle ~$55 are also source estimates, not delivered totals or proof of compliance.

The baseline assesses one survey; previous-survey comparison is optional. Post-processed pose refinement is permitted with independent checks. A known launch coordinate alone does not establish scale, orientation, or centimeter accuracy. The approximate 1 m × 1 m horizontal / 20 cm vertical preference does not replace S3/PC1.

## People and subsystem ownership

| Code | Subsystem | Lead | Charter support |
| --- | --- | --- | --- |
| FP | Flight Platform, Power & Control | Ankit Dhakal | Aalok Uprety |
| DT | Diagnostics & Telemetry | Shisir Baral | Ankit Dhakal |
| SA | Sensor Payload & Data Acquisition | Abhinav Dhakal | Saugat Karki |
| GC | Ground Control & Communications | Pritam Adhikari | Abhinav Dhakal |
| PC | Data Processing & Change Detection | Aalok Uprety | Shisir Baral |
| RD | Reporting, Database & Alerts | Saugat Karki | Pritam Adhikari |

Shisir remains PM/overall reviewer; Abhinav is Chief Scientist. Pritam's diagnostics support does not transfer DT ownership. Source selections do not amend signed charter governance.

## Demonstration and calendar

SRC-034 concludes with ground power/recording/timing/communications/processing tests before integrated flights. SRC-006/SRC-007 still propose a stand/manual-carriage Capstone I demonstration with real sensors, measured or post-processed poses, local recording, and labeled replay; a finished aircraft is unnecessary. These proposals establish neither instructor acceptance nor airborne performance.

Saved schedule: approach final November 13; demo rubric final November 20; demonstration November 30; final document December 4, 2026. These are saved planning dates, not a new Canvas check or proof of submission.
