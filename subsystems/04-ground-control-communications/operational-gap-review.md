# Ground-control operation: workflow and gap review

October 28, 2026. **Draft for discussion before user stories.** The workflow below comes from the user's proposal; recommendations are not approved implementation choices. No hardware, navigation estimator, transport, or application stack has been selected or tested by this review.

**October 29 follow-up:** [Supervised mission operation](supervised-mission-operation.md) records the subsequent accepted operating direction and supersedes open questions here about allowing post-processed references, skip/early-end support, proximity stopping, pilot detours, and explicit resumption. The original gap analysis remains as discussion context; numeric reference conventions and implementation choices remain open.

## User intent and accuracy clarification

- A laptop application supports planning, loading a mission, starting a run, extracting onboard data, and uploading data to a cloud endpoint.
- A wired connection and/or Bluetooth are candidates. Reusing the RC communications channel is another candidate; a dedicated Bluetooth link is not a requirement.
- The operator defines route, height, and duration and routes around obstacles. The aircraft is moved to the launch location after mission loading; departure is deliberately requested from the controller or application after checks.
- Exact sidewalk-centerline tracking is **not required for the first version**. The desired location reference is approximately **1 m × 1 m horizontally and 20 cm vertically**, to support mapping findings to the world. The user allows a looser approach if downstream results remain adequate.
- The meaning of the horizontal box, confidence/pass fraction, reference origin, vertical datum, and whether accuracy must be live or may be post-processed remain to be agreed. Do not silently translate the box into ±1 m per axis or a radial error bound. The working recommendation is to evaluate final acquisition-time poses separately from live navigation.
- Pi 4 is the user's current example recorder. Existing planning favors Orange Pi; neither is a confirmed selection. Cloud upload is a requested workflow action, with mandatory versus optional availability still open.

## Main distinction: flight, reference, and findings

| Purpose | What must be established | Current constraint / gap |
| --- | --- | --- |
| Navigate the aircraft | A usable live position estimate and bounded flight corridor | FP2 permits 2 m horizontal route error for its specified fraction of samples. Passing FP2 does not guarantee remaining above a narrow sidewalk or full survey coverage. |
| Reference acquired data | Position **and orientation at acquisition time**, with source, frame, uncertainty, timing, and rigid sensor offsets | User's desired location reference resembles PC1's 1 m X/Y and 0.2 m Z checkpoint bounds, but PC1 does not guarantee those bounds for every aircraft/image pose. |
| Map findings | Target position/geometry in the selected local and geographic frames | S3 requires 0.5 m horizontal centroid and 60 mm height accuracy for the specified fraction. Passing a drone-location target alone does not establish S3. Defect height relative to pavement and geographic altitude have different error contributions. |

A local origin (0,0,0) is useful bookkeeping. It does not improve measurement accuracy. Geographic mapping also needs an origin coordinate, orientation, metric scale, vertical reference, and uncertainties. An uncertain launch coordinate remains uncertain after being labeled zero. A known origin alone does not establish the other constraints; see [the shared frame contract](../../integration/time-and-frames.md).

## Gaps to settle before complete user stories

| ID | Missing behavior / decision | Why it matters and proposed treatment | Coordination |
| --- | --- | --- | --- |
| GC-G01 | What is connected, and who receives each action? | Distinguish laptop→recorder file access, laptop→flight-controller mission/control, and controller→flight-controller takeover. A USB cable to a Pi does not by itself define networking, file transfer, or mission routing. Choose supported ports, endpoint software, power behavior, and reconnect procedure. | GC/FP/SA; IF-09/11/12/15 |
| GC-G02 | Is a shared RC radio actually a laptop telemetry link? | Verify bidirectional mission/ack/status support, ground-side laptop access, firmware, bandwidth, and simultaneous RC behavior. Handset battery/status telemetry alone is insufficient. A shared radio makes RC and telemetry loss potentially simultaneous; test that failure separately. | GC/FP/DT; IF-11/12/13 |
| GC-G03 | What does the planning map prove? | Use imagery with a route/waypoint overlay, scale, launch/landing areas, permitted corridor, and predicted sensor footprint. Support offline field use. Treat clicked sidewalk edges as approximate until independently referenced; record map source and any site alignment. Route precision cannot be inferred from zoom level. | GC/FP/PC |
| GC-G04 | How is the pavement referenced? | First decide whether precise centerline coordinates are needed at all: first-version flight does not require exact tracking. For findings, choose controls, checkpoints, GNSS support, and/or an aligned reconstruction. Include winding sections, heading/orientation, and geographic export. Keep alignment controls separate from accuracy checkpoints. | GC/PC/FP; Q-07/12 |
| GC-G05 | What do height and duration mean? | Distinguish above-launch altitude, height above pavement, and geographic altitude. Define route speed, curve/corner behavior, yaw, sensing width/overlap, and transit legs. Specify whether duration is an estimate, a hard maximum, or an instruction to stop/repeat; resolve conflicts between finishing the route and time/energy limits. | GC/FP/SA |
| GC-G06 | When is a plan really loaded? | Save plan ID/revision and aircraft identity; transfer to the flight controller and read back normalized mission fields. Verify recorder capture configuration against the same run identity. Distinguish saved locally, sent, accepted, verified, and ready. Editing a loaded plan invalidates verification. | GC/FP/SA; GC1/2 |
| GC-G07 | What happens between loading and launch? | Moving or rebooting the aircraft requires renewed checks of actual launch/home, current fix quality, mission identity, recorder readiness, and the safe path to waypoint one. Being near any point on the route is insufficient. Define the permitted launch area and maximum entry distance with uncertainty. | GC/FP/SA |
| GC-G08 | Who can start flight, and what does Start Run do? | Separate creating a recording session, preparing a mission, arming, and departing. Define pilot authority and the priority of RC versus app requests. Require a deliberate launch request after readiness checks; reject stale/duplicate launch requests and never auto-launch on reconnect. Acknowledged, executed, and completed are distinct outcomes. | GC/FP/SA/DT |
| GC-G09 | What is displayed during the flight? | Show aircraft identity, mode, route progress, live position quality, battery, link state, recording/storage health, faults, and age of each status. Define what remains visible on the controller if the laptop disconnects. Preserve actual versus commanded route/height. Exact centerline following is excluded, but sensing coverage still needs assessment. | GC/DT/FP/SA; DT1–3 |
| GC-G10 | What happens on interruption? | Define pause, resume, manual takeover, return, landing, low energy, position loss, recorder/sensor failure, and separate RC/GCS/laptop failures. Define which faults stop inspection versus flight. Include safe transit/return paths in operator review; obstacle responsibility includes turns, return, and landing. Mark partial coverage; do not claim an interrupted survey is complete. | GC/FP/DT/SA |
| GC-G11 | What is GC3 buffering? | Existing requirement asks for 60 s backlog before current stream data. Identify the stream and buffer endpoints. Proposed separation of historical replay from fresh control/health requires explicit requirement review; historical values must not appear current and old launch commands must not execute. | GC/DT; IF-14; Q-08 |
| GC-G12 | What does run completion mean? | Landing is followed by disarming, closing/flushing recordings, manifest finalization, coverage/fault summary, and orderly shutdown. Define restart/new-run behavior, incomplete logs after power loss, and association between planned mission, actual flight, and files. | GC/SA/PC/DT |
| GC-G13 | What does Extract Data guarantee? | Copy rather than implicitly delete onboard originals; show progress/free space, resume interrupted transfer, verify file sizes/hashes, and mark completeness. Define when deletion is allowed after a verified copy. PC3 already requires three ≥1 GB exports, each within 30 min. | SA/PC with GC UI; IF-15 |
| GC-G14 | What does Upload Data mean? | Separate drone→laptop extraction from laptop→cloud upload. Define endpoint, authentication, offline behavior, retry/resume, duplicate-run handling, upload confirmation, and whether processing is triggered. Keep credentials out of mission files/logs. Preserve a local usable copy while cloud scope is unresolved. | GC/RD/PC; Q-11 |
| GC-G15 | How is location quality established? | Record timestamped pose, source, frame, uncertainty, calibration, and invalid periods. If later processing revises poses, preserve originals and identify the revision used for findings. Agree independent checks and a pass fraction for the user's location target before calling it achieved. | PC/SA/FP/DT; S6/SA2/PC1/S3 |
| GC-G16 | How much application must be custom? | Compare an existing GCS for route editing and flight operations plus a small payload/run-management application against a single custom UI. A unified UI must still honor autopilot mission and command semantics. Laptop OS, offline resources, and field power remain unspecified. | GC/FP/RD |

## Direct answers to the proposed approaches

**Draw-a-path screen:** a satellite/aerial map with editable waypoints or a corridor is a reasonable starting UI. QGroundControl already documents map-based mission planning and upload; its planned home marker is only a planning aid, distinct from actual vehicle home [E1]. Use existing GCS behavior as a candidate before building a map editor. A measured site overlay can supply better alignment if later checks show that map placement is inadequate. This is an engineering proposal, not map-accuracy evidence.

**Pavement centerline:** a precise centerline is unnecessary unless flight/coverage tolerances demand one. For a winding sidewalk, let the operator sketch a polyline and inspect turns, corridor, and expected coverage. If geographic placement is insufficient, reference multiple site points/edges with a documented measurement method and evaluate independent checkpoints. A carefully drawn line cannot remove navigation or imagery-registration error. Choosing controls or RTK requires an error budget and cost review, not an assumed accuracy improvement.

**Local coordinates and camera tracking:** support local coordinates as a representation. Keep live camera-based navigation as an unverified option, separate from post-flight image pose estimation. ArduPilot's optical-flow documentation requires calibration, rangefinder checks, and estimator setup [E2]; it does not validate our camera/2D LiDAR as that stack. Image motion also depends on aircraft rotation, camera geometry, surface depth, and timing. Live odometry would need bounded latency, quality/drift detection, flight-controller integration, and a tested loss response. Offline pose improvement cannot control a flight that has already happened.

**Reuse the controller radio:** technically plausible for a specifically supported system. ExpressLRS documents a MAVLink mode and ground-station connectivity with hardware/firmware prerequisites [E3]. That is evidence of an available architecture, not compatibility of any candidate RC set. Decide on the complete flight/RC/recorder stack before eliminating a dedicated telemetry link.

## Proposed operational sequence to use when writing stories

1. Connect and identify aircraft, flight controller, and recorder; show which services are reachable.
2. Create a survey/run draft; obtain the map/site reference and define route, launch/landing areas, speed, height reference, acquisition configuration, and limits.
3. Validate the route and review time/energy/coverage estimates; transfer mission and acquisition configuration; verify both.
4. Disconnect and move to the launch area; reconnect required operational links or inspect the agreed controller status. Recheck home, position quality, mission identity, payload readiness, and flight limits.
5. Pilot deliberately starts the prepared mission; recording readiness is established before required survey coverage begins. Flight controller retains flight-control authority.
6. Monitor progress/health; handle takeover, interruption, and recovery with an explicit partial-coverage record.
7. Land/disarm, finalize recordings, and inspect completion/quality. Export and verify the survey package; optionally upload under the agreed cloud policy; shut down safely.

These are proposed states/actions, not finalized stories. Each story should specify actor, prerequisites, trigger, visible success, failure/recovery, and the evidence needed to verify it.

## Next decisions for discussion

1. Define whether the location target applies live or to final acquisition-time poses; settle the 1 m × 1 m convention and vertical reference. Keep flight-corridor adequacy and final finding accuracy separate.
2. Decide whether an existing GCS plus a payload application meets the desired UX, and select the complete firmware/RC/GCS candidate for a compatibility check.
3. Agree launch authority, recording readiness, default end/interruption behavior, and the meaning of the duration field.
4. Write stories across preparation, execution, recovery, extraction, and upload using the agreed behavior. Do not make unverified visual navigation a prerequisite for the baseline.

## Verification implications and evidence

Bench/simulation scenarios should include wrong aircraft/plan, partial upload, mismatched readback, reboot after loading, moved launch position, duplicate start, stale status, separate and shared link loss, recorder failure, interrupted export, duplicate cloud upload, and incomplete coverage. Confirm real hardware behavior later; simulation is not airborne acceptance. Preserve existing GC1/GC2/GC3, DT1, PC3, S6/SA2, FP2/FP3, and S3/PC1 criteria without relaxing them through this review.

External documentation reviewed October 28, 2026 is recorded in [the evidence note](../../references/new-evidence/2026-10-28-ground-control.md). Existing project requirements, interfaces, and frame contracts supply the project-specific bounds. No new mass, power, price, pinout, or throughput has been allocated; shared budgets and electrical interfaces remain unresolved.
