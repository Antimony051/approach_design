# Timing, pose, and coordinate contracts to finish

Updated November 16, 2026 for SRC-034 / PW-APPROACH-01: Pi 4, picoScan150 Pro Ethernet, Camera Module 3 CSI, and MicoAir/PX4 serial MAVLink pose. The selected software retains a recorder common reference plus native sensor, camera, and flight-controller times. A monotonic elapsed-time reference remains the working convention to specify. This is a starting contract, not a completed clock design. SA2 requires ≤20 ms residual relative timing, including drift, across ≥10 minutes.

For each stream record: device/configuration, sample or frame ID, native acquisition timestamp and its semantics, timestamp units/epoch/wrap, host receipt time, mapping into the common clock, offset/drift estimate and uncertainty, gaps, and calibration version. Image capture time must identify exposure start/midpoint or documented equivalent. Receipt time alone is not exposure time. LiDAR scan/segment/beam phase must be considered for moving scans.

For pose record: source (flight estimator, measured ground pose, or offline image-derived estimate), position and orientation, native and mapped times, quality/validity, interpolation method, stale threshold, and frame ID. Keep estimated camera center, aircraft reference origin, and LiDAR measurement origin distinct. A local Z coordinate or slant range is not automatically height above the observed pavement.

Frames needing explicit definitions: aircraft body; GNSS antenna/IMU origin; LiDAR; camera optical frame; test/survey local metric frame; optional geographic frame. Record origin, axes/handedness, units, orientation convention, transform direction, measured lever arms/boresight, and calibration uncertainty. Earlier documents suggest ENU; the selected autopilot's conventions must be converted at a documented boundary rather than assumed identical.

For image-derived poses, document overlap, intrinsics, reconstruction scale/orientation constraints, GPS/LiDAR/control inputs, independent checkpoints, and what happens when estimation fails. The original location note's exact/centimeter promises are not accepted evidence. The approximate 1 m × 1 m / 20 cm location preference does not replace S3/PC1. Measured ground poses can validate transform handling without validating an image pose estimator.

To complete: choose available sensor timestamp/PTP/trigger methods; verify exact camera driver/mode metadata; allocate FC ports and log rates; design independent timing events; calibrate intrinsics and rigid transforms; establish the complete range/pose/time error budget against S3; test remounting and clock drift. See SRC-007 A2/P1 for the ground-demo methods. Do not assert optional sensor IMU/PTP licenses are present.

## Selected acquisition details still to specify — SRC-034

The LiDAR clock starts unsynchronized; the approach proposes PTP or NTP mapping to the Pi. Verify support/configuration and independently measure residual offset/drift over ≥10 min; nominal synchronization is not a ≤20 ms result. Record Camera Module 3 native timestamps/exposure/readout metadata, not Python receipt time; planned 3 fps and ≤1 ms exposure require a combined-load trial. Account for rolling shutter and beam/segment timing. Freeze PX4 message types/rates/clock mapping, serial latency, units and NED/body-to-survey conversions.

A removable common sensor plate keeps LiDAR/camera relative mounting fixed. Whole-plate isolation can still change plate-to-aircraft pose; measure or bound it rather than assuming all transforms stay rigid. Version/check calibration after remounting or focus changes.

Source plans 0.25–1 m/s; SA2's 20 ms corresponds to 5–20 mm translation at those speeds, excluding angular/pose effects. FP2's 1–2 m/s remains a separate unresolved condition. Neither timing compliance nor FP4 alone proves S3.

IF-16 must distinguish local metric XYZ from WGS84 geographic geometry. Record origin, orientation, scale, datum and transform version/uncertainty; a best-effort GPS map point is not a precise ground reference. Q-20 tracks the reporting schema.

## Optional RGB/depth products — November 3 (IF-20; D-011)

The [PC proposal](../subsystems/05-data-processing-change-detection/rgb-depth-fusion-proposal.md) adds candidate derived views, not a finalized schema. Preserve raw profiles and referenced XYZ. For a point acquired at `t_l` and an image at `t_i`, transform LiDAR-to-survey using pose at `t_l`, then survey-to-camera using pose at `t_i`, before applying camera intrinsics/distortion. Respect beam/segment phase, image exposure and any rolling-shutter timing. Bound the accumulation window using pose quality and scene motion; temporal proximity alone does not establish pixel correspondence. Reject occluded, out-of-view, and invalid associations.

Declare whether D means camera-axis Z, ray distance, survey elevation, or signed reference-surface height; these are different quantities. Proposed metric arrays retain units, numeric precision, frame/calibration/clock/run IDs, source sample IDs/times, projection/grid mapping, coverage, and quality. Keep observed, interpolated, and learned values distinguishable; an unsupported value is missing, never a measured zero. Camera-depth views need intrinsics and view pose; elevation tiles need origin, axes, spacing, and datum; residuals need the versioned reference surface. Model normalization must not destroy the retained metric values. IF-16 carries source links and validity through to reports.
