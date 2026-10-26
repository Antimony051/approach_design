# FP — Flight Platform, Power & Control

Lead: **Ankit Dhakal**. Charter support: **Aalok Uprety**. Requirements: **S1, S6, FP1–FP4**.

## Required function

Fly the complete acquisition payload, execute supervised survey legs, permit operator takeover, provide timestamped pose, and supply power to the other airborne systems.

## Existing direction and evidence

SRC-003 slides 13–15 and SRC-004 favor X500 v2 ARF + Kakute H7 Mini v1.5 as the aircraft planning choice. SRC-008 also compares S500 DIY and S500/Pixhawk configurations. The presentation retains the original F450/SpeedyBee/F9P concept; SRC-010's generic $405 estimate is not a compatible, released BOM. Research figures are $657.17 X500 DIY, $587.17 S500 DIY, and $669.20 S500 development kit before shipping/tax, with charger qualifications. Do not treat them as current quotes.

The H7 proposal uses ArduCopter with a revision-specific target; the older application proposes Pixhawk/PX4. These are separate configurations. SRC-008 includes an on-paper H7 port map and power/current constraints that must be checked against the actually selected revisions. Motor size alone does not establish KV/voltage/prop/ESC compatibility. Published takeoff mass is not additional payload capacity.

## Work for the design agent

- Exact aircraft/controller/firmware/GCS and GNSS/compass/RC/radio combination, with kit inclusions and all harnesses.
- Complete takeoff mass and loaded power/endurance estimates, installed payload allowance, current bottlenecks, and calibrated battery monitoring.
- Power tree for propulsion, control/peripherals, sensor, and recorder; regulator/BEC interaction, grounds, protection, startup, and shutdown.
- Exact mechanical interfaces, battery placement, controller adapter, landing clearance, and payload load paths with SA.
- 4S charging arrangement and delivered aircraft cost under $700; inventory the owned 2S equipment without assuming compatibility.
- Port allocation with GC/SA/DT; independent pose/attitude reference plan with PC.

## Required design handoff

Use [the research template](../../templates/research-note.md) for options/evidence, then maintain the selected implementation here. Include exact parts and configuration, rationale, inputs/outputs, installed mass/power/dimensions where applicable, interfaces, failure behavior, assembly/calibration needs, verification, and open decisions. Mark the design status explicitly; the initial status is **implementation unresolved**.

Write purchasing lines into [the shared BOM](../../procurement/bom.csv); write connection details into [interfaces](../../integration/interfaces.csv). Update [power](../../integration/power-budget.csv), [fit/mass](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), and [decisions](../../decisions/decision-log.md) when this subsystem changes them. Cross-reference shared components instead of duplicating them.

## Starting references

- SRC-008: locate in [the source index](../../references/source-index.md).
- SRC-010: locate in [the source index](../../references/source-index.md).
- SRC-020: locate in [the source index](../../references/source-index.md).
- SRC-028: locate in [the source index](../../references/source-index.md).
