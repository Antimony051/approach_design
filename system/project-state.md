# Project state at workspace creation

Consolidated October 24, 2026. The latest explicit hardware/delivery/test confirmations in the repository are October 22–23; no newer inventory was inferred.

## Confirmed context

- PaveWatch / Aerovengers, ECE 4512, Mississippi State University; advisor Jingdao Chen. UAV inspection of paved-surface geometry and visible distress supports human maintenance review.
- The team was selected for the SICK$10K Challenge. The picoScan was reported incoming and had **not arrived** on October 23. Exact variant, licenses, system plug, cables, and included accessories are unknown. No hardware tests had been performed.
- No project hardware had been ordered at the latest confirmation. The only explicitly owned equipment is two 2S packs and chargers: each pack 5,200 mAh, 50C, 7.4 V nominal, 38.48 Wh. Charger models/cell support, pack dimensions/mass, connectors, condition, and charging leads are unknown.
- The user set the complete aircraft ceiling to **under $700**, including flight battery, RC, and navigation, excluding supplied LiDAR and recording payload. Earlier research subtotals include ground telemetry. Include delivered costs and a usable charging arrangement; identify accounting boundaries explicitly.
- Overall hardware/demo/operating funding remains to be reconciled. Earlier $700 Fall / $1,000 total course context and the application's $999 acquisition estimate are historical context, not a new approved whole-project budget.
- FP4 attitude acceptance is **≤5° for ≥90% of evaluated roll/pitch samples**, per user correction. The final source document's ≤1° test wording is stale.

Sources: reference entries SRC-001 (root context), SRC-002 (final requirements), SRC-003 (latest saved final deck text), SRC-004 (MSDR notes), SRC-008 (flight comparison), and this conversation's aircraft budget clarification. No external claims were rechecked here.

## Planning direction, still open to design work

Latest final MSDR slides 13–15 name X500 v2 ARF + Kakute H7 Mini v1.5, Orange Pi Zero 3 + expansion board, and InnoMaker color USB camera as planning choices. The original F450/SpeedyBee/F9P concept remains in that presentation. S500/Pixhawk is another candidate. Earlier application files instead propose X500 development kit/Pixhawk/PX4, Pi 5, Camera Module 3, and cloud processing; these are historical proposals and do not establish purchased equipment.

The current baseline assesses **one survey**. Earlier-survey change detection, paired-fusion improvements, cloud infrastructure, and edge inference are extension/design choices rather than reasons to impose new airborne hardware requirements. Post-flight transfer and processing remain necessary.

The proposed survey envelope is dry daylight, 5–8 m above pavement, 1–2 m/s. A user's location concept used 3 m as an example; it did not replace the requirement envelope. Pose may be measured or estimated offline in the ground demo; global centimeter accuracy is unproven.

## People and subsystem ownership

| Code | Subsystem | Lead | Charter support |
| --- | --- | --- | --- |
| FP | Flight Platform, Power & Control | Ankit Dhakal | Aalok Uprety |
| DT | Diagnostics & Telemetry | Shisir Baral | Ankit Dhakal |
| SA | Sensor Payload & Data Acquisition | Abhinav Dhakal | Saugat Karki |
| GC | Ground Control & Communications | Pritam Adhikari | Abhinav Dhakal |
| PC | Data Processing & Change Detection | Aalok Uprety | Shisir Baral |
| RD | Reporting, Database & Alerts | Saugat Karki | Pritam Adhikari |

Shisir is PM and current overall reviewer; Abhinav is Chief Scientist. Current MSDR/demo handoffs route architecture, purchase, and scope recommendations to Shisir. This workspace does not amend signed charter governance. Pritam's diagnostics implementation support in the demo does not transfer DT ownership.

## Near-term demonstration and calendar

The proposed Capstone I demonstration uses real sensors on a stand/manual carriage, local recording, measured or post-processed poses, and labeled replay. A finished aircraft is not required. Acquisition, diagnostics, and processing are the three demonstration workstreams. Live sensor timing/range tests still need the actual sensor and interfaces. Bench substitutes do not establish airborne performance or instructor acceptance.

Saved schedule: approach draft October 30; approach final November 13; demo rubric final November 20; demonstration November 30; final document December 4, 2026. Spring dates in the MSDR are proposals. These dates are carried from saved files, not freshly checked against Canvas.

See SRC-006/SRC-007 for exact ground-demo scope and methods, and SRC-005/SRC-009 for assignments/charter.
