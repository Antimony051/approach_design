# Task brief for the next design agent

Use this workspace to develop a complete, compatible PaveWatch hardware design and purchasing package. Start with the source guide and current-state files. The required subsystem functions are defined; implementation, component choices, and fit remain open.

## Inputs and scope

Design the whole operating system: aircraft/propulsion/control/navigation, payload sensors, acquisition computer/storage, power distribution, mechanical installation, ground control/radios, diagnostics, post-flight transfer, processing/reporting hardware, and equipment required to commission and demonstrate it. Distinguish airborne, ground/demo, fabrication, spare, already-owned, challenge-supplied, and recurring items. Software choices matter where they constrain hardware interfaces; no application implementation is requested by this task brief.

Respect the under-$700 complete-aircraft ceiling. Do not apply that ceiling to the complete project or silently assume older $999/$1,000 estimates remain funded. Use the 650 g payload target and 800 g planning case as allocations to check, not established lift capability. Preserve 10-minute loaded flight and 20% calibrated usable-energy reserve as acceptance targets.

The latest planning direction is X500 v2 ARF/Kakute H7 Mini v1.5, Orange Pi Zero 3, and an InnoMaker color USB camera. Investigate that combination's actual feasibility. Compare alternatives where needed, including the original F450 concept. A different recommendation should explain the consequence for cost, compatibility, power, fit, timing, and testing. Do not merge the older Pixhawk/PX4/Pi 5/CSI design with the H7/USB design without explicitly revising its interfaces.

## Required outputs

1. Update each subsystem brief with a justified implementation, alternatives considered, exact component revisions/modes, evidence, and outstanding tests.
2. Complete procurement/bom.csv with manufacturer part numbers, exact variants, quantities, kit inclusions, suppliers/links, checked dates, unit and extended prices, shipping/tax allocation, availability, lead times, and the reason for each item. Include cables, connectors on both ends, mounting hardware, cooling, boot media, power protection, chargers/leads, test fixtures, and any required operating hardware. Identify owned/supplied/borrowed equipment honestly.
3. Complete procurement/compatibility.csv and integration/interfaces.csv with evidence for all connections, firmware support, voltage and current limits, bandwidth, timestamps, connector genders/keying/pin numbers, and port conflicts. Mark pending physical tests.
4. Complete power-budget.csv and mass-and-fit.csv. Provide a dimensioned layout showing actual component placement, cable exits/bends, fasteners, optics, battery, center of gravity, landing clearance, and service access. Produce editable diagrams/CAD where useful. Do not replace fit evidence with an overall liters calculation.
5. Finish integration/assembly-plan.md with the interaction description, wiring diagram, pin map, assembly sequence, configuration/software version list, and commissioning steps for the selected build. Include startup, recording, landing, shutdown, disconnects, and recovery.
6. Reconcile procurement/cost-summary.csv with a single configuration and available funds. Separate aircraft, recording payload, ground/demo equipment, fabrication/spares, tax/shipping, contingency, and recurring services. Explain any unmet ceiling or unpriced item.
7. Update verification/plan.md and its matrix to connect the design to requirements and the ground-demo scope. Identify equipment and independent references needed, without inventing measured results.
8. Deliver a concise recommendation and purchase-readiness report: chosen configuration, full delivered totals, quantities, compatibility evidence, fit/power/mass margins, unresolved dependencies, and decisions for the team. Update decisions/decision-log.md throughout.

Ask focused questions when a missing decision prevents progress; continue work on independent areas. Sensor variant/accessories, current whole-project funding, and owned equipment/charger details are early information gaps. Existing documents are evidence leads, not permission to purchase or evidence of tested performance.
