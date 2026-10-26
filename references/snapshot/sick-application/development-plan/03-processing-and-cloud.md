### 8. Cloud processing and data management

After landing, a transfer client will upload the survey to private object storage. Each survey will include a manifest containing site and survey identifiers, time domains, calibration identifiers, firmware and sensor settings, file sizes, and SHA-256 hashes. Uploads will be resumable, and the service will verify every file before scheduling processing. A local source copy will be retained until cloud integrity and a recovery copy are confirmed.

The initial deployment will use one containerized processing worker, private object storage, and a metadata service. The cloud provider will be selected during deployment preparation; processing interfaces will remain portable. A single application service can use SQLite for the initial catalog with serialized writes and tested backups. Expansion to multiple writers will use a server database with a defined migration path.

| Data product | Proposed representation | Purpose |
|---|---|---|
| Original survey | Packet captures, images, flight logs, JSON manifest | Replayable acquisition evidence |
| Calibration | Versioned JSON and target observations | Intrinsics, transforms, timing mappings and uncertainty |
| Normalized measurements | Parquet with units, frames, sequence and quality fields | Efficient repeatable processing |
| Processing run | Input hashes, baseline ID, container version, configuration, seed | Reproduce an analysis |
| Candidate changes | Geometry, magnitude, uncertainty, evidence links, flags | Human review and comparison |
| Reports | HTML/PDF, CSV/JSON; GeoJSON when georeferencing permits | Shareable engineering outputs |

Jobs will be idempotent: retrying an upload or queue message must not duplicate a survey or overwrite a completed result. Algorithm or calibration changes create a new processing run. The accepted baseline will remain explicitly linked to each comparison.

Authenticated access will control raw-data download and report release. Storage will be private by default; credentials will stay outside code and survey files. Compute will run for queued work and stop when idle. Storage retention, transfer volume, compute duration, and monthly spending will be monitored. Cloud operating costs will be tracked separately from initial hardware acquisition.

### 9. Geometry and change detection

The geometric pipeline will proceed through six stages:

1. **Validate acquisition.** Check sequence continuity, timestamps, calibration compatibility, image completeness, and flight-state coverage. Record gaps rather than silently filling them.
2. **Reconstruct profiles.** Convert angle/range samples into the sensor frame, then transform them using calibrated mounting geometry and interpolated vehicle pose. Account for scan timing instead of assuming an entire scan was measured at one instant.
3. **Establish valid support.** Filter invalid returns and identify where surface coverage, incidence, motion, or pose quality is inadequate. Preserve masks for unsupported regions.
4. **Register surveys.** Initialize from navigation and marker observations; refine on stable geometry. Exclude changed objects from alignment and evaluate independent check targets.
5. **Compare surfaces.** Estimate local reference planes or normals, calculate baseline/current displacement on common support, and require spatially persistent evidence. Avoid fitting away the deformation being sought.
6. **Report supported changes.** Attach coverage, uncertainty, residuals, and visual evidence to each candidate. Withhold quantitative changes where alignment or sampling is inadequate.

A Python implementation using NumPy/SciPy, OpenCV, and Open3D will provide transparent initial algorithms. Dependencies and execution settings will be pinned. Robust registration is useful for refinement but will not be treated as proof of correct alignment on repetitive or nearly planar pavement. [7, 8]

The uncertainty model will consider sensor repeatability, pose, timing, mounting calibration, and survey registration. Repeated observations will establish empirical variation and false-positive behavior on unchanged pavement. A numerical detection threshold will be accepted only when it exceeds the characterized uncertainty for the relevant operating conditions.

### 10. RGB and range-assisted defect analysis

The image branch will identify visible crack-like features and pavement-distress candidates. Calibrated projection will associate supported LiDAR samples with image locations. Range-derived features may include local height residual, slope, roughness, and a validity mask. Unsampled pixels will retain missing-data status; interpolation will not create assumed measurements.

The first fusion experiment will compare an image-only model with an image-plus-geometry model using the same examples, preprocessing, train/test groups, and evaluation metrics. Where appropriate, a simple classifier provides an inspectable starting point before larger models are introduced. Performance will be reported by defect class and operating condition, including cases where geometry offers no improvement.

Images from the same route, adjacent frames, augmented copies, and repeated visits to the same test segment will remain in the same evaluation group to avoid leakage. The final controlled-site test will be held out from training and tuning. Crack visibility will be measured against known targets at the selected altitude, focus, and exposure; no camera resolution alone will be used as a crack-width guarantee.

### 11. Reporting and operator workflow

The interface will provide three principal views: survey and baseline selection, a candidate map/list, and a detail view with current/baseline evidence. Each candidate will show location or local coordinates, observation type, supported dimensions or displacement, measurement uncertainty, data-quality flags, and review state.

Algorithm score, measurement uncertainty, and data quality will be displayed separately. A reviewer may confirm the need for field inspection, reject an artifact with a reason, or request another survey. Review history will be retained without rewriting the original algorithm output.

Exports will carry the same limitations as the interface. A local-coordinate plot is valid when global positioning is unavailable; geographic exports will require an explicit valid transformation. Every illustrated or experimental result will identify whether it comes from synthetic data, a public dataset, or team measurements.

The output supports maintenance review. It does not independently certify pavement safety or authorize repair. Its practical value will be evaluated by whether a reviewer can locate a candidate, understand the supporting evidence, and distinguish a measured change from an uncertain observation.
