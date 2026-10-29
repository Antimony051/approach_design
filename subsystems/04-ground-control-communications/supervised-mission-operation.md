# Supervised mission operation and interruption handling

Updated October 29, 2026 from the ground-control design discussion. **Agreed operating direction; implementation and numerical acceptance limits remain open.** This document records the discussion before detailed user stories. No aircraft, proximity system, estimator, control mode, or software integration has been selected or tested here.

The [initial workflow and gap review](operational-gap-review.md) retains the broader laptop/communications/data-management discussion. This document refines its navigation, obstacle handling, interruption, and recovery behavior. It does not replace the existing [requirements](../../system/requirements.md).

## Agreed scope and rationale

- Use supervised waypoint survey flight with deliberate pilot takeover for obstacle detours. Autonomous obstacle negotiation is outside the initial operating baseline.
- Exact sidewalk-centerline tracking is unnecessary. More accurate acquisition-time references may be estimated after collection; successful recovery is conditional on adequate recorded evidence and validation, not guaranteed.
- Live positioning must still support flight clearance and the chosen operating corridor. Post-processing cannot repair an unsafe flight or create missing coverage.
- Support skipping an obstructed section and ending the run early whenever continuation is not possible or the pilot elects to stop. Continuous coverage is not mandatory; retain a truthful incomplete-coverage record.
- Proximity detection must trigger interruption, controlled stopping, and an attempted hold, rather than only a notification. This is a desired system behavior whose implementation remains unverified. A confirmed hold requires valid supporting estimates.
- Seek useful proximity coverage within available hardware resources; do not promise complete detection in every direction. Document actual field of view, blind areas, detectable obstacle types/sizes, and allowed motion in the tested envelope.
- Pilot detours, explicit resumption, visible control authority, data-quality marking, remaining-energy checks, and separate return-path review were accepted as useful parts of the design.
- IMU-based stabilization was suggested by the user as a possible positioning-loss fallback. It is an **unverified proposal**, not an agreed position-holding capability; see the distinction below.

## Accuracy and obstacle clearance

There are three separate questions: can the aircraft navigate the flight corridor, can recorded samples be referenced at acquisition time, and can final findings meet their location/geometry requirements? The user's approximate 1 m × 1 m horizontal and 20 cm vertical reference target is intended for mapping and may be addressed after collection. Its box convention, vertical reference, pass fraction, and acceptable uncertainty still need definition. S3 and PC1 remain in force unless explicitly revised.

Waypoint planning alone can be adequate when the obstacle clearance is sufficiently large and validated for the installed system. It cannot establish a safe close pass merely because the waypoint line avoids a tree on a map. Clearance review must include:

- Obstacle/map registration uncertainty, including branches at the flight altitude rather than just the trunk location.
- Actual aircraft position error and path-tracking deviations, using an error budget that avoids counting the same error twice.
- Aircraft/propeller extent, turn rounding, stopping distance, wind, and an additional operating margin.
- The entry, detour, rejoin, return, and landing trajectories, including their altitude changes.

The FP2 allowance of 2 m horizontal error for ≥90% of specified samples is not an obstacle-clearance guarantee: the remaining deviations are not bounded by that criterion. ArduCopter documents curved transitions between waypoints; a drawn corner is not necessarily the flown trajectory [O1]. No minimum clearance or default GPS accuracy is asserted for our untested build.

## Operator workflow

1. **Connect and prepare.** Use the laptop to identify the aircraft/controller/recorder, create a run, plan route/height/speed/limits, and verify the deployed mission and recording configuration. Preserve the earlier workflow's map, transfer, identity, and readiness checks.
2. **Move and recheck.** At the actual launch site recheck home, position quality, mission identity, entry path, RC/telemetry, energy, storage, and acquisition readiness. Loading the plan elsewhere is not flight authorization.
3. **Start deliberately.** Create the recording session and establish required acquisition readiness before survey coverage begins. Arming and departure are distinct actions. The flight controller owns flight control.
4. **Survey under supervision.** Display actual mode, control authority, active target/segment, paused/running state, link and estimator quality, battery, recording/storage health, and status age.
5. **Interrupt.** Pilot takeover pauses mission progression. A proximity event also requests interruption and stopping; report the measured state and whether hold is actually established. Do not wait for a laptop round trip to provide the intended immediate response; the onboard integration must be verified.
6. **Pilot detour.** Pilot explicitly selects the validated assisted control mode and maneuvers around the obstruction. Neutral sticks do not restart the mission; position holding is conditional on valid estimates and mode behavior.
7. **Choose the outcome.** Skip a section and rejoin, continue holding while deciding, or end the survey. Holding consumes energy and cannot be indefinite. Fault/energy responses can preempt ordinary continuation.
8. **Resume explicitly.** Pilot reaches a clear entry area beyond the obstruction, selects/reviews the remaining mission segment, and confirms the rejoin trajectory, altitude, heading, estimator quality, acquisition health, and remaining reserve. A separate resume action is required. Clearing a sensor, reconnecting a link, or releasing sticks must not automatically resume.
9. **Finish or end early.** Stop further survey progression and execute an appropriate pilot-reviewed recovery/landing procedure. Ending a survey is not an instruction to disarm in flight or necessarily to land immediately beneath the aircraft. Review return-path clearance separately.
10. **Finalize and export.** After landing/disarming, finalize the recordings and summary; integrity-check extraction to the laptop, handle cloud upload under the chosen policy, and shut down orderly. Keep partial data and the reason/extent of any incomplete survey.

## State and authority contract

These are logical application states; exact autopilot modes and commands are unresolved. An application must not label a requested transition as an achieved aircraft state.

| State | Required observed behavior / exit |
| --- | --- |
| Prepared | Mission and recording configuration verified; departure still requires launch-site readiness and a deliberate request. |
| Surveying | Mission is executing; pilot can deliberately take over. Proximity/other qualifying faults interrupt survey progression. |
| Stopping / hold requested | Mission is paused and stopping is requested; monitor motion and estimator validity before declaring a hold. |
| Holding | Validated control maintains position within a yet-to-be-defined bound. Clearing an obstacle alone cannot exit this state into Surveying. |
| Pilot control | Mission remains paused. Pilot maneuvers using the validated control mode; neutral sticks do not transfer authority. |
| Rejoin review | Selected continuation and entry path are checked. Selection changes or degraded health invalidate readiness to resume. |
| Ending / recovering | No further survey continuation; recover/land under the applicable procedure while retaining available data. |
| Finalized | Flight has ended, files have been closed/recovered, and coverage/outcome is summarized. Export/upload may still be pending. |
| Degraded navigation | Hold cannot be relied on. Display the actual fault/state; inhibit ordinary mission resumption and use a separately validated fallback. Exact fallback remains open. |

Ordinary mission commands must not silently undo takeover or a proximity stop. Exact priorities among pilot commands, proximity intervention, low-energy actions, link failsafes, and estimator failsafes require a selected-stack authority table and testing; pilot authority is not a promise that every failsafe permits unrestricted control.

## Rejoining and skipping

ArduPilot documents that normal resumption can head directly to the last active waypoint. That path may cross the obstacle after a manual detour. Rewind-on-resume can revisit earlier track and also needs clearance review [O2]. These are examples of stack behavior, not the selected implementation.

The preferred first-version procedure is a pilot-controlled detour to a clear entry area beyond the obstruction, review of an appropriate remaining segment, and explicit resumption. Selection of the next waypoint must account for associated non-navigation commands, altitude transitions, headings, and acquisition actions. Do not implement a blind waypoint-index increment or assume the original route will be retraced.

Preserve the original plan; log the active plan revision, selected continuation, skipped interval/segment, interruption cause, and actual trajectory. A skipped segment must not be marked inspected merely because the aircraft passed near it during a detour. An uncertain gap may initially be marked by time/segment and refined during processing. A later reflight must be a deliberate operation.

## Proximity and positioning limitations

**Detection and response are separate capabilities.** Define relevant obstacles, coverage geometry, minimum detectable size, valid range, update rate, data age, false returns, and sensor-failure detection. Cover planned directions of motion, including vertical motion where needed; a horizontal ring does not establish protection against overhanging branches. Do not assume the payload picoScan also supplies collision protection without a suitable installed view and validated integration.

**Stopping takes distance.** Allocate sensing/processing/control delay and braking distance at the loaded aircraft's speed, with propeller extent and uncertainty/margin. Validate against the actual load and conditions. DT1's display latency and GC2's ordinary command-ack latency are not collision-response timing budgets. Thresholds and speed limits remain unknown.

**Protection is mode-specific.** Verify survey, assisted pilot flight, stopping/holding, rejoin, return, takeoff, and landing individually. ArduPilot's simple avoidance documentation distinguishes Loiter/AltHold behavior from AUTO/GUIDED avoidance, and some modes allow pilot inputs to overcome avoidance [O3]. An enabled sensor is not proof that our desired stop-and-hold policy exists in all modes. Repeated triggering, safe motion away from an obstacle, sensor disagreement, and any protection-disable procedure remain implementation questions.

**IMUs can support attitude stabilization, not a dependable geographic hover by themselves.** Leveling roll/pitch does not cancel existing horizontal velocity or wind-driven drift. Integrating imperfect accelerometer measurements into velocity/position accumulates error; attitude error also affects gravity compensation. Keeping height additionally needs a supported vertical estimate, normally with aiding. ArduPilot's Stabilize self-levels but requires pilot drift/throttle correction; AltHold adds altitude control using additional estimation. Brake explicitly requires a valid position estimate [O4–O6]. Thus IMU-only stabilization cannot be documented as a proven obstacle-safe hold.

If positioning becomes invalid, distinguish that event from ordinary obstacle holding. Possible fallbacks include a validated pilot-controlled attitude/altitude mode or another supported local-position source; neither is selected here. Proximity ranges alone do not establish a complete velocity/position estimate. Show degraded navigation, block ordinary resumption, and define how the pilot recovers or lands. If both positioning and RC are lost, there may be no valid hover or pilot fallback; that combined-failure response needs explicit investigation.

## Data, faults, and resource implications

Continue recording during interruption where hardware health permits. Tag survey/pilot/transit periods, mode changes, requests and acknowledgements, proximity events and validity, pose quality, interruptions, selected targets, skipped coverage, and final outcome using the shared time/frame contract. Preserve originals if post-processing revises the poses. Recorded footage is not automatically acceptable survey evidence.

Use explicit outcomes such as completed, completed with skipped sections, and ended early, with separate quality/completeness and file/export/upload status. Warn when pose or sensing data cannot support a downstream result; do not interpolate gaps as measured coverage. Reassess energy after detours and validate safe return paths independently, including link-loss and low-energy returns.

Keep the six subsystem boundaries: FP owns aircraft control/estimators/failsafes; GC owns mission/operator commands and operational UI; DT owns fault/health observability; SA owns recording and sensor integration; PC/RD consume referenced evidence, gaps, and outcomes. Shared exchanges are in [interfaces](../../integration/interfaces.csv), particularly IF-09/11/12/13/16/19.

Additional proximity sensors, interfaces, wiring, mounts, and processing will affect aircraft cost, power, ports, installed mass, center of gravity, and endurance. No specific parts or numerical allocations are selected. Do not assume free capacity or that the existing under-$700 aircraft allocation accommodates them; complete the affected BOM/budgets/fit checks once candidates exist.

## Next refinement and verification

1. Choose a controller/firmware candidate and map logical takeover, stop/hold, pilot detour, resume, and recovery onto supported modes. Check whether the proximity response requires additional integration.
2. Define the actual sensing/flight envelope and mode/authority priorities, including estimator loss, stale sensors, RC/GCS loss, and simultaneous faults.
3. Define clearance, response/stopping limits, hold tolerance, return reserve, and rejoin acceptance against measurable evidence. No untested numerical bound is supplied here.
4. Exercise wrong-target resume, unchanged obstacle, cleared obstacle without resume, duplicate/stale commands, blocked return path, skipped coverage, early ending, estimator failure, and sensor failure in simulation/bench work before suitable controlled hardware tests. Simulation does not establish real obstacle detection or loaded stopping performance.
5. Convert the agreed workflow into actor-based user stories once those operational choices are sufficiently clear. The [verification plan](../../verification/plan.md) tracks the proposed checks; [documentation evidence](../../references/new-evidence/2026-10-29-supervised-missions.md) records source support and limitations.
