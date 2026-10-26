# MSDR preparation — proposed team assignments

Prepared October 22, 2026. Review: October 23, 11:00–11:55 a.m. Central.
Website posting deadline: October 23, 10:00 a.m. Central.

Shisir remains Project Manager and overall reviewer. These assignments divide
MSDR preparation; they do not change the signed charter's subsystem ownership.
Bring Shisir recommendations and the evidence needed to choose. He retains the
final decisions on architecture, purchases and budget, requirement changes,
semester demonstration commitments, and presentation release.

## Common handoff from each teammate

Return slide-ready corrections for your section, source links for specifications
and prices, your recommended option and rationale, and a short list of decisions
that need Shisir's review. Identify assumptions explicitly. Include realistic
task dates and one measurable Capstone I deliverable with its test method,
equipment, sample count, and artifact. Send your team photo to Saugat.

Work on separate section copies or provide slide-numbered edits so five people
do not overwrite the same master. Saugat assembles the review copy. The builder
regenerates and overwrites the deck; preserve manual edits before using it.

## 1. Ankit — aircraft, propulsion, power, and flight BOM

**Outcome:** a specified aircraft candidate and an honest estimate of its
installed cost and feasibility.

- Review `parts_to_buy.txt`: identify exact F450, motor, propeller, ESC,
  SpeedyBee stack, flight battery, and RC receiver options. Check whether the
  bundle and stack duplicate ESCs.
- Check the complete installed mass, published thrust/current evidence at the
  selected voltage, mounting/clearance, payload power branches, and charger
  compatibility. The existing packs are **2S, 7.4 V, 5,200 mAh**, not 6S.
- Update the three platform alternatives and recommend one. Distinguish
  published specifications, calculations, and tests still needed; do not claim
  demonstrated payload capacity or endurance.
- Supply a line-item flight BOM with exact links, price dates, included parts,
  missing parts, and shipping allowances. Send it to Saugat for budget assembly.
- Recommend how to reconcile FP4's 5° requirement and 1° test wording, with
  Aalok checking the consequence for final surface accuracy.

**Slide ownership:** 11; aircraft/power contributions to 14–15; FP row on 20;
flight decisions on 22. Coordinate with Pritam on controller ports and firmware.

**Handoff to Shisir:** platform recommendation, exact flight BOM, mass/power
worksheet, flight test proposal, and unresolved choices. Hardware purchase and
acceptance-threshold changes remain Shisir's decisions.

## 2. Abhinav — LiDAR, camera, recorder, and acquisition health

**Outcome:** a credible plan to receive the sensor and record synchronized data.

- Confirm what is known about picoScan delivery, variant, and accessories.
  List what must be checked on receipt: power, connectors, Ethernet output,
  configuration, timestamps, and usable scan sector.
- Review the three onboard-computer and three camera alternatives. Recommend
  the baseline, with installed power, storage, timing access, cost, and image
  detail as selection criteria.
- Specify the recorder's LiDAR/image/pose inputs, files and timestamps, and
  proposed calibration steps. Give Ankit payload mass/power allowances and
  Pritam the required flight-controller data interface.
- Define recorder health outputs: recording state, storage condition,
  stream gaps, and missing pose references. Pritam owns delivery to the operator;
  Saugat owns their display in findings.
- Provide a 10-minute bench/replay demonstration plan, range-reference setup,
  timing-event method, and explicitly labeled fallback if the sensor is late.

**Slide ownership:** 12–13; sensor/recorder details on 6 and 9–10; SA row and
recorder-side DT details on 19. Provide payload lines for 14–15.

**Handoff to Shisir:** computer/camera recommendations, sensor commissioning
checklist, recorder/interface sketch, payload BOM, and test plan. State which
physical claims depend on actual sensor delivery.

## 3. Pritam — missions, RTK, communications, and operator telemetry

**Outcome:** an end-to-end route/control/data-link plan that can actually be wired
and tested.

- With Ankit, map GNSS, receiver, companion computer, telemetry and any compass
  connections to the selected controller. Recommend firmware/GCS pairing and
  identify any unverified feature support.
- Identify an actual RTK correction source: available base station or suitable
  correction service, its access/cost, and how corrections reach the rover.
  Distinguish ordinary GNSS, RTK float, and RTK fixed operation.
- Separate RC control, mission/health telemetry, sensor recording, and post-flight
  transfer. Identify required radios/cables and their budget implications.
- Recommend an exact meaning for GC3's 60-second buffer: stream, expected rate,
  buffer location/capacity, reconnection order, and test endpoint. Keep control
  commands and current safety status out of any proposed stale-data backlog.
- Plan waypoint, acknowledgement-latency, link-loss/recovery, and diagnostics
  delivery tests. Coordinate shared timestamps with Abhinav.
- Identify who will handle site approval/pilot arrangements and what lead time
  affects field milestones. Report the status rather than assuming approval.

**Slide ownership:** control/link details on 6; RTK line on 14; GC row on 20;
operator-side DT details on 19; communications issues on 22. Input to 9 and 15.

**Handoff to Shisir:** connection/port map, correction-source recommendation,
link/BOM table, proposed buffer requirement wording, and communications tests.

## 4. Aalok — requirements consistency, processing, and verification

**Outcome:** a coherent explanation of what the system measures and how success
will be scored.

- Check S1–S6 against the current final requirements file, including October 19
  edits. Preserve single-survey assessment; historical comparison is optional.
- Trace geometry/image inputs through the common frame to detections and
  reported measurements. State what valid pose, timing, and calibration evidence
  the processor needs from Ankit and Abhinav.
- Explain why the looser PC1 frame checks do not establish S3's final surface
  accuracy. Recommend reconciliations with Ankit rather than silently changing
  the accepted limits.
- Propose a measurable gradient-error criterion for Shisir's review, or clearly
  identify gradient testing as characterization until one is agreed.
- Define held-out geometric/image evaluation cases, correspondence rules,
  sample counts, references/tools, precision/recall, and error reporting.
- Plan three timed, integrity-checked ≥1 GB laptop exports and give Saugat a
  sample finding schema with image, measurement, units, and warning fields.

**Slide ownership:** 7–8, 21; PC row on 19; processing/accuracy issues on 22.
Review the proposed processing portion of 6 and 23.

**Handoff to Shisir:** corrected requirement wording proposals, processing flow,
test matrix, and a precise list of claims the planned demo can support.

## 5. Saugat — reporting, schedule, and presentation assembly

**Outcome:** one coherent presentation and review package ready for Shisir's
final review.

- Define the reviewer-facing finding view: images, available geometry, units,
  survey reference, and missing-data/invalid-reference warnings. Use Aalok's
  output schema and Abhinav/Pritam's health fields.
- Collect all six real team photos and maintain names/roles. Label mockups and
  illustrative data accurately.
- Gather each owner's task dates, dependencies, and Capstone I deliverable.
  Consolidate the two-semester Gantt and keep Spring dates labeled as proposed.
- Consolidate flight, payload, communications, and other cost lines into one
  nonduplicated budget. Show missing quotes, shipping, correction access, and
  contingency separately. Shisir decides any scope/budget tradeoff.
- Merge slide contributions, fix formatting/citations, and check terminology,
  diagram interfaces, requirement IDs, and the two-slide deliverables limit.
- Produce the review PowerPoint/PDF and prepare the website download/link.
  Check the draft's website/submission logistics; Shisir reviews the final
  release before publication.

**Slide ownership:** 1–5, 16–18, 23–28; RD row on 20. Assemble approved inputs
on 6, 9–10, and 14–15; do not independently choose other owners' technical values.

**Handoff to Shisir:** merged PPTX/PDF, reporting sketch, consolidated budget,
updated schedule, rubric checklist, and a short unresolved-decision list.

## Shisir — review and high-level decisions

Review complete recommendations rather than doing each owner's research.
Resolve cross-subsystem conflicts and decide:

1. Aircraft/controller/firmware baseline and fallback.
2. Budget allocation and what is ready to order.
3. Requirement/test wording, particularly FP4, S3/PC1, gradients, and GC3.
4. Physical versus bench/replay commitments for the Capstone I demonstration.
5. Final slide claims, presentation speaking split, and release for publication.

Retain the charter's Diagnostics & Telemetry responsibility through review of
Abhinav's acquisition-health outputs, Pritam's delivery tests, and Saugat's
warning display. Those teammates prepare the evidence; Shisir judges whether
the pieces form a coherent subsystem story.

## Proposed handoff times — Central

- **Tonight, October 22, 10:30 p.m.:** each technical owner supplies a first pass,
  sources, task dates, photo, and decision list; Saugat merges available sections
  as they arrive.
- **Tonight after the first pass:** Shisir resolves the critical choices;
  unresolved items remain explicitly labeled as proposals in the briefing.
- **Tomorrow, October 23, 8:30 a.m.:** merged deck/PDF ready for final review and
  a brief team speaking walkthrough.
- **9:00 a.m.:** Shisir freezes the reviewed version.
- **9:30 a.m. target:** publish the approved file and verify the website link,
  leaving margin before the **10:00 a.m. requirement**.
- **11:00–11:55 a.m.:** all members attend the review and explain their work.
  Upload the approved presentation to Canvas before the saved **11:59 p.m.**
  deadline.

These times are a proposed coordination plan, not commitments already accepted
by teammates. This file has not been sent to anyone.
