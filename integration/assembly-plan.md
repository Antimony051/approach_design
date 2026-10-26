# Installed design and assembly plan — to be developed

Status: no selected complete installation. This outline specifies the needed design output; it is not executable wiring instructions.

## Configuration and interactions

Fill in the selected configuration ID, BOM revision, exact hardware/firmware/OS versions, requirements covered, and remaining uncertainties. Explain how power, commands, pose, LiDAR, images, storage, diagnostics, export, processing, and reporting interact. Link each physical connection to an IF ID and BOM rows.

## Electrical design

Add an editable power/wiring diagram and pin map: source and load connector, gender/keying, orientation/pin number, net/polarity, signal level, wire gauge/length, fuse/protection, current rating, ground/shield handling, regulator input/output limits, and strain relief. Include charging/bench supply cables. Reconcile every FC UART/I2C/output and regulator load. Earlier H7 and Pixhawk maps are candidate-specific examples, not interchangeable wiring instructions.

## Mechanical design

Add a dimensioned installed layout/CAD with the chosen airframe, battery, sensor/system plug, camera/lens, recorder/expansion/cooling, SSD, regulators, antennas, cables, brackets, fasteners, and retention. Include landing clearance, optics/scan sector, propeller clearance, connector service access, heat flow, load paths, CG, and rigid calibration relationships. The earlier 120 × 100 × 130 mm sensor and 120 × 90 × 60 mm recorder envelopes are allocations, not proven available space.

## Assembly and commissioning sequence

Write component-specific steps after selection: incoming inventory/revision check; mount fabrication and inspection; power/harness polarity and continuity checks; bench supply startup; firmware/port configuration; sensor/camera/storage commissioning; health/pose integration; simultaneous recording; timing/intrinsic/extrinsic calibration; static and controlled-motion evaluation; aircraft checks and later authorized loaded flights. Identify tools and test fixtures in the BOM. Retain measured results separately from instructions.

## Operating and recovery procedures

Define startup readiness, clock/calibration/configuration checks, start/stop recording confirmation, full/low storage, sensor disconnect, stale pose, regulator brownout/recorder reboot, RC/telemetry loss, manual takeover, low battery, landing/shutdown, export/hash verification, and remount/recalibration. Record what still runs and what data become invalid after each failure. No assumed cloud link may silently become necessary to finish acquisition.

## Review package

Supply chosen configuration/BOM and delivered cost, fit/mass/power margins, unresolved tests and dependencies, commissioning evidence, and requirement traceability. Explain differences from the planning slides through dated decisions.
