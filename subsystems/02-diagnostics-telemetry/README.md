# DT — Diagnostics & Telemetry

Lead: **Shisir Baral**. Charter support: **Ankit Dhakal**. Requirements: **DT1–DT3; S1, S4, S6**.

## Required function

Report battery, acquisition, storage, and flight mode to the operator; detect stream gaps, sensor loss, and missing/invalid pose; retain faults in exported evidence.

## Existing direction and evidence

The ground-demo plan uses real acquisition/storage status and explicitly emulated battery/mode if no aircraft is ready. A local transport/display is acceptable for that demo. Pritam implements/supports diagnostics tests under Shisir's review; ownership stays with Shisir. No specific airborne aggregation hardware or health transport has been frozen.

## Work for the design agent

- Identify each real health source, units, event ID/time, rate, age/stale rule, and operator display endpoint.
- Decide whether aggregation runs on recorder, ground station, or both, and its behavior if recorder/link fails.
- Map battery current/voltage sensing and flight-state acquisition with FP; map payload status and faults with SA.
- Specify transport/bandwidth, queueing, timestamps, disconnect/recovery, and persisted warning format with GC/RD.
- Define fault-injection and end-to-display latency instrumentation; include any actual test hardware in the BOM.
- Distinguish health freshness from GC3's historical buffered stream; do not silently replay old values as current.

## Required design handoff

Use [the research template](../../templates/research-note.md) for options/evidence, then maintain the selected implementation here. Include exact parts and configuration, rationale, inputs/outputs, installed mass/power/dimensions where applicable, interfaces, failure behavior, assembly/calibration needs, verification, and open decisions. Mark the design status explicitly; the initial status is **implementation unresolved**.

Write purchasing lines into [the shared BOM](../../procurement/bom.csv); write connection details into [interfaces](../../integration/interfaces.csv). Update [power](../../integration/power-budget.csv), [fit/mass](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), and [decisions](../../decisions/decision-log.md) when this subsystem changes them. Cross-reference shared components instead of duplicating them.

## Starting references

- SRC-006: locate in [the source index](../../references/source-index.md).
- SRC-007: locate in [the source index](../../references/source-index.md).
- SRC-023: locate in [the source index](../../references/source-index.md).
- SRC-024: locate in [the source index](../../references/source-index.md).
