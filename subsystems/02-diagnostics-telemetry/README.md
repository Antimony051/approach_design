# DT — Diagnostics & Telemetry

Lead: **Shisir Baral**. Charter support: **Ankit Dhakal**. Requirements: **DT1–DT3; S1, S4, S6**.

Updated November 16, 2026. **Status: recorder HealthMonitor and Pocket alert destination selected in SRC-034 §3.3.2; forwarding/display integration unverified.**

## Required function

Report battery, acquisition, storage, and mode; identify stream gaps, sensor loss, and invalid/missing pose; retain faults with exported evidence.

## Selected approach and alternatives

HealthMonitor on the Raspberry Pi 4 consumes capture counters/state transitions, avoiding bulk-file rereads. It records field/value/units, source ID/time, sequence, validity, severity, and persistent events. Ground StatusModel retains newest valid samples and calculates age. Loss of recorder heartbeat must be distinguishable from a healthy payload.

**RadioMaster Pocket 2.4 GHz ELRS** is the primary immediate critical-alert display; the laptop provides detailed status/review over separate MAVLink telemetry. Proposed short warnings: LOW BATTERY, LIDAR LOST, CAMERA LOST, STORAGE LOW, POSE INVALID. Pocket's source-listed price is $71.50 and its display 128 × 64; Boxer and TX16S Mark II were considered but offer no necessary benefit for this short-warning role at their higher source prices. These are document inputs, not current quotes.

A software bridge must carry recorder faults through **MicoAir/PX4 → RP1 V2/ELRS → Pocket/EdgeTX** in a supported format. Exact protocol, firmware versions, field mapping, bridge, and display script remain open (Q-19/COMP-19). Cited Lua/Yaapu references do not prove this path works. Manual RC and handset telemetry share a radio failure path; laptop MAVLink is separate. FP retains aircraft recovery responsibility.

## Freshness and verification

Persist timing validity from SRC-036: PTP lock loss/relock, clock steps/restart, invalid boot/realtime or FC mapping segments, sensor sequence gaps and missing timestamp/pose metadata. Record source clock/segment IDs and do not label a sync-status flag as measured end-to-end accuracy. Delivery through Pocket remains the separate Q-19 integration task; timing events do not automatically command flight control.

Mark stale/unavailable readings explicitly. Reconnect must not present old battery or fault values as current. Persist local events even if delivery fails; GC3's undefined historical backlog must not displace fresh control/health without an agreed interpretation.

Instrument recorder fault time, forwarded timestamps, Pocket display time, laptop display time, and recovery. Verify DT1's ≥90% ≤4 s over ≥10 min with ≥300 updates/field, >1 s gap detection, sensor loss, invalid pose, recorder heartbeat loss, and simultaneous RC/alert interruption. A local demo display and emulated battery/mode remain permitted by SRC-006/007 if labeled; that does not establish the installed handset path. Pritam supports implementation under Shisir's review; ownership is unchanged.

Historical leads: SRC-006/007/023/024.

## Shared design records

Maintain one owning row per component in [the BOM](../../procurement/bom.csv), exact connections in [interfaces](../../integration/interfaces.csv), and affected [power](../../integration/power-budget.csv), [mass/fit](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), [verification](../../verification/plan.md), and [decisions](../../decisions/decision-log.md). Design selection is not purchase authorization or test evidence. Blank installed/price values remain unknown.

Current source: [SRC-034 final approach](../../references/new-evidence/2026-11-16-final-approach/PaveWatch_Approach_Final.docx), [readable text SRC-035](../../references/new-evidence/2026-11-16-final-approach/approach-text.txt), and [reconciliation](../../references/new-evidence/2026-11-16-final-approach.md). Earlier source IDs resolve through [the source index](../../references/source-index.md).
