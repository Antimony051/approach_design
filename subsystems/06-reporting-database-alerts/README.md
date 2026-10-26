# RD — Reporting, Database & Alerts

Lead: **Saugat Karki**. Charter support: **Pritam Adhikari**. Requirements: **RD1; S2–S5**.

## Required function

Show findings with supporting images, available geometry/units, local or geographic location, and data/reference warnings; retain survey/result relationships for human review.

## Existing direction and evidence

Existing research proposes survey files plus SQLite, portable reports, and optional cloud hosting. The application integration plan instead describes post-flight private cloud processing. Current hardware needs for a local reviewer workstation versus hosted service are not frozen. A previous survey must not be required to review a current survey. No notification service or paid cloud provider has been selected.

## Work for the design agent

- Define minimum processing-to-report evidence fields and warning persistence with PC/DT; distinguish local metric position from valid geographic output.
- Inventory the actual operator/reviewer/processing computer(s) and peripherals; do not count one shared machine as several purchases.
- Decide local/hosted demonstration approach, storage/backup requirements, transfer path, network dependence, and any recurring services.
- Specify software/OS/resource constraints only as needed to choose hardware; do not add an enterprise platform to satisfy a simple review demo.
- Supply display/export verification and evidence packaging needs, including the real source data required for three ≥1 GB exports.

## Required design handoff

Use [the research template](../../templates/research-note.md) for options/evidence, then maintain the selected implementation here. Include exact parts and configuration, rationale, inputs/outputs, installed mass/power/dimensions where applicable, interfaces, failure behavior, assembly/calibration needs, verification, and open decisions. Mark the design status explicitly; the initial status is **implementation unresolved**.

Write purchasing lines into [the shared BOM](../../procurement/bom.csv); write connection details into [interfaces](../../integration/interfaces.csv). Update [power](../../integration/power-budget.csv), [fit/mass](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), and [decisions](../../decisions/decision-log.md) when this subsystem changes them. Cross-reference shared components instead of duplicating them.

## Starting references

- SRC-006: locate in [the source index](../../references/source-index.md).
- SRC-007: locate in [the source index](../../references/source-index.md).
- SRC-027: locate in [the source index](../../references/source-index.md).
- SRC-029: locate in [the source index](../../references/source-index.md).
