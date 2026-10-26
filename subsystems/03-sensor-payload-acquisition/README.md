# SA — Sensor Payload & Data Acquisition

Lead: **Abhinav Dhakal**. Charter support: **Saugat Karki**. Requirements: **SA1–SA3; S3–S6**.

## Required function

Record real LiDAR and image streams concurrently, retain capture timing and pose association, detect continuity problems, and produce a replayable survey package for offboard analysis.

## Existing direction and evidence

The supplied sensor has not been confirmed received; exact variant/licenses/plug/accessories are unknown. Existing material proposes a transverse downward LiDAR scan plane, nadir camera, rigid camera/LiDAR relationship, and Ethernet packet capture. An initial 15 Hz / 0.33° and ±30° useful sector are proposals subject to the delivered sensor.

Latest MSDR planning choice: Orange Pi Zero 3 + expansion board, USB InnoMaker U20CAM-1080P, external SSD. Alternatives include Pi 4, Pi Zero 2 W with hub, other USB cameras, and older Pi 5/CSI plans. The Arducam B0495 full mode requires USB 3 per the MSDR; the OV9281 option is monochrome and changes the color plan. Exact InnoMaker mode/lens/timing remains unresolved. Global shutter does not eliminate exposure blur. Raw compute/camera notes contain optimistic and inconsistent claims; use them as leads.

## Work for the design agent

- Receipt inventory: sensor part number, firmware/licenses, plug, connector pinout, cables, supplied accessories, usable scan modes, timestamp access, optional PTP/IMU.
- Joint camera/recorder/storage/OS decision, exact board revisions, expansion compatibility, USB/CSI bus layout, encoding, boot media, drivers, timing metadata, and measured-demand benchmark plan.
- Exact SSD/cable/mount, regulator/cooling/protection, sensor power and Ethernet harness, and installed mass/volume/power.
- Rigid sensor layout, clear useful scan/camera fields, lens/focus/exposure selection, cable bends and service access with FP.
- Raw files, sequence counters, per-frame timing, session manifest, clock mapping and calibration IDs; pose/reference inputs with PC.
- Independent timing/range fixtures and stand/manual-carriage hardware for the ground demo, including a laptop-recorder fallback.

## Required design handoff

Use [the research template](../../templates/research-note.md) for options/evidence, then maintain the selected implementation here. Include exact parts and configuration, rationale, inputs/outputs, installed mass/power/dimensions where applicable, interfaces, failure behavior, assembly/calibration needs, verification, and open decisions. Mark the design status explicitly; the initial status is **implementation unresolved**.

Write purchasing lines into [the shared BOM](../../procurement/bom.csv); write connection details into [interfaces](../../integration/interfaces.csv). Update [power](../../integration/power-budget.csv), [fit/mass](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), and [decisions](../../decisions/decision-log.md) when this subsystem changes them. Cross-reference shared components instead of duplicating them.

## Starting references

- SRC-006: locate in [the source index](../../references/source-index.md).
- SRC-007: locate in [the source index](../../references/source-index.md).
- SRC-011: locate in [the source index](../../references/source-index.md).
- SRC-012: locate in [the source index](../../references/source-index.md).
- SRC-021: locate in [the source index](../../references/source-index.md).
- SRC-022: locate in [the source index](../../references/source-index.md).
- SRC-023: locate in [the source index](../../references/source-index.md).
- SRC-028: locate in [the source index](../../references/source-index.md).
