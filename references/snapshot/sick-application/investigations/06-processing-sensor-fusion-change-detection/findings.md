# Processing, sensor fusion, and change detection

## 1. Scope and recommendation

### Recommendation

Build the first PaveWatch processing system as a **versioned, offline pipeline with two explicit analysis branches**:

1. a geometric branch that reconstructs a site-local surface from time-stamped moving 2D profiles and compares an accepted baseline with a current survey; and
2. a visual branch that detects or scores pavement-distress regions in RGB, then tests whether registered range/shape features improve the same held-out decisions.

The minimum viable geometric algorithm should be deliberately explainable: validate and synchronize the logs, motion-compensate each available LiDAR sample, transform it into a site-local frame, refine repeat-survey alignment using stable control areas, fit local planes or low-order surface patches, and threshold signed baseline/current residuals only when they persist spatially and exceed the estimated uncertainty. The output is a **candidate geometric change**, not a diagnosis or safety determination.

The minimum viable fusion experiment should compare:

- an image-only baseline using simple RGB/texture features and a transparent classifier; and
- the identical classifier and evaluation split with registered shape features added, such as local-plane residual, relative height, slope, roughness, and valid-range fraction.

For the pre-hardware demonstration, use the analytic profile fixtures and paired public stereo data selected in investigation 07. Those inputs can verify schemas, algorithms, paired evaluation, and reporting, but cannot establish picoScan150 or UAV field performance. After hardware arrives, retain the same canonical schemas and replace each simulated/public adapter with real picoScan150, camera, pose, and calibration records.

This is preferable to beginning with an end-to-end neural fusion model because the principal early risks are observability, time alignment, calibration, pose drift, repeat registration, sparse coverage, and domain mismatch. A more complex model cannot recover information the sensors did not observe and can make those failures harder to diagnose.

### Alternatives considered

| Decision | Recommended MVP | Alternative and disposition |
|---|---|---|
| Geometric comparison | Robust local surface/profile fit and signed change along a local normal | Raw nearest-neighbor point distance is easy but confounds sampling density and surface orientation; retain only as a diagnostic. A full M3C2-style multiscale comparison is a strong later enhancement.[7] |
| Surface representation | Site-local grid plus profile records, preserving original points | A single dense mesh can look compelling but may interpolate across unobserved pavement; defer it until gap/uncertainty behavior is explicit. |
| Repeat registration | Navigation/marker seed followed by one constrained robust rigid refinement on stable controls | Unconstrained tilewise or nonrigid registration risks fitting away actual change. Pose-graph or piecewise correction is an enhancement requiring independent controls. |
| Change threshold | Absolute test-objective threshold plus uncertainty and spatial persistence | One universal millimeter threshold would be unsupported before characterization. A classifier-only change score is also harder to audit. |
| Visual fusion | Same simple classifier with and without registered shape features | Late score fusion is a reasonable second baseline. Dense learned fusion is deferred until real paired data is large enough and the alignment baseline passes. |
| Deployment | Deterministic laptop/offline pipeline | Cloud processing is optional synchronization/scale-out later; full onboard inference is deferred until data rates and resources are measured. |

### Minimum credible demonstration

The first laptop demonstration should produce all of the following from one reproducible command or documented workflow:

1. validation and quality reports for the input survey folders;
2. a synthetic baseline/current change map with known truth and declared degradation settings;
3. an unchanged synthetic control case that reveals false positives;
4. paired image-only and image-plus-shape metrics on the same public-data groups;
5. an anomaly/result table carrying measurement uncertainty, model score, coverage, and quality as separate fields; and
6. a report whose inputs, calibration, parameters, code revision, and source-data licenses are traceable.

Every pre-hardware output should carry this statement:

> Pre-hardware software demonstration using public and/or synthetic data. Not a field validation of PaveWatch or the SICK picoScan150.

### Claims this design can and cannot support

The proposed work can demonstrate that the team has a technically coherent plan for ingest, motion compensation, coordinate transforms, repeat-survey comparison, RGB/range association, uncertainty, evaluation, and reporting. It cannot yet establish:

- a minimum pavement-change size detectable by the proposed aircraft and picoScan150;
- crack width or fine-crack depth measured by the 2D LiDAR;
- an accuracy, precision, recall, or improvement percentage for PaveWatch;
- reliable reconstruction when position, orientation, timing, or calibration is missing;
- safe pavement, code compliance, or a maintenance decision; or
- real-time operation onboard the UAV.

Those claims require controlled measurements with the selected camera, flight platform, positioning system, supplied picoScan150, and independent ground truth.

## 2. Evidence and assumptions

### Project-state labels

| Label | Meaning in this brief |
|---|---|
| **Proposed** | An architecture, algorithm, threshold rule, or schema recommended here but not implemented. |
| **Available to borrow** | Hardware that another investigation has confirmed can be borrowed; none is assumed here. |
| **Planned** | Work accepted for a later software or field phase. |
| **Simulated** | Deterministically generated surfaces, scans, pose errors, timestamps, or images. |
| **Public data** | Externally maintained data with recorded version, license, and retrieval information. |
| **Measured** | Data captured by the PaveWatch team under a traceable procedure. No current repository result qualifies. |

No algorithm has been run for this investigation and no accuracy or improvement has been measured.

### Evidence behind the recommendation

1. The picoScan150 is a 2D LiDAR. Its operating instructions define scan and IMU output, Ethernet data paths, device configuration, diagnostics, and telegram structures.[1] Processing must therefore preserve the actual scan configuration, firmware/configuration snapshot, timestamps, invalid returns, and status fields rather than accepting an undocumented point cloud.
2. ROS REP 103 provides SI-unit and right-handed coordinate conventions, including body and camera optical-frame conventions; REP 105 separates a globally referenced map frame from a locally continuous odometry frame.[2][3] PaveWatch does not need ROS to adopt the useful discipline of named frames and explicit transform authority.
3. OpenCV's calibration model provides the camera intrinsics, distortion, and rigid transformations needed to project 3D observations into image coordinates.[4] A pixel association is not valid merely because an image and scan have nearby filenames.
4. Rotations must be interpolated on the rotation manifold, not by independently interpolating Euler angles. SciPy's spherical linear interpolation follows the shortest rotation path between key rotations and supplies a suitable laptop implementation.[5]
5. Open3D supplies point-to-plane ICP and robust kernels for registration and outlier resistance.[6] ICP is a refinement method, not proof of correct global alignment; PaveWatch must seed it from navigation/control information and reject weak or implausible solutions.
6. The M3C2 work shows why point-cloud change detection should consider surface orientation, local roughness, point density, and registration error rather than using unqualified nearest-neighbor distances alone.[7] A complete M3C2 implementation is an enhancement; the MVP adopts the same principle of change along a local surface normal with a visible uncertainty budget.
7. The Guide to the Expression of Uncertainty in Measurement treats a result and its uncertainty together and describes propagation from input quantities.[8] Accordingly, PaveWatch should not equate a classifier probability, a geometric uncertainty interval, and a data-quality score.
8. Precision and recall trade off as a classification threshold changes, while average precision summarizes a precision-recall curve.[9] The visual experiment must publish the operating threshold and paired held-out results, not only a single favorable accuracy value.

### Assumptions

- Raw sensor data is recorded during acquisition and processed on an existing laptop after landing.
- A single survey can contain multiple flights or a stationary/ground-rig acquisition.
- Early controlled sites have a site-local metric frame even if reliable world coordinates are unavailable.
- The navigation stream supplies time-stamped position and orientation estimates plus an indication of validity or covariance. If it does not, measurement-grade moving reconstruction is blocked.
- LiDAR-to-body and camera-to-body extrinsics are rigid over a survey and are versioned calibration inputs.
- A baseline is an accepted earlier survey linked to a particular processing run; it is not silently replaced.
- Stable control regions or surveyed markers exist outside the expected change region. Without them, rigid misregistration and broad pavement change may be unidentifiable.
- Fine cracks remain RGB observations. Range data may add context about nearby surface geometry but is not assumed to resolve the crack itself.
- Processing thresholds are configuration values. Field thresholds will be selected only after bench and controlled-site characterization.

### Coordinate-frame convention

Use the notation <code>^A T_B</code> for the rigid transform that maps a point expressed in frame <code>B</code> into frame <code>A</code>. Store translation in meters and rotations as normalized quaternions with the component order stated explicitly; derived 4 × 4 matrices may be cached but do not replace the source calibration record.

| Frame | Proposed axes and authority | Purpose |
|---|---|---|
| <code>earth</code> | Optional geodetic/ECEF authority from the positioning subsystem | Cross-site/world reference; not required for the first local demonstration. |
| <code>site</code> | Right-handed local ENU: x east, y north, z up, with a recorded origin | Repeat-survey comparison and reports. A marked local frame is acceptable before RTK. |
| <code>odom</code> | Locally continuous navigation frame, allowed to drift | Motion compensation within a flight. |
| <code>body</code> | x forward, y left, z up | UAV/payload rigid-body frame. |
| <code>lidar_raw</code> | Manufacturer-defined sensor axes, documented without reinterpretation | Polar scan decoding. The calibration maps this into <code>body</code>. |
| <code>camera_optical</code> | x right, y down, z forward | Image projection convention. |
| <code>surface_local</code> | Normal/tangent basis fitted for a profile or patch | Signed distance and uncertainty calculation. |

The transformation chain for a LiDAR return acquired at time <code>t</code> is:

```text
^site p = ^site T_odom · ^odom T_body(t) · ^body T_lidar · ^lidar p(range, angle)
```

If the navigation system directly supplies <code>^site T_body(t)</code>, the separate <code>odom</code> term may be omitted, but the frame semantics must remain explicit. Investigation 03 must decide whether the navigation estimator uses ENU or NED and supply a tested conversion at one boundary only.

### Time model and temporal alignment

Preserve four concepts instead of overwriting timestamps:

| Field | Meaning |
|---|---|
| <code>sensor_time_raw</code> | Original device timestamp and its clock domain. |
| <code>host_receive_time</code> | Host monotonic receive time; useful for packet-order and latency diagnostics, not a substitute for acquisition time. |
| <code>survey_time_ns</code> | Mapped monotonic survey time used for fusion. |
| <code>utc_time</code> | Optional civil timestamp used for survey ordering and provenance. |

Each clock mapping should be stored as a versioned model, initially <code>t_survey = a · t_sensor + b</code>, with the observations used to fit it, fit residuals, validity interval, and uncertainty. A single offset is acceptable only if drift is shown negligible over the acquisition interval. UTC synchronization alone does not establish sub-frame sensor alignment.

For pose at an observation time, linearly interpolate translation and use quaternion spherical interpolation for orientation. Never interpolate across a pose gap larger than a configured maximum. Use a per-beam timestamp if the acquisition format supplies one; otherwise use the best documented scan timestamp, carry the scan-time approximation as uncertainty, and test motion smear at the proposed speed and angular rate.

A useful first-order timing sensitivity is:

```text
translation displacement ≈ speed × timing uncertainty
rotational displacement at range r ≈ r × angular_rate × timing uncertainty
```

These terms belong in the uncertainty/stress model; they are not corrections unless the time offset is estimated from independent evidence.

### When a moving 2D scan is insufficient

A 2D scan gives ranges only in one instantaneous plane. Motion can sweep that plane into a 3D sampling pattern, but a usable pavement surface is not guaranteed. Geometry is insufficient when any of the following applies:

- the scan plane does not intersect the target with useful incidence and spacing;
- the trajectory does not sweep adjacent profiles across the region of interest;
- pose or per-scan timing is absent, discontinuous, or too uncertain for the desired change scale;
- extrinsics are unknown or mechanically changing;
- occlusion, invalid returns, or specular/dark-surface behavior leaves gaps larger than the candidate feature;
- repeated passes observe substantially different footprints without reliable control;
- the reference area is itself changing, or no stable controls constrain registration; or
- the desired feature is finer than the effective spatial sampling and uncertainty.

In these cases the pipeline must lower coverage, add a blocking quality flag, and withhold metric change. It may still present RGB evidence with an explicit image-only label.

## 3. Proposed components or software

### 3.1 Free laptop/offline stack

| Component | Proposed use | MVP status |
|---|---|---|
| Python managed with <code>uv</code> and a committed lockfile | Reproducible commands and environment | Required |
| NumPy and SciPy | Arrays, interpolation, robust statistics, optimization, quaternion rotation/Slerp | Required |
| OpenCV | Camera calibration, undistortion, projection, image features, masks | Required |
| Open3D | Point-cloud representation, normals, registration, visualization | Required once 3D swept scans are used |
| scikit-learn | Transparent logistic regression/tree baselines and metrics | Required for public-data fusion experiment |
| PyArrow/Parquet | Typed intermediate and result tables | Required |
| JSON plus JSON Schema | Small manifests, calibration references, run parameters, and validation | Required |
| Matplotlib or Plotly with locally bundled assets | Static profiles, change maps, and diagnostic plots | One required; static output preferred first |
| PDAL | LAS/LAZ import/export and larger point-cloud pipelines | Optional enhancement |
| PyTorch or an object-detection framework | Learned aerial RGB detector or learned fusion | Optional, after the explainable baselines |

No paid cloud service, online map, or GPU is needed for the MVP. Cloud synchronization may be added later without becoming part of the algorithm's correctness.

### 3.2 Canonical data products

Every record includes <code>schema_version</code>, <code>survey_id</code>, an evidence-state label, and either <code>run_id</code> or a raw acquisition identifier. Every artifact is referenced by a relative URI and cryptographic content hash. Investigation 08 owns the final persistent catalog; this section defines the processing contract.

#### Raw and calibrated products

| Product | Minimum fields |
|---|---|
| <code>raw_scan</code> | sensor ID, sequence/telegram ID, raw sensor timestamp, host receive timestamp, scan configuration ID, angle start/increment or per-return angle, range, return/status code, intensity/RSSI if supplied, original packet URI and byte offset |
| <code>raw_image</code> | camera ID, frame ID, raw camera timestamp, host receive timestamp, exposure, gain, image URI, width/height, rolling/global-shutter metadata when known |
| <code>raw_pose</code> | pose source, raw timestamp, frame IDs, position, quaternion and order, linear/angular velocity when present, validity, covariance when present |
| <code>clock_model</code> | source and target clock domains, model type, coefficients, fit interval, observations URI, residual statistics, uncertainty, method/version |
| <code>intrinsic_calibration</code> | camera matrix, distortion model/coefficients, image size, calibration time/method, target data URI, residual summary, validity interval |
| <code>extrinsic_calibration</code> | parent/child frame IDs, translation, quaternion/order, covariance or repeatability evidence, method, fixture state, validity interval |
| <code>frame_tree</code> | named frames, transform direction, static/dynamic authority, axis/unit definition, graph validation result |

Invalid, out-of-range, missing, and filtered LiDAR returns must remain distinguishable. Do not encode all of them as zero or silently drop them before quality accounting.

#### Intermediate products

| Product | Minimum fields |
|---|---|
| <code>synchronized_sample</code> | source record ID, mapped survey time, interpolated pose IDs/times, interpolation fraction, time residual/uncertainty, synchronization flags |
| <code>motion_compensated_point</code> | source scan/return ID, site-frame xyz, original range/angle/status, transform-chain ID, point uncertainty summary, filter flags |
| <code>registration</code> | baseline/current survey IDs, initial and refined transforms, stable-control definition, algorithm/parameters, inlier count, fitness/residuals, covariance/uncertainty estimate, acceptance decision |
| <code>surface_cell</code> | survey/run/frame, cell/profile ID, center, local normal, fitted coefficients, point count, spatial extent, roughness/residual scale, coverage, valid/invalid counts |
| <code>rgb_geometry_association</code> | image/region ID, source point IDs or aggregate URI, projection/calibration ID, depth/shape features, valid fraction, occlusion rule, association flags |

#### Result products

| Product | Minimum fields |
|---|---|
| <code>change_sample</code> | baseline/current cell IDs, signed normal distance, standard/expanded uncertainty and coverage convention, signal-to-uncertainty ratio, spatial support, registration ID, flags |
| <code>vision_prediction</code> | image/region ID, model ID, channel (<code>rgb_only</code> or <code>rgb_plus_shape</code>), raw score, calibrated probability if validated, threshold, predicted class, geometry availability |
| <code>candidate_anomaly</code> | anomaly ID, type/channel, local-frame geometry, optional WGS 84 geometry, magnitude summary, uncertainty summary, image score, coverage, quality flags, evidence links, requires field verification |
| <code>metrics</code> | dataset/split/group definition, truth source, metric names/values/units, confidence-interval method, exclusions, evaluated sample IDs |
| <code>run_manifest</code> | code revision, environment lock hash, command, random seed, parameters hash, input/calibration hashes, start/end times, stage statuses, output hashes |

Do not store a single ambiguous <code>confidence</code> number. Keep at least these concepts separate:

- geometric measurement uncertainty;
- visual model score or calibrated probability;
- coverage/completeness;
- registration quality; and
- blocking/advisory quality flags.

### 3.3 End-to-end pipeline with named artifacts

```text
survey folder + manifest.json
  -> INGEST / schema, checksum, stream, unit, and frame validation
  -> ingest/validation.json + ingest/inventory.parquet

raw scan packets + raw images + raw pose/IMU + calibration/configuration
  -> NORMALIZE / lossless adapters preserving IDs and raw status
  -> normalized/scans.parquet + images.parquet + poses.parquet
     + clock-model.json + frame-tree.json + calibration references

normalized streams + clock-model.json
  -> SYNCHRONIZE / clock mapping, pose bracketing, gap checks
  -> intermediate/synchronized-samples.parquet + synchronization-quality.json

synchronized scans + poses + ^body T_lidar
  -> DECODE, FILTER, AND MOTION COMPENSATE / one transform per timed return
  -> intermediate/site-points.parquet + point-quality.parquet

site points + mission coverage + stable-control definition
  -> REPEAT REGISTRATION / navigation or marker seed, then constrained robust refinement
  -> intermediate/registration.json + registered-points.parquet

registered points
  -> SURFACE/PROFILE RECONSTRUCTION / robust local plane or low-order patch fits
  -> intermediate/surface-cells.parquet + coverage-grid.parquet

baseline surface + current surface + uncertainty inputs
  -> SIGNED DIFFERENCING / local-normal residual and uncertainty propagation
  -> intermediate/change-samples.parquet + change-map.tif/png + quality-flags.json

change samples + persistence/coverage rules
  -> GEOMETRIC CANDIDATE EXTRACTION
  -> results/geometric-candidates.parquet + geometric-metrics.json

raw images + camera calibration
  -> RGB PREPROCESSING / decode, undistort, normalize, region/patch definition
  -> intermediate/image-regions.parquet + rgb-features.parquet

site points + image pose + ^body T_camera + camera intrinsics
  -> PROJECT / visibility, occlusion, neighborhood aggregation
  -> intermediate/rgb-geometry-associations.parquet + shape-features.parquet

same image regions and held-out groups
  -> IMAGE-ONLY MODEL -------------------\
  -> RGB-PLUS-SHAPE MODEL ----------------+-> paired predictions + paired-metrics.json

geometric candidates + visual predictions + evidence/provenance + quality flags
  -> ASSOCIATION, REVIEW PRIORITY, AND EXPORT
  -> results/anomalies.parquet + report.json + figures + report.html/pdf
```

Each arrow is a versioned processing activity. A failed stage retains its validation output and must not generate apparently complete downstream evidence.

### 3.4 Minimum viable geometric algorithm

#### A. Validate and filter without erasing evidence

1. Reject non-finite angles, ranges, poses, and transforms from computation while retaining their counts and source IDs.
2. Decode manufacturer invalid-return and status values explicitly.
3. Apply configured usable-angle and range bounds only after recording the raw values and configuration source.
4. Use a small robust neighborhood or statistical filter for isolated outliers; record the filter, parameters, and removed-point mask.
5. Never fill a gap larger than the configured spatial or temporal support. Mark it uncovered.

#### B. Motion compensate

For every timed LiDAR return, construct its point in <code>lidar_raw</code>, interpolate the body pose at that acquisition time, and evaluate the transform chain into <code>site</code>. Retain both the uncompensated and compensated diagnostics for a controlled test. If only a scan-level timestamp exists, apply that documented approximation and estimate its spatial sensitivity under the observed motion.

#### C. Register repeat surveys

Use this order:

1. seed with RTK/world pose, surveyed markers, or the repeatable site-local setup;
2. select stable controls that are outside the candidate-change region and span the survey footprint;
3. refine a rigid transform with robust point-to-plane ICP or an equivalent robust least-squares method;
4. constrain implausible translation/rotation relative to the initial evidence;
5. evaluate held-out control points, not only the points used for optimization; and
6. reject or flag a transform when overlap, control distribution, residuals, or observability are inadequate.

Do not let unconstrained ICP independently warp small tiles until apparent change disappears. The default repeat-survey correction is one rigid site transform. Piecewise/nonrigid correction is a research enhancement and must be validated not to absorb real pavement deformation.

If surveyed markers or RTK are unavailable, a repeatable marked local frame plus natural stable edges may support a demonstration. It does not support the same absolute-geolocation claim. If neither external controls nor stable scene geometry exists, report that baseline/current change is unobservable.

#### D. Reconstruct local profiles or surface patches

The simplest MVP is a regular site-local grid whose cell size is selected from observed sampling density rather than a promised physical resolution. Within each cell or along each profile:

1. require a minimum number and spatial spread of valid points;
2. estimate a local normal from a robust plane fit;
3. store median signed height/normal coordinate, point count, roughness, and footprint;
4. reject vertical or poorly conditioned patches when the pavement model is inappropriate; and
5. retain multi-pass values so repeatability can be estimated rather than averaging away disagreement.

A low-order polynomial or locally weighted surface may be added where curvature is real and sufficiently sampled. Model order is selected on stable validation regions, not increased until a candidate disappears.

#### E. Difference along the local surface normal

For a baseline patch with representative point <code>p_b</code>, current patch point <code>p_c</code>, and baseline local unit normal <code>n</code>, define the signed change:

```text
d = nᵀ (p_c - p_b)
```

Positive/negative semantics must be tested against the chosen up-axis and displayed as heave-like/settlement-like only after the frame is verified. Report the peak only with robust summaries such as median, percentiles, footprint, and support because one return can be an outlier.

#### F. Carry an uncertainty budget

The first implementation may use linear covariance propagation where justified and a deterministic Monte Carlo propagation for nonlinear transform effects. Include, at minimum:

- baseline and current local fit/roughness uncertainty;
- range repeatability/noise characterized for the actual surface and configuration;
- pose position and orientation uncertainty;
- clock-mapping/timestamp uncertainty converted through observed motion;
- extrinsic calibration uncertainty;
- repeat-registration uncertainty estimated from independent controls or repeats; and
- surface-model/sampling uncertainty.

For an independence approximation only:

```text
u_d² ≈ u_baseline² + u_current² + u_pose² + u_time²
       + u_extrinsic² + u_registration² + u_surface_model²
```

Shared errors can be correlated and must not be double-counted. Store which terms are measured, manufacturer-sourced, simulated, or conservatively assigned. Until a term is defensibly quantified, flag the uncertainty as incomplete rather than reporting false precision.

#### G. Extract persistent candidates

A cell becomes eligible only when all of these hold:

1. baseline and current coverage pass;
2. registration and calibration are accepted;
3. the magnitude exceeds a configured absolute threshold selected for the test objective;
4. the magnitude also exceeds a configured multiple of its uncertainty; and
5. the sign/magnitude persists across a configured connected area, length, number of neighboring profiles, or independent passes.

The absolute threshold, uncertainty multiplier, and persistence support are recorded, swept during validation, and never described as a sensor capability before field evaluation. Neighboring eligible cells are joined into candidates, but raw cell values remain linked.

### 3.5 Image-only and LiDAR/range-assisted baselines

#### Image-only baseline

For the small public paired experiment from investigation 07:

1. define fixed patches or superpixels without seeing held-out labels;
2. compute simple color statistics, gradient magnitude, edge density, local contrast, and texture features;
3. assign labels from the public mask using a declared occupancy rule;
4. fit a class-weighted logistic regression or shallow tree; and
5. select preprocessing, hyperparameters, and an operating threshold using training groups only.

This is the control condition. A later aerial object detector may replace it, but the image-only comparator must remain available.

#### Range-assisted baseline

Use the exact same image regions, labels, groups, model family, tuning budget, and operating-threshold procedure. Add only registered geometric summaries:

- valid geometry fraction and point count;
- robust median relative height/local-plane residual;
- lower/upper residual quantiles;
- local slope and normal components;
- residual or height dispersion/roughness; and
- neighborhood coverage or distance to the nearest valid geometry.

Feature concatenation into the same transparent classifier is the recommended first fusion method. A second simple option is late score fusion using the RGB model score plus a small set of geometric summaries. Missing geometry is represented by an availability flag and missing-value policy fitted on training data; it is never silently replaced by a plausible depth.

For the public Stereo Pothole data, call the result **RGB plus public stereo-derived shape**, not picoScan150 fusion. It tests the software method only.

#### Association with the real camera

For each site-frame LiDAR point and image time:

1. interpolate the camera/body pose at the observation time;
2. transform the point into <code>camera_optical</code> using the versioned extrinsics;
3. reject points behind the camera or outside the calibrated image domain;
4. project with the stored camera model and distortion handling;
5. apply a visibility/occlusion rule rather than allowing a farther point to overwrite a nearer surface; and
6. aggregate sparse points over a declared region or neighborhood.

Because a moving 2D scanner will generally project sparse support into an image, the MVP should use region-level features, not fabricate a dense depth image. Learned depth completion is an enhancement and must be evaluated separately from observed range.

#### Fair paired comparison

- Split by acquisition sequence, flight, route segment, or source group, never random neighboring patches.
- Use identical held-out samples for both branches.
- Fit normalization, imputation, feature selection, calibration, and thresholds on training data only.
- Bootstrap or resample whole frames/sequences, not correlated patches.
- Publish every evaluated group and exclusion.
- Report the paired metric difference with uncertainty, even when geometry hurts.
- Run a shuffled-geometry negative control. A persistent apparent benefit after breaking alignment is evidence of leakage or confounding.
- Use “improved” only if the completed held-out experiment and its uncertainty support that statement.

### 3.6 Staged enhancement path

| Stage | Added capability | Gate before advancing |
|---|---|---|
| 0 — analytic profiles | Known surfaces, exact transforms, configurable noise/dropout/pose error | Deterministic schemas and truth-based tests pass. |
| 1 — public paired data | Image-only versus RGB-plus-shape experiment | Leakage-safe grouped evaluation and provenance pass. |
| 2 — stationary picoScan150 bench | Real decoding, status handling, range repeatability, clock capture | Known targets and replay produce consistent outputs. |
| 3 — moving ground rig | Motion compensation, swept reconstruction, camera association | Timing/extrinsic tests and independent fixture recovery pass. |
| 4 — controlled flight | Navigation integration, coverage, vibration, repeat registration | Stable-control residuals and independent ground truth meet predeclared gates. |
| 5 — field pilot | Local pavement data, domain-specific RGB model, repeated surveys | Held-out route/date evaluation and human review protocol pass. |
| 6 — enhancements | M3C2-like multiscale change, pose-graph optimization, learned detector/fusion, optional edge inference | Each enhancement beats or clarifies an explainable baseline without hiding quality failures. |

### 3.7 Minimum quality flags

| Flag | Effect |
|---|---|
| <code>TIME_ALIGNMENT_UNKNOWN</code> | Block metric fusion/change for moving data. |
| <code>POSE_GAP</code> | Exclude affected samples; reduce coverage. |
| <code>POSE_UNCERTAINTY_MISSING</code> | Permit diagnostics but mark uncertainty incomplete. |
| <code>EXTRINSIC_UNVERIFIED</code> | Block camera/LiDAR association and measurement claim. |
| <code>INSUFFICIENT_REPEAT_OVERLAP</code> | Block change comparison in affected region. |
| <code>REGISTRATION_WEAK</code> | Block or downgrade geometric candidates according to a predeclared rule. |
| <code>SPARSE_GEOMETRY</code> | Withhold shape features or geometric magnitude locally. |
| <code>GAP_INTERPOLATION_PROHIBITED</code> | Preserve a hole instead of manufacturing a surface. |
| <code>SENSOR_OCCLUSION_SUSPECTED</code> | Exclude/flag affected region. |
| <code>RGB_OVEREXPOSED</code>, <code>RGB_UNDEREXPOSED</code>, <code>RGB_BLUR</code> | Downgrade visual evidence; geometry may remain usable. |
| <code>BASELINE_UNACCEPTED</code> | Block final change candidates. |
| <code>UNCERTAINTY_INCOMPLETE</code> | Allow exploratory values but prohibit threshold-based measurement language. |
| <code>SIMULATED_INPUT</code>, <code>PUBLIC_NON_PAVEWATCH_SENSOR</code> | Force the pre-hardware disclaimer. |

## 4. Interfaces and data flow

### Acquisition and sensing interface — investigations 02 and 04

Processing requires investigation 02 to settle:

- canonical raw picoScan150 packet/telegram capture and lossless replay;
- exact timestamp meaning and granularity for scan/return/IMU messages;
- scan-angle convention, usable sector, range units, invalid-return encoding, intensity/RSSI meaning, and status/diagnostic fields;
- configuration snapshot, firmware version, active filters, performance profile, and Ethernet-output settings; and
- proposed scan orientation and altitude/speed cases.

Investigation 04 must preserve packet order, receive timestamps, sequence gaps, checksums, flight/survey IDs, storage-capacity warnings, and atomic completion state. Normalized Parquet is a processing product, not a replacement for the raw capture.

### RGB, positioning, calibration, and time interface — investigation 03

Processing requires:

- raw image timestamps and exposure interval, not filesystem modification time;
- camera intrinsics, distortion model, shutter behavior, resolution, exposure, and gain;
- time-stamped body pose, frame IDs, quaternion convention, validity, and covariance if available;
- camera/body and LiDAR/body extrinsics with calibration evidence and validity interval;
- a common-clock or clock-mapping method and residual/uncertainty evidence; and
- calibration targets/fixtures suitable for checking both reprojection and 3D alignment.

If RTK is selected, it supplies a strong global seed but does not remove the need for local alignment checks, lever-arm calibration, timestamp alignment, or stable controls. If RTK is unavailable, reference markers and site-local optimization become required for credible repeat-survey geometry.

### Mission-planning interface — investigation 05

Processing needs both planned and executed route, altitude, ground speed, heading, sensor orientation, overlap, turns, pauses, and site boundary. After a survey, it must produce a coverage grid and identify regions where spacing/incidence/overlap do not support the requested analysis. Mission planning should accept these coverage failures when designing the next flight.

### Dataset and demonstration interface — investigation 07

Investigation 07 supplies:

- deterministic analytic surfaces and moving-profile fixtures with exact truth;
- source manifests and leakage-safe group IDs;
- normalized public RGB, disparity/point-cloud, and label records;
- a paired evaluation protocol; and
- mandatory pre-hardware labeling.

This investigation owns the algorithms, uncertainty model, registration, feature definitions, quality gates, and final metric calculations. The public RGB and synthetic geometry must not be combined into a fabricated physically paired observation.

### Reporting interface — investigation 08

For every candidate, send investigation 08:

- baseline/current evidence IDs and processing-run ID;
- local geometry and optional valid world geometry;
- channel and evidence state;
- geometric magnitude with uncertainty convention;
- visual score/probability with model and threshold;
- coverage and registration diagnostics;
- quality flags and exclusions;
- representative current/baseline images and profile/change plots; and
- links to raw/calibrated/intermediate artifacts.

The report labels outputs as candidates requiring review. A review decision is a new record and must not rewrite the algorithm output.

### Central integration decisions

1. One frame tree, transform notation, quaternion order, unit convention, and ENU/NED conversion boundary must be adopted by investigations 02–06.
2. One canonical survey clock and clock-mapping record must be adopted by investigations 02–04 and 06.
3. The scan plane orientation, camera field of view, flight direction, altitude, speed, and expected sampling pattern must be checked together; none can be selected independently.
4. The team must decide whether real raw evidence is original SICK datagrams, a bag/container that preserves them, or both.
5. The team must choose the first target measurands—for example, signed local surface displacement and rut/profile change—before selecting field thresholds.
6. The application currently mentions cloud processing, while investigations 07–08 assume laptop/offline processing. Recommended integration wording is post-flight offload for local processing with optional later cloud synchronization.

## 5. Development sequence and dependencies

### Phase 0 — contracts and fixtures

1. Freeze schema version 0.1 for frames, clocks, raw samples, calibration, runs, and results.
2. Implement schema/checksum validation and a run manifest before implementing detection.
3. Adopt one transform notation and write round-trip/frame-direction tests.
4. Import investigation 07's analytic profiles and generate identity, known-change, zero-change, missing-data, and pose/timing-error fixtures.
5. Define quality flags and investigation 08 result fields.

Dependencies: investigation 07 fixture contract and investigation 08 identifiers. This phase does not need hardware.

### Phase 1 — geometric software baseline

1. Normalize synthetic profile, pose, and calibration records.
2. Implement clock mapping, pose interpolation, transform chaining, and motion compensation.
3. Implement grid/profile reconstruction with robust local planes.
4. Implement stable-control rigid registration and rejection diagnostics.
5. Implement local-normal differencing, initial uncertainty propagation, persistence grouping, and result export.
6. Run one-factor degradation sweeps and publish failure boundaries rather than tuning only a clean case.

Dependencies: proposed timing/pose fields from investigations 02–04; synthetic stand-ins may be used until those contracts are final.

### Phase 2 — public paired fusion baseline

1. Load the normalized Stereo Pothole records from investigation 07.
2. Build leakage-safe frame/sequence groups and region labels.
3. Implement RGB features and a fixed transparent classifier.
4. Implement shape features and the paired RGB-plus-shape branch.
5. Run grouped evaluation, whole-frame resampling, missing-geometry tests, and shuffled-geometry control.
6. Export both results without assuming a benefit.

Dependencies: dataset access/license record and group definitions from investigation 07. No PaveWatch hardware claim results.

### Phase 3 — real packet replay and bench characterization

1. Add the picoScan150 raw/replay adapter after investigation 02 freezes it.
2. Verify packet loss, status, invalid returns, units, angle convention, and configuration capture.
3. Collect repeated stationary scans of known planar, step, and sloped targets with independent dimensions.
4. Estimate repeatability and systematic residuals by range, angle, surface, and configuration; do not copy one universal noise value into every condition.
5. Add the actual camera and verify intrinsic/extrinsic projection on an independent target.

Dependencies: supplied picoScan150 or an authorized loaner, selected camera, fixtures, and acquisition/logger work.

### Phase 4 — moving rig and controlled flight

1. Use a hand cart/linear fixture before flight to isolate timing and motion compensation.
2. Recover known surface changes without using their truth markers to perform final registration.
3. Fly only after acquisition, timing, transform, and storage tests pass on the ground.
4. Repeat a marked route over an unoccupied permitted site with stable controls and independent level/straightedge/fixture measurements.
5. Predeclare acceptance thresholds from bench uncertainty and the project use case before viewing the final controlled-site result.

Dependencies: investigations 01–05, safety/site permission, actual hardware, and independent ground truth.

### Phase 5 — field pilot and enhancement

1. Build a local held-out dataset grouped by site segment and date.
2. Evaluate stable-pavement false positives, change magnitude/localization, coverage, and image-only versus LiDAR-assisted detection.
3. Add a learned RGB detector only if the classical/data pipeline is reliable.
4. Evaluate M3C2-like multiscale comparison, pose-graph optimization, or learned fusion one change at a time against the frozen MVP.
5. Consider edge preview only after offline results and resource measurements justify it.

## 6. Verification tests and success measures

The thresholds below are **software-verification gates or rules for setting later gates**, not claimed picoScan150/UAV accuracy.

### Unit and contract tests

| Test | Input | Expected output and pass/fail criterion |
|---|---|---|
| Schema rejection | Missing unit, frame, timestamp domain, or calibration reference | Validation fails with the exact field and no complete run is emitted. |
| Raw preservation | Valid and invalid synthetic returns | Counts by raw status match the fixture exactly; filters retain a source-ID mask. |
| Transform direction | Known translations/rotations and inverse chains | Round trip returns the input within configured floating-point tolerance and wrong frame order fails a known-axis test. |
| Quaternion handling | Sign-equivalent quaternions and non-unit input | Equivalent rotations compare equal; non-unit records are rejected or normalized only under an explicit rule. |
| Pose interpolation | Constant-velocity translation and constant-rate rotation | Endpoints and analytic midpoint agree within numerical tolerance; interpolation across the configured gap is refused. |
| Clock mapping | Known offset/drift observations | Stored coefficients and residuals recover the analytic mapping within numerical tolerance and retain the original timestamps. |
| Projection | Synthetic 3D points and camera model | Pixels match analytic/OpenCV projection within numerical tolerance; behind-camera and out-of-bounds points are rejected. |
| Determinism | Same inputs, lockfile, seed, and configuration | Truth tables and deterministic result artifacts have identical hashes; nondeterministic fields are isolated. |

### Synthetic geometric tests

| Test | Input | Pass/fail criterion |
|---|---|---|
| Identity reconstruction | Noise-free planar profiles with exact poses | Reconstructed samples and zero-change residuals agree with analytic truth within numerical discretization tolerance. |
| Sign convention | One positive and one negative known fixture | Heave/settlement signs and site z direction are correct in tables and plots. |
| Known rigid transform | Asymmetric stable controls plus a seeded translation/rotation | Refined alignment is within one-tenth of a grid cell in translation and 0.1° in rotation for this noise-free software fixture. This is not a field specification. |
| Zero-change control | Identical baseline/current surfaces | No candidate is emitted in the noise-free case. Any residual is retained as a diagnostic. |
| Known anomaly | Noise-free heave, settlement, rut, and edge-drop fixtures | Center lies within one grid cell, sign is correct, magnitude agrees within discretization tolerance, and footprint IoU is at least 0.8 for the configured fixture. |
| Timing compensation | Constant-motion fixture with known scan timing | Correct compensation returns to numerical/discretization tolerance and materially outperforms the deliberately uncompensated case. |
| Pose/timing sweep | One error source varied at a time | Output records the correct parameter; error trends are plotted; the declared failure region triggers a flag or withheld result. No fixed accuracy pass is imposed. |
| Missing profiles | Removed returns and contiguous gaps | Coverage falls by the exact expected amount; prohibited gaps remain empty; affected candidates carry flags. |
| Outliers | Declared isolated and clustered outliers | Source IDs remain traceable; robust filtering improves stable residuals without deleting the injected broad anomaly. |
| Registration leakage | Candidate region included/excluded from controls | Default control masking prevents the known anomaly from being fit away; a contaminated-control scenario is flagged in diagnostics. |
| Uncertainty calibration | Monte Carlo samples generated from the declared input distributions | Empirical coverage of the nominal interval is statistically compatible with its declared coverage using a predeclared binomial test; otherwise the model is recalibrated or marked incomplete. |

The numeric noise-free thresholds above verify implementation behavior at a selected fixture resolution. They must not appear in the application as physical sensor accuracy.

### Public-data fusion tests

| Test | Expected output and pass/fail criterion |
|---|---|
| Adapter completeness | Every public frame has the expected RGB, geometry, label, source manifest, group, and hash or a blocking discrepancy record. |
| Split leakage | No content hash, near-duplicate group, sequence, or source group crosses train/validation/test. |
| Paired design | Both branches use the same groups, labels, regions, model family, tuning budget, and operating-point selection procedure. |
| Training isolation | Imputation, scaling, feature selection, calibration, and threshold selection never see held-out groups. |
| Missing geometry | Geometry loss produces an availability flag and declared fallback; it never becomes zero-depth evidence silently. |
| Shuffled geometry | The negative-control result is published. If it retains an apparent advantage, the fusion conclusion fails pending leakage/confounding investigation. |
| Claim gate | “Improved” is prohibited when the paired held-out difference or uncertainty does not support it. A null or worse result is still a successful pipeline demonstration. |
| Reproducibility | Same data version, groups, configuration, seed, and environment reproduce predictions/metrics within declared deterministic tolerances. |

### Bench and controlled-site tests after hardware arrives

| Test | Independent reference | What must be reported before a pass threshold is set |
|---|---|---|
| Stationary plane/step/ramp | Measured fixture geometry | Bias, repeatability, invalid-return rate, residual versus range/angle/surface/configuration, temperature if available. |
| Camera calibration | Held-out calibration images/target points | Reprojection residual distribution, image coverage, calibration repeatability, and failure examples. |
| Extrinsic calibration | Independent target not used in fitting | 3D alignment and pixel reprojection residuals across the working field of view. |
| Timing/motion | Measured cart speed or known trajectory/target | Compensated versus uncompensated residual, estimated time offset/drift, uncertainty, and pose gaps. |
| Stable repeated survey | Independently judged unchanged area | Bias, robust spread, 95th/99th residual percentiles, false-candidate area, registration residual, and coverage. |
| Known geometric change | Shims/boards/level survey withheld from registration | Magnitude and sign error, localization error, footprint overlap, uncertainty coverage, and detection/omission. |
| Controlled flight | Surveyed markers and independent pavement measurements | Same metrics plus route overlap, data loss, processing time, and sensitivity to speed/altitude/heading. |

The team should set controlled-site pass/fail values from the target measurand, independently measured fixture uncertainty, and completed bench results **before** evaluating the held-out flight. A manufacturer specification alone is not an end-to-end system threshold.

### Metrics to report

#### Geometry and data quality

- signed bias, MAE, RMSE, median absolute error, and robust percentiles against synthetic/fixture truth;
- peak and median change-magnitude error by candidate;
- candidate centroid/localization error and footprint intersection-over-union;
- precision, recall, F1, false-positive count/area, and false negatives on known fixtures;
- stable-control residual distribution and held-out control residual;
- uncertainty interval coverage and fraction marked uncertainty-incomplete;
- valid-range fraction, surface coverage, point/profile density, pose gaps, packet loss, and baseline/current overlap; and
- runtime, peak memory, input/output size, and failed-stage count.

#### Vision and fusion

- precision, recall, F1, average precision/PR-AUC, IoU where masks exist, and confusion matrix;
- result at the declared operating threshold plus the full precision-recall curve;
- metrics per held-out frame/sequence and an aggregate with whole-group uncertainty;
- paired RGB-plus-shape minus RGB-only differences;
- valid-geometry coverage and performance stratified by missing/sparse geometry, lighting, and source group; and
- inference/feature time and peak memory.

### Demonstration completion gate

The pre-hardware processing brief is implemented when a clean laptop can reproduce:

1. input validation and immutable run provenance;
2. zero-change and known-change synthetic reports with truth-based metrics;
3. motion/timing/pose/dropout stress results and quality flags;
4. paired public image-only and image-plus-shape predictions on leakage-safe groups;
5. negative controls and honest uncertainty; and
6. investigation 08-compatible candidate and report records carrying the required disclaimer.

No minimum field accuracy or fusion improvement is part of this pre-hardware gate.

## 7. Cost, mass, power, or resource implications

### MVP resources

| Resource | Planning implication |
|---|---|
| Software licenses | $0 for the proposed open-source stack; confirm model-weight and dataset licenses separately. |
| New flight hardware | None for pre-hardware processing. The picoScan150 is assumed supplied only if selected. |
| Flight mass/power | None added by laptop/offline processing. Onboard logging requirements belong to investigation 04. |
| Compute | Existing multicore laptop. Process scans/images in chunks; GPU is optional for a later learned RGB model. |
| Storage | Raw capture plus immutable intermediates and reports. Investigation 04 must measure real byte rates; investigation 08 owns retention/backup. |
| Network/cloud | Not required. Public datasets require initial download; processing and report viewing should work offline. |

Large point sets should be partitioned by survey, flight, spatial tile, and time window. Cache a stage only when its input hashes, code version, calibration, and parameters are part of the cache key. Avoid loading an entire survey into memory when a tiled pass is sufficient.

### Software effort estimate

These are planning ranges for one student-developer equivalent after interfaces are agreed, not completed effort:

| Work package | Estimate |
|---|---:|
| Schemas, validation, provenance, and fixtures | 3–5 person-days |
| Frames, clocks, interpolation, and motion compensation | 4–7 person-days |
| Surface reconstruction, registration, change, and uncertainty MVP | 7–11 person-days |
| Public-data image-only and shape-fusion baseline | 5–8 person-days |
| Metrics, quality gates, exports, and report integration | 4–6 person-days |
| Automated tests and reproducibility documentation | 4–7 person-days |
| **Pre-hardware total** | **27–44 person-days** |

Bench adapters, calibration, moving-rig experiments, controlled flight, and field-data labeling are additional work because they depend on hardware and site access. Parallel student work can reduce calendar time only after schemas, frames, and ownership are frozen.

### Optional onboard/real-time path

Real-time edge inference is not required for the MVP. A later onboard component should be limited initially to acquisition-health previews: packet loss, pose validity, storage remaining, and approximate coverage. Full change detection still requires a baseline, repeat registration, quality review, and laptop resources. Do not select an edge computer or promise a processing rate until investigation 04 measures representative data and this pipeline is profiled.

## 8. Risks, open decisions, and fallback

### Risks and mitigations

| Risk | Consequence | Mitigation/fallback |
|---|---|---|
| Sparse or uneven swept coverage | Holes or unstable local surfaces | Compute coverage before change; change route/orientation; report uncovered regions; fall back to profile-only comparison. |
| Pose drift or weak world position | False broad change and poor localization | Use markers/RTK as available, stable-control rigid refinement, held-out controls, and reject unobservable comparisons. |
| Time offset/drift | Motion smear and camera/range mismatch | Preserve clock domains, estimate mapping, use ground-rig timing tests, propagate timing uncertainty, slow the controlled pass if needed. |
| Bad lighting, blur, wet surface, or shadows | RGB false positives/domain shift | Exposure/blur flags, repeat acquisition, augmentation only on training data, geometry-only candidate where valid. |
| Missing labels | Unverifiable model metrics | Use synthetic truth and licensed public labels; label a small controlled dataset with a written protocol; do not self-grade on training data. |
| Sensor occlusion or invalid returns | Biased geometry or false depression | Visibility and status checks, valid-fraction feature, no large-gap interpolation, alternative pass direction. |
| Insufficient 2D geometry | Surface is not observable | Reorient/replan sweep, use controlled profiles instead of a 3D claim, or limit output to RGB-only observations. |
| Registration absorbs real change | False negatives | Stable controls outside candidates, one rigid transform, held-out control validation, synthetic leakage test. |
| ICP converges to a wrong local solution | Plausible but false alignment | Strong seed, transform bounds, asymmetric controls/markers, overlap/residual gates, manual diagnostic plot. |
| Uncertainty model is incomplete | False precision | Expose missing terms, use repeated measurements/Monte Carlo, block measurement language with a flag. |
| Fusion gains come from leakage | Unsupported picoScan150 claim | Grouped split, paired design, train-only preprocessing, shuffled-geometry negative control. |
| Public stereo domain differs from UAV LiDAR | Method result does not transfer | Label the modality/source on every result and repeat evaluation with actual synchronized PaveWatch data. |
| Fine cracks attributed to LiDAR | Misrepresents sensor capability | Keep modality-specific evidence and describe fine cracks as RGB detections with optional geometric context. |
| Compute/storage exceeds laptop | Incomplete run | Tile/chunk processing, profile stages, cache by hash, lower visualization density without deleting raw evidence. |

### Fallback ladder

1. **No hardware:** run analytic geometric fixtures plus the public stereo paired experiment.
2. **No usable paired public data:** run a synthetic aligned texture/height fusion interface test and make no empirical fusion conclusion.
3. **picoScan150 but no flight-ready UAV:** use stationary and moving ground rigs to verify real packets, timing, calibration, and known profiles.
4. **No RTK:** use a marked site-local frame and surveyed/reference targets; limit absolute-geolocation claims.
5. **Poor pose:** perform stationary/profile comparisons or slow controlled ground passes; withhold moving 3D change.
6. **Sparse/occluded LiDAR:** publish RGB-only observations and geometry coverage; never impute metric deformation from imagery alone.
7. **Poor RGB:** publish valid geometric candidates without a visual defect class and request re-imaging.
8. **Registration failure:** present each survey separately with diagnostics; do not emit baseline/current change.

### Open decisions requiring central agreement

1. What exact geometric measurands and candidate scales are the first MVP targets?
2. What scan-plane mounting orientation and mission direction provide useful pavement coverage?
3. What are the authoritative raw, normalized, and replay formats for LiDAR, IMU, pose, and images?
4. Which device clock is the survey-time authority, and how is offset/drift observed?
5. Is the navigation output ENU or NED, and where is the single tested conversion boundary?
6. Will RTK be available, and what markers or site-local controls are the fallback?
7. How will extrinsics be calibrated and checked after mounting or a hard landing?
8. What maximum pose gap, synchronization uncertainty, coverage, and registration residual block a result? Values must follow characterization.
9. Which public-data fusion experiment will appear in the application attachment, if any?
10. Who owns controlled-site ground truth and ensures it is not used both to register and evaluate the same result?
11. Will final application language use offline/local post-flight processing with optional cloud sync?

## 9. Sources

All external sources were accessed **2026-09-19**.

1. SICK AG, **picoScan150 2D LiDAR Sensors — Operating Instructions**, document 8028323/1THA/2025-09-03. Device setup, scan/IMU data, Ethernet output, configuration, diagnostics, and telegram reference: https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf
2. Open Robotics, **REP 103 — Standard Units of Measure and Coordinate Conventions**. SI units, right-handed axes, body/camera conventions, and ENU/NED suffix frames: https://www.ros.org/reps/rep-0103.html
3. Open Robotics, **REP 105 — Coordinate Frames for Mobile Platforms**. Earth, map, odom, and body-frame semantics and transform authority: https://www.ros.org/reps/rep-0105.html
4. OpenCV, **Camera Calibration and 3D Reconstruction (calib3d)**. Camera matrix, distortion, calibration, rigid pose, and 3D-to-image projection: https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
5. SciPy, **Slerp — Spherical Linear Interpolation of Rotations**. Shortest-path constant-angular-velocity interpolation between rotations: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Slerp.html
6. Open3D, **ICP Registration** and **Robust Kernels**. Point-to-point/point-to-plane registration, convergence information, and robust outlier weighting: https://www.open3d.org/docs/latest/tutorial/t_pipelines/t_icp_registration.html and https://www.open3d.org/docs/latest/tutorial/pipelines/robust_kernels.html
7. Lague, D., Brodu, N., and Leroux, J., “Accurate 3D comparison of complex topography with terrestrial laser scanner: Application to the Rangitikei canyon (N-Z),” *ISPRS Journal of Photogrammetry and Remote Sensing*, 2013. Local-normal multiscale comparison, roughness, density, registration error, and level of detection: https://doi.org/10.1016/j.isprsjprs.2013.04.009
8. Joint Committee for Guides in Metrology, **JCGM 100:2008 — Evaluation of measurement data: Guide to the expression of uncertainty in measurement**. Measurement models, standard/combined/expanded uncertainty, propagation, and reporting: https://doi.org/10.59161/JCGM100-2008E
9. scikit-learn developers, **Precision-Recall**. Precision/recall tradeoff, operating thresholds, and average precision definition: https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html
10. Local project reference, **Datasets and pre-hardware pipeline demonstration**. Dataset selection, analytic surface/profile fixtures, canonical public-data records, split rules, and pre-hardware limitations: <code>../07-datasets-pipeline-demonstration/findings.md</code>
11. Local project reference, **Reporting, data management, and user interface**. Survey/run/anomaly provenance, quality flags, local-first evidence storage, and report interface: <code>../08-reporting-data-management-user-interface/findings.md</code>
12. Local project reference, **PaveWatch application draft**. Current problem/solution statement and cloud-processing wording requiring central reconciliation: <code>../../main.md</code>
