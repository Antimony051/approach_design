# Shared integration record

These worksheets connect subsystem choices into one installed system. They are initially seeded from functions and existing allocations, with no newly verified electrical or mechanical design.

- [interfaces.csv](interfaces.csv): from/to, physical connector/pin assignment, protocol, logic/power, bandwidth, timing, and failure semantics. TBD means unresolved.
- [power-budget.csv](power-budget.csv): load rails, typical/peak/startup draw, conversion losses and measurement/evidence. Blank values are unknown; size regulators and upstream conductors from combined loads and transients.
- [mass-and-fit.csv](mass-and-fit.csv): existing payload allocations, installed masses, dimensions, placement, and clearances. Retain evidence for both mass and shape.
- [time-and-frames.md](time-and-frames.md): capture-time semantics, pose sources, clock mappings, calibration, and frame definitions.
- [assembly-plan.md](assembly-plan.md): future complete wiring, layout, operational interactions, and commissioning sequence.

One interface can require several BOM rows: mating plugs, cable, crimps, strain relief, adapter, protection, and fabrication. Map every physical interface to its procurement items and every part to its mounting/power needs.
