# Timing, pose, and coordinate contracts to finish

Existing plans propose a recorder monotonic elapsed-time reference while retaining native sensor, camera, and flight-controller times. This is a starting contract, not a completed clock design. SA2 requires ≤20 ms residual relative timing, including drift, across ≥10 minutes.

For each stream record: device/configuration, sample or frame ID, native acquisition timestamp and its semantics, timestamp units/epoch/wrap, host receipt time, mapping into the common clock, offset/drift estimate and uncertainty, gaps, and calibration version. Image capture time must identify exposure start/midpoint or documented equivalent. Receipt time alone is not exposure time. LiDAR scan/segment/beam phase must be considered for moving scans.

For pose record: source (flight estimator, measured ground pose, or offline image-derived estimate), position and orientation, native and mapped times, quality/validity, interpolation method, stale threshold, and frame ID. Keep estimated camera center, aircraft reference origin, and LiDAR measurement origin distinct. A local Z coordinate or slant range is not automatically height above the observed pavement.

Frames needing explicit definitions: aircraft body; GNSS antenna/IMU origin; LiDAR; camera optical frame; test/survey local metric frame; optional geographic frame. Record origin, axes/handedness, units, orientation convention, transform direction, measured lever arms/boresight, and calibration uncertainty. Earlier documents suggest ENU; the selected autopilot's conventions must be converted at a documented boundary rather than assumed identical.

For image-derived poses, document overlap, intrinsics, reconstruction scale/orientation constraints, GPS/LiDAR/control inputs, independent checkpoints, and what happens when estimation fails. The original location note's exact/centimeter promises are not accepted evidence. Measured ground poses can validate transform handling without validating an image pose estimator.

To complete: choose available sensor timestamp/PTP/trigger methods; verify exact camera driver/mode metadata; allocate FC ports and log rates; design independent timing events; calibrate intrinsics and rigid transforms; establish the complete range/pose/time error budget against S3; test remounting and clock drift. See SRC-007 A2/P1 for the ground-demo methods. Do not assert optional sensor IMU/PTP licenses are present.
