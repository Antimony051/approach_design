# Open design questions

These are handoffs for future design work, not questions the user must answer before this workspace can be used. Investigate available evidence first; ask focused questions when needed. No answer is inferred from elapsed time.

| ID | Lead / coordination | Question | Affected work | Starting evidence / next action |
| --- | --- | --- | --- | --- |
| Q-01 | SA | What exactly arrives from SICK: variant licenses system plug cables and accessories? | Sensor connectors power data timing mass and missing accessories | Inventory package/label/manual; latest status unreceived |
| Q-02 | FP+GC | Which complete aircraft/controller/firmware/GCS is selected? | Propulsion port map mounts kit inclusions and delivered aircraft cost | Start latest X500/H7 preference; compare S500 and exact F450 route |
| Q-03 | SA | Which camera recorder expansion storage and OS work as one stack? | Color lens USB/CSI modes shared bus timing power cooling | Latest Orange Pi + InnoMaker; retain Pi/USB3/CSI alternatives |
| Q-04 | FP+SA | What power branches regulators protective parts and harnesses are required? | Loaded energy startup current rail stability and protection | Derive from selected loads; no FC-powered recorder assumption |
| Q-05 | FP+SA | How will everything physically mount and clear the ground/optics? | Rail/plate interfaces battery location CG rigid sensor transforms | Dimensioned installation; 650/800 g are allocations |
| Q-06 | SA+PC+FP | Which clocks timestamps and independent timing method meet SA2? | Camera exposure sensor phase pose clock drift and uncertainty | Optional sensor features unconfirmed; receipt time insufficient |
| Q-07 | PC+FP+GC | How are image/aircraft poses and survey scale/orientation established? | Ordinary GNSS vs markers/offline reconstruction vs RTK/PPK | Independent checkpoints; known launch coordinate alone insufficient |
| Q-08 | GC+DT | What stream exactly does GC3 buffer and how does it reconnect? | Buffer rates capacity endpoints ordering and fresh control/health | Retain exact requirement until interpretation approved |
| Q-09 | FP | What chargers connectors and other owned tools are actually available? | 4S charging plan test supply tools and budget | Ask for model/label inventory; only 2S packs/chargers confirmed |
| Q-10 | Shisir+RD | What is the current whole-project acquisition and recurring allocation? | Payload demo equipment contingency shipping tax and services | Under-$700 aircraft is confirmed; older $999/$1000 whole plan historical |
| Q-11 | PC+SA+RD | Which physical transfer and local/hosted processing/review path is selected? | SSD cables workstation backup resources and operating costs | Do not assume cloud is mandatory; three real ≥1 GB exports |
| Q-12 | PC+FP+SA | How is S3 error allocated across range pose timing geometry and calibration? | Camera/IMU/mount/navigation selection and reference tools | FP4/PC1 passing alone cannot establish S3 |
| Q-13 | PC+Shisir | What numerical gradient-error acceptance bound will be used? | Reference slope fixtures and evaluation | Current requirement asks reporting; no agreed numerical threshold |
| Q-14 | FP+GC | What site pilot authorization operating equipment and flight limits apply? | Schedule campus lead time Remote ID and loaded flight access | Saved requirements are leads not current approval or legal research |
| Q-15 | SA+PC+DT | What ground fixtures references timing logger and demo test space are available? | Can commission/demo before aircraft completion | Real sensor still needed; actual tools and instructor acceptance unconfirmed |

## Source conflicts to preserve

October 29 refinement is recorded in [supervised mission operation](../subsystems/04-ground-control-communications/supervised-mission-operation.md) and D-009/D-010. Post-processed reference estimation, skip/early-end support, proximity-triggered stopping/holding, pilot detours, and deliberate resumption are the agreed direction. Remaining questions: exact modes/authority and safe rejoin semantics; measured stopping/holding/clearance limits; proximity coverage/failure response; cost/power/mass/port impact; positioning-loss and combined RC/position-loss fallback. IMU-only position holding is not established. This follow-up resolves the earlier live-versus-offline permission question, while final error bounds and evidence remain open.

October 28 GC operational follow-up: [the gap review](../subsystems/04-ground-control-communications/operational-gap-review.md) expands Q-02/03/07/08/11/12/14. Exact centerline tracking is excluded from first-version scope. Define the user's provisional location target (1 m × 1 m horizontal, 20 cm vertical), its confidence and datum, and live versus post-processed applicability. Decide mission/run identity, launch authority, duration semantics, link-loss behavior, and cloud-upload scope before complete user stories. These do not replace existing acceptance criteria.

- September application says “Purchased X500” and uses Pixhawk/PX4/Pi 5/Camera Module 3. October confirmations say no orders; latest slides favor X500 ARF/H7/Orange Pi/USB. The old purchase wording is not inventory evidence.
- September investigations include 8–12 m / 3–5 m/s camera proposals, 30-minute recording gates, smaller geometric fixtures, and preferred global-shutter CSI cameras. Current requirement/demo numerical targets take precedence; historical characterization remains useful as a lead.
- The final requirements document's FP4 test says 1° despite its 5° requirement. The user resolved both to 5°; do not reopen it as an unanswered question.
- The user's location note assumes a Pro unit, 3 m example height, and exact/centimeter reconstruction and reflectivity claims. Delivered variant and demonstrated accuracy remain unknown; current envelope stays 5–8 m.
- Flight report shortlist has three configurations across two airframes; latest presentation instead retains F450 among three showcased options. Neither presentation ordering nor research recommendation is a completed purchase decision.
- Cloud-first application and local-first investigations are competing implementation proposals. Baseline hardware functions do not require a cloud selection yet.
- Raw compute/camera notes contain inconsistent price sums, optimistic throughput/blur claims, and no measured validation. Preserve them as leads rather than selecting parts from their prose alone.
