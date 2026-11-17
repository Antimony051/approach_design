# GC — Ground Control & Communications

Lead: **Pritam Adhikari**. Charter support: **Abhinav Dhakal**. Requirements: **GC1–GC3; S1, S4**.

Updated November 16, 2026. **Status: PX4/QGroundControl, Pocket/RP1 V2, and separate laptop MAVLink telemetry selected in SRC-034 §§3.3.4/3.4.1; exact radio/ports and custom application remain open.**

## Required function

Prepare/verify missions, carry commands/acknowledgements and status, support manual recovery, manage link loss, and coordinate integrity-checked extraction/upload.

## Selected approach and alternatives

Use QGroundControl with the **MicoAir H743v2-AIO-35A / PX4 1.16.0** and **M10G GNSS/compass**. **RadioMaster Pocket 2.4 GHz ELRS ↔ RP1 V2** provides pilot commands and intended handset alerts. The laptop uses a **separate MAVLink telemetry connection** for mission upload/readback, acknowledgements, and detailed status. Choose its actual radios, antennas, serial rates, power and host cables; avoid FC UART conflicts with recorder, receiver, and GNSS.

The source compares separate RC/telemetry, supported shared RC/MAVLink, and optional nearby Bluetooth service. Its Level 2 design retains separate laptop telemetry; a shared radio is an alternative requiring an explicit revision. A handset alert link does not automatically provide a laptop mission connection. Post-flight bulk data remain separate from in-flight radios.

## Recorder maintenance connection — SRC-039–042

[The Pi access guide](../../integration/raspberry-pi-access.md) documents recorded November16 Tailscale/OpenSSH service access: `picoscan-pi` / `100.72.89.22`, port22, with the trusted host fingerprint, individual Tailscale invitations and shared **pavewatch** SSH login using the **private key supplied by Shisir** (D-026/SRC-045–046). The Pi OS hostname is `raspberrypi`. The original administrator's shortcut/key and wired link-local profile are laptop-specific; client-visible shared addresses can differ.

This is recorder setup/development access, separate from the selected RC and flight-controller MAVLink paths. The source records no advertised subnet routes; SSH does not establish remote SOPASair access. Bulk export can be evaluated over an appropriate path later, but recorded shell success does not pass PC3 or select its transport. The source guides record existing administrator login, not completed key distribution or fully verified team-member connectivity. No new remote connection or account changes were made here.

## Operator workflow and authority

The laptop supports **Plan Run, Extract Data, Upload Data**. QGroundControl plus a small custom run/export app is the starting architecture; a unified UI remains an alternative. Upload a plan, read it back, and verify aircraft/run identity and recorder configuration. At the real launch site recheck home/fix, energy, links, recording, storage, and entry path. Recording and arming remain separate; pilot approval is required for takeoff. Reconnect or delayed commands must not launch automatically.

Track mode, progress, battery/link/position quality, recording/storage, and age. Pause/resume/takeover/return/landing create explicit events and partial-coverage records. Post-flight extraction verifies inventory/bytes/hashes before upload; cloud-report upload may wait for internet without blocking capture or local package preservation.

## Retained operating decisions and gaps

The [October 29 operating design](supervised-mission-operation.md) retains pilot detours, skip/early-end support, deliberate rejoin/resume, and desired proximity stopping/holding. Map it onto **PX4**, since historical ArduPilot examples are not implementation evidence. Proximity hardware, mode priorities, measured clearance/stopping/hold, and degraded-positioning/combined-failure responses remain open; no IMU-only position hold is established.

The [initial gap review](operational-gap-review.md) remains workflow background. Exact sidewalk-centerline tracking is unnecessary. The approximate **1 m × 1 m horizontal / 20 cm vertical** reference preference has unresolved confidence/datum semantics and does not replace S3/PC1. Post-processed acquisition-time references are permitted with independent checks; live flight clearance still needs suitable positioning.

Resolve **GC3**'s undefined 60 s buffered stream, endpoints, capacity, and backlog ordering while keeping stale health/commands from appearing current. Preserve FP2's **1–2 m/s** acceptance condition pending reconciliation with the approach's **0.25–1 m/s** plan. Select physical export/service paths and actual laptop/field power. Any RTK alternative still needs a real correction source and separate budget.

Historical leads: SRC-005/008/024/028 and October 28–29 evidence notes.

## Shared design records

Maintain one owning row per component in [the BOM](../../procurement/bom.csv), exact connections in [interfaces](../../integration/interfaces.csv), and affected [power](../../integration/power-budget.csv), [mass/fit](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), [verification](../../verification/plan.md), and [decisions](../../decisions/decision-log.md). Design selection is not purchase authorization or test evidence. Blank installed/price values remain unknown.

Current source: [SRC-034 final approach](../../references/new-evidence/2026-11-16-final-approach/PaveWatch_Approach_Final.docx), [readable text SRC-035](../../references/new-evidence/2026-11-16-final-approach/approach-text.txt), and [reconciliation](../../references/new-evidence/2026-11-16-final-approach.md). Earlier source IDs resolve through [the source index](../../references/source-index.md).
