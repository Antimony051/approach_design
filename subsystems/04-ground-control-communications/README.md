# GC — Ground Control & Communications

Lead: **Pritam Adhikari**. Charter support: **Abhinav Dhakal**. Requirements: **GC1–GC3; S1, S4**.

## Current operational discussion — October 29, 2026

The [supervised mission operating design](supervised-mission-operation.md) records the agreed direction: waypoint surveys with pilot detours, proximity-triggered stopping/holding, explicit rejoin/resume, skipped sections, and premature ending with preserved partial data. The proximity implementation, sensing envelope, mode priorities, and degraded-positioning fallback remain unresolved. IMU attitude stabilization is not accepted as a reliable position hold. Post-processed acquisition-time references are permitted in principle, with live clearance still required and final accuracy subject to validation.

See [the workflow and gap review](operational-gap-review.md) for the initial planning/data-management discussion. The user proposes laptop-based planning, mission loading, deliberate launch, onboard-data extraction, and cloud upload, with wired/Bluetooth/shared-RC transports still candidates. Exact sidewalk-centerline tracking is not required for the first version. The desired mapping reference is approximately 1 m × 1 m horizontally and 20 cm vertically, with flexibility if downstream accuracy remains adequate; bound conventions remain open. This does not replace S3, PC1, or the timestamped pose/frame contract. Recorder choice remains open, including the user's Pi 4 example. No implementation is selected by this discussion.

## Required function

Define, transfer, and verify routes; carry operator commands/acknowledgements and status; support manual recovery and any selected GNSS correction delivery; define link-loss buffering and reconnection.

## Existing direction and evidence

Older plans favor PX4/QGroundControl; the H7 aircraft proposal instead uses ArduCopter. Select and test the actual firmware/GCS pairing. RC control, MAVLink mission/health, local sensor capture, and post-flight bulk transfer are distinct paths. Ordinary M10 GNSS is proposed for the X500/S500 choices. The original F9P rover concept requires an identified correction source; an RTK label does not supply corrections.

GC3 explicitly calls for up to 60 s of buffered stream data sent before new stream data. Which stream, rate, buffer endpoint, and reconnect ordering are not defined. Log a proposed interpretation for team review rather than pretending the contradiction with fresh health/control is solved.

## Work for the design agent

- Exact controller ports, GCS operating system/version, ground workstation availability, RC transmitter/receiver, telemetry pair/antennas/cables/power, and link budget/test plan.
- Determine whether navigation uses ordinary GNSS, local control markers/registration, RTK/PPK, or another method with FP/PC; include correction source/access/cost if used.
- Route files/readback, mission command support, return/takeover/failsafe behavior, and timestamped acknowledgement endpoint.
- Resolve GC3 with explicit bounded stream/rate/storage and freshness semantics shared with DT/SA.
- Select a physical post-flight export link with SA/PC; budget adapters and ground equipment.
- Record site/pilot/authorization dependencies from existing requirements and identify operational equipment still needed.

## Required design handoff

Use [the research template](../../templates/research-note.md) for options/evidence, then maintain the selected implementation here. Include exact parts and configuration, rationale, inputs/outputs, installed mass/power/dimensions where applicable, interfaces, failure behavior, assembly/calibration needs, verification, and open decisions. Mark the design status explicitly; the initial status is **implementation unresolved**.

Write purchasing lines into [the shared BOM](../../procurement/bom.csv); write connection details into [interfaces](../../integration/interfaces.csv). Update [power](../../integration/power-budget.csv), [fit/mass](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), and [decisions](../../decisions/decision-log.md) when this subsystem changes them. Cross-reference shared components instead of duplicating them.

## Starting references

- SRC-005: locate in [the source index](../../references/source-index.md).
- SRC-024: locate in [the source index](../../references/source-index.md).
- SRC-008: locate in [the source index](../../references/source-index.md).
- SRC-028: locate in [the source index](../../references/source-index.md).
