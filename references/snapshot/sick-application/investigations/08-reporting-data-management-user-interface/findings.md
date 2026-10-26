# Reporting, data management, and user interface

## 1. Scope and recommendation

### Recommendation

Build the PaveWatch MVP as a **local-first evidence system**, not as a cloud product. Keep large sensor files in immutable survey folders, keep relationships and review state in one SQLite catalog, and generate a self-contained HTML report that can be printed to PDF. Export anomaly locations and summaries as GeoJSON, CSV, and JSON where their coordinate systems permit it. Cloud synchronization can be added later, but it is not required for the competition demonstration.

The recommended minimum architecture is:

| Concern | MVP choice | Reason |
|---|---|---|
| Raw evidence | Files in a versioned survey folder | LiDAR packets, images, and logs are too large and awkward to store as database blobs. |
| Integrity | SHA-256 for every ingested artifact plus a manifest hash | Detects accidental or unauthorized changes after ingest. |
| Relationships and review | SQLite with foreign keys enabled | One portable local file is sufficient for a single-workstation or small-team MVP. |
| High-volume derived tables | Parquet, with an explicit schema version | Efficient for profiles, poses, predictions, and other columnar results. |
| Mapped interchange | GeoJSON in WGS 84 only | Standard, inspectable, and compatible with common mapping tools. |
| Local engineering coordinates | Parquet or JSON with an explicit frame identifier and metric units | RFC 7946 GeoJSON does not represent an arbitrary site-local coordinate reference system.[4] |
| Human-readable output | Self-contained HTML plus browser-produced PDF | Works offline and can combine summaries, images, plots, flags, and provenance links. |
| MVP interface | Three views: survey selection, anomaly map/list, anomaly detail/review | Demonstrates the whole workflow without building an enterprise asset-management product. |

The catalog should be treated as an index and review ledger, not as the sole source of truth. Every survey folder must carry enough manifests and schema-versioned records to audit it and rebuild the catalog. Raw inputs are never silently replaced. A corrected calibration, processing setting, or algorithm creates a new processing run; it does not rewrite the old run.

The report must describe outputs as **candidate changes for human review**. It must not certify pavement safety, declare legal or accessibility compliance, or automatically authorize maintenance. “Severity” should be labeled **review priority** until field validation establishes a defensible severity model.

### What this investigation delivers

This brief defines:

- the evidence and provenance records needed from acquisition through review;
- a survey-folder layout and relational model;
- minimal example records for a survey, processing run, anomaly, and quality flag;
- the three-view MVP interface and a conceptual report;
- verification tests for provenance, baseline selection, missing data, quality flags, reproducibility, export, offline behavior, and restore;
- planning estimates for storage, compute, software, and implementation effort; and
- decisions required from acquisition, synchronization, mission-planning, and processing work.

It does not claim that hardware data has been captured or that detection performance has been measured. The illustrative record in Section 3 is simulated.

## 2. Evidence and assumptions

### Evidence behind the architecture

1. The picoScan150 operating instructions document Ethernet scan and IMU streaming, configuration parameters, diagnostic information, and device-specific telegrams. The current manual also documents IMU data and configurable Ethernet destinations.[1] These facts make the sensor configuration and firmware/configuration snapshot part of the evidence, not incidental setup notes.
2. SQLite provides transactional updates and foreign-key constraints, although foreign-key enforcement must be explicitly enabled for each connection.[2] This suits a small local catalog, provided the application tests that enforcement at startup.
3. SQLite's documentation warns that a write-ahead log is part of database state while it exists. Copying only the main database file during active WAL use can lose committed transactions or corrupt the copy.[3] PaveWatch should use SQLite's backup API, <code>VACUUM INTO</code>, or a clean closed/checkpointed copy rather than ordinary file copying for live backups.
4. RFC 7946 defines GeoJSON coordinates using WGS 84 longitude and latitude in decimal degrees.[4] Therefore site-local east/north coordinates in meters must not be written to a file labeled GeoJSON. They remain in a local-frame record until a valid georeferencing transform is available.
5. JSON Schema 2020-12 can validate the structure and required fields of JSON manifests.[5] The schema version and validator result should be stored at ingest.
6. Apache Parquet stores typed columnar data and file metadata.[6] It is appropriate for large derived tables, but PaveWatch must pin writer settings and schema versions rather than assuming all format features are universally readable.
7. W3C PROV models provenance in terms of entities, activities, and agents.[7] The MVP does not need an RDF implementation, but the useful mapping is direct: artifacts and surveys are entities, processing and review are activities, and software versions/operators/reviewers are agents.
8. NIST FIPS 180-4 defines SHA-256 and explains that a message digest can detect whether a message changed after the digest was generated.[8] A hash is an integrity check, not proof that the original measurement was correct or that the person who supplied it was authorized.

### Project-state labels

Every survey, run, anomaly, figure, and export must carry one of these evidence labels:

| Label | Meaning |
|---|---|
| <code>proposed</code> | Architecture, component, test, or field that has not yet been implemented. |
| <code>available_to_borrow</code> | Equipment has been confirmed as borrowable; it is not owned or necessarily reserved. |
| <code>planned</code> | An approved future action or configuration, not completed evidence. |
| <code>simulated</code> | Generated data with known parameters; useful for software verification only. |
| <code>public_data</code> | External data with a recorded source, version, license, and retrieval record. |
| <code>measured</code> | Captured by the team with a traceable acquisition record. No current repository evidence qualifies yet. |

The user interface must display this label near every result. A simulated anomaly must not become visually indistinguishable from a field measurement when exported or screenshotted.

### Assumptions

- The first demonstration uses one controlled sidewalk or parking-lot site.
- The picoScan150 is supplied only if the team is selected; it is not charged to the capstone budget.
- Raw data is recorded locally during flight and processed on an existing laptop after landing.
- The first deployment has one active writer to the catalog. Multiple people may receive read-only exports.
- A survey can exist without world coordinates. A repeatable site-local frame is sufficient for early bench and controlled-site tests.
- A baseline is an ordinary accepted survey selected for a particular comparison; it is not a special file that can be overwritten by a new baseline.
- Fine cracks are primarily RGB observations. LiDAR may provide contextual geometry or fusion features, but the report must not claim that the 2D LiDAR measured a fine crack unless later validation supports that claim.
- Confidence, measurement uncertainty, and data quality are separate concepts. A high model score does not erase missing calibration, poor registration, or incomplete coverage.

### Central terminology

| Term | Definition |
|---|---|
| Survey | The complete evidence package for one attempted observation of a site over a stated time interval. Failed or incomplete attempts remain surveys. |
| Flight | One UAV operation within a survey. A survey may contain multiple flights or a bench acquisition with no flight. |
| Baseline link | A versioned relationship declaring which accepted earlier survey a processing run compares against. |
| Processing run | One immutable execution using identified inputs, code, environment, parameters, and random seed where applicable. |
| Candidate anomaly | A processing output that warrants review; not a certified defect or repair instruction. |
| Review | A human decision about a candidate, including field-verification status and notes. Review does not rewrite the algorithm output. |
| Artifact | Any stored file or directory represented by a URI, media type, byte count, and integrity value. |
| Quality flag | A structured condition affecting scope, confidence, interpretability, or release of a result. |

## 3. Proposed components or software

### 3.1 Local-first components

```text
Acquisition package
  raw picoScan150 + IMU + RGB + pose/telemetry + flight log
                 |
                 v
Ingest/validation
  schema check + required-stream check + SHA-256 inventory
                 |
         +-------+--------+
         |                |
         v                v
Immutable survey files    SQLite catalog
large evidence/artifacts  IDs, relationships, run/review state
         |                |
         +-------+--------+
                 v
Versioned processing run
  registration + fusion/change detection + quality rules
                 |
         +-------+--------+
         |                |
         v                v
Derived Parquet/plots     Candidate anomalies + evidence links
         |                |
         +-------+--------+
                 v
Human review
  accept candidate / dismiss / needs field visit / confirmed in field
                 |
                 v
Static report + CSV/JSON + WGS 84 GeoJSON when available
                 |
                 v
Future survey may select an accepted survey as its historical baseline
```

Recommended implementation building blocks are:

- Python for ingest, processing integration, export, and report generation;
- SQLite for metadata and review state, with <code>PRAGMA foreign_keys = ON</code> checked for every connection;
- JSON plus JSON Schema 2020-12 for manifests and small exchange records;
- Parquet for large derived tables such as synchronized samples, surface profiles, poses, and predictions;
- ordinary image files for RGB evidence and PNG/SVG for plots;
- server-rendered or generated HTML with assets bundled locally; and
- browser print-to-PDF for the attachment or demonstration handout.

The implementation should not require a paid cloud database, map-tile subscription, or internet connection. A conceptual site plan, orthomosaic, or locally stored image can be the map background. If an interactive mapping library is selected later, its JavaScript/CSS and any permitted tiles must be bundled locally for the offline demonstration.

### 3.2 Survey-folder design

```text
pavewatch-data/
  catalog/
    pavewatch.sqlite
    backups/
  sites/
    <site-id>/
      site.json
      site-assets/
      surveys/
        <survey-id>/
          manifest.json
          manifest.schema.json
          checksums.sha256
          config/
            lidar-config.json
            camera-config.json
            mission-plan.json
            frame-tree.json
          calibration/
            calibration-ref.json
          raw/
            lidar/
            imu/
            rgb/
            pose/
            flight-controller/
          ingest/
            validation.json
            inventory.parquet
          runs/
            <run-id>/
              run.json
              parameters.json
              environment.json
              inputs.json
              derived/
                synchronized-samples.parquet
                surface-profiles.parquet
                anomalies-local.parquet
                anomalies.geojson
              quality-flags.json
              metrics.json
              evidence/
              report/
                index.html
                report.pdf
                report.json
                anomalies.csv
```

Rules for this layout:

1. Identifiers are generated independently of display names. Use lowercase UUIDs or sortable UUID-compatible identifiers; never use a mutable site name or raw filename as the primary key.
2. All paths stored in a survey manifest are relative to that survey root. The complete project may then be moved without breaking links.
3. Raw files become read-only after successful ingest. Corrections create a new artifact or survey revision with an explicit derivation link.
4. The catalog stores artifact URIs and hashes, not image or LiDAR blobs.
5. Every JSON record includes <code>schema_version</code>. Database schema changes use ordered migrations recorded in a <code>schema_migration</code> table.
6. Every numeric measurement stores or inherits an explicit unit. Store physical values in SI units internally and format millimeters or centimeters only in the interface.
7. Every spatial record includes <code>frame_id</code>. Local metric and WGS 84 coordinates are separate fields, not interchangeable arrays.
8. The SHA-256 list excludes itself and is finalized before hashing the canonical manifest. The manifest records the hash-list URI and its digest, avoiding a self-referential hash.
9. Generated reports include stable identifiers but use relative links only. A packaged report must not leak workstation absolute paths or student credentials.

### 3.3 Minimal relational schema

The following is the minimum logical model. It can be implemented as SQLite tables without adopting every field on the first day.

#### Core records

| Record | Required fields | Important rules |
|---|---|---|
| <code>site</code> | <code>site_id</code>, display name, local-frame definition, boundary artifact, created time | World coordinates may be null; local origin and axis convention may not be implicit. |
| <code>survey</code> | <code>survey_id</code>, <code>site_id</code>, evidence label, attempt start/end UTC, status, manifest artifact, created by | Status includes planned, ingesting, incomplete, accepted, rejected, or archived. An incomplete survey is retained. |
| <code>flight</code> | <code>flight_id</code>, <code>survey_id</code>, mission-plan artifact, actual flight-log artifact, start/end UTC, operator | Planned route and executed track are separate artifacts. Bench acquisitions use an acquisition record with flight null. |
| <code>sensor_configuration</code> | <code>config_id</code>, sensor identifiers, firmware/software versions, saved configuration artifacts, effective time | Include scan output format, performance profile, active filters, network/output configuration, camera mode, and settings provenance. |
| <code>calibration</code> | <code>calibration_id</code>, type, version, method, effective interval, parameter artifact, residual/quality summary | Camera intrinsics, LiDAR-camera extrinsics, body transforms, and time offset may be separate linked calibrations. |
| <code>artifact</code> | <code>artifact_id</code>, owning survey/run, role, relative URI, media type, bytes, SHA-256, created time | Hash is required before an artifact may support a released result. Directories receive a manifest, not a guessed directory hash. |
| <code>processing_run</code> | <code>run_id</code>, current survey, baseline survey, code revision, environment artifact, parameter artifact/hash, status, start/end UTC | New inputs or parameters require a new run. Baseline and current survey cannot be the same. |
| <code>anomaly</code> | <code>anomaly_id</code>, <code>run_id</code>, type, detection channel, local geometry/frame, magnitude/unit if supported, uncertainty if supported, confidence semantics, review priority | Null means unknown; never substitute zero. Preserve the algorithm output separately from human review. |
| <code>anomaly_evidence</code> | anomaly ID, artifact/sample ID, evidence role, time/row/pixel/profile locator | Evidence role includes current RGB, baseline RGB, current range, baseline range, change plot, or context. |
| <code>quality_flag</code> | <code>flag_id</code>, code, scope type/ID, severity, rule version, message, created time, disposition | Flags can block processing, block a numeric claim, or only warn. They propagate to anomalies and reports. |
| <code>review</code> | <code>review_id</code>, anomaly ID, reviewer, decision, field-verification status, UTC timestamp, note | Append a new review event; do not overwrite history. |
| <code>baseline_link</code> | site ID, current survey, baseline survey, purpose, selected by, selected UTC | The processing run freezes the baseline ID it used even if a later preferred baseline is selected. |

#### Controlled values

Use controlled enumerations initially and version them rather than allowing arbitrary spellings:

- anomaly type: <code>heave</code>, <code>settlement</code>, <code>rut</code>, <code>edge_drop</code>, <code>pothole_like_depression</code>, <code>crack_like_visual_feature</code>, <code>unexplained_change</code>;
- detection channel: <code>geometry</code>, <code>rgb</code>, <code>rgb_plus_geometry</code>;
- review decision: <code>unreviewed</code>, <code>candidate_retained</code>, <code>dismissed</code>, <code>needs_more_data</code>;
- field status: <code>not_requested</code>, <code>requested</code>, <code>visited_unconfirmed</code>, <code>visited_confirmed</code>, <code>not_applicable</code>;
- flag severity: <code>info</code>, <code>warning</code>, <code>blocking</code>;
- review priority: <code>routine</code>, <code>elevated</code>, <code>urgent_review</code>, with a visible note that priority is not a safety rating.

### 3.4 Example records

All values below are illustrative. They describe a synthetic software demonstration, not a picoScan150 field measurement.

#### Survey

~~~json
{
  "schema_version": "pavewatch.survey/1.0",
  "survey_id": "sur_demo_current_20260915",
  "site_id": "site_synthetic_walkway_01",
  "evidence_label": "simulated",
  "status": "accepted",
  "attempt_start_utc": "2026-09-15T14:00:00Z",
  "attempt_end_utc": "2026-09-15T14:05:00Z",
  "flight_ids": [],
  "sensor_config_id": "cfg_simulator_v1",
  "calibration_ids": ["cal_simulator_identity_v1"],
  "local_frame_id": "synthetic_walkway_enu_v1",
  "world_georeference_status": "unavailable",
  "manifest_artifact_id": "art_manifest_current_01",
  "created_by": "pavewatch-synthetic-generator",
  "limitations": [
    "Pre-hardware synthetic input",
    "No UAV, picoScan150, camera, or field site was used"
  ]
}
~~~

#### Processing run

~~~json
{
  "schema_version": "pavewatch.processing-run/1.0",
  "run_id": "run_demo_change_20260919_001",
  "purpose": "synthetic_baseline_change_demo",
  "current_survey_id": "sur_demo_current_20260915",
  "baseline_survey_id": "sur_demo_baseline_20260901",
  "status": "succeeded_with_warnings",
  "code_revision": "REPLACE_WITH_GIT_COMMIT_AT_RUN_TIME",
  "environment_artifact_id": "art_environment_001",
  "parameters_artifact_id": "art_parameters_001",
  "parameters_sha256": "REPLACE_WITH_64_HEX_DIGITS",
  "random_seed": 20260919,
  "started_utc": "2026-09-19T17:20:00Z",
  "ended_utc": "2026-09-19T17:20:18Z",
  "output_artifact_ids": [
    "art_anomalies_local_001",
    "art_change_plot_001",
    "art_report_001"
  ],
  "quality_flag_ids": ["qf_pre_hardware_001", "qf_no_world_georef_001"]
}
~~~

#### Candidate anomaly

~~~json
{
  "schema_version": "pavewatch.anomaly/1.0",
  "anomaly_id": "anom_demo_settlement_001",
  "run_id": "run_demo_change_20260919_001",
  "evidence_label": "simulated",
  "anomaly_type": "settlement",
  "detection_channel": "geometry",
  "local_frame_id": "synthetic_walkway_enu_v1",
  "centroid_local_m": {"east": 8.2, "north": 1.4, "up": 0.0},
  "geometry_local_artifact_id": "art_anomalies_local_001",
  "geometry_wgs84": null,
  "estimated_change_m": -0.028,
  "uncertainty_m": null,
  "dimensions_m": {"length": 1.1, "width": 0.7},
  "confidence": null,
  "confidence_definition": "not_calibrated",
  "review_priority": "elevated",
  "priority_basis": "illustrative_threshold_only",
  "quality_flag_ids": ["qf_pre_hardware_001", "qf_no_world_georef_001"],
  "field_verification_status": "requested",
  "claim": "Candidate synthetic surface change for workflow demonstration; not a field observation or safety determination."
}
~~~

The negative sign above means downward change along the named frame's positive-up axis. That convention must appear in the schema and user interface; “2.8 cm change” without direction is insufficient.

#### Quality flag

~~~json
{
  "schema_version": "pavewatch.quality-flag/1.0",
  "flag_id": "qf_pre_hardware_001",
  "code": "PRE_HARDWARE_SYNTHETIC_INPUT",
  "scope_type": "processing_run",
  "scope_id": "run_demo_change_20260919_001",
  "severity": "warning",
  "blocks_processing": false,
  "blocks_numeric_claim": false,
  "blocks_field_claim": true,
  "rule_version": "reporting-rules/1.0",
  "message": "This run uses synthetic inputs and cannot validate field or picoScan150 performance.",
  "created_utc": "2026-09-19T17:20:18Z",
  "disposition": "open"
}
~~~

### 3.5 Quality flag taxonomy

The first release should implement at least these machine-readable flags:

| Code | Typical scope | Default effect |
|---|---|---|
| <code>PRE_HARDWARE_SYNTHETIC_INPUT</code> | survey/run | Blocks field-performance claims. |
| <code>PUBLIC_DATA_DOMAIN_MISMATCH</code> | survey/run | Requires dataset/source disclosure. |
| <code>MISSING_REQUIRED_STREAM</code> | survey | Blocks affected processing branch. |
| <code>INCOMPLETE_CAPTURE</code> | survey/area | Warns or blocks comparison for uncovered area. |
| <code>CHECKSUM_MISMATCH</code> | artifact | Blocks use and export of affected artifact. |
| <code>SCHEMA_VALIDATION_FAILED</code> | record | Blocks ingest until quarantined or corrected as a new record. |
| <code>CALIBRATION_MISSING</code> | survey/run/anomaly | Blocks calibrated dimensions or magnitude. |
| <code>CALIBRATION_OUT_OF_INTERVAL</code> | survey/run | Blocks or warns according to validation policy. |
| <code>TIME_SYNC_UNVERIFIED</code> | survey/run | Blocks strong sensor-fusion claims. |
| <code>REGISTRATION_RESIDUAL_HIGH</code> | run/anomaly | Blocks magnitude or lowers review confidence according to a centrally approved threshold. |
| <code>BASELINE_INCOMPATIBLE</code> | run | Blocks comparison. |
| <code>NO_WORLD_GEOREFERENCE</code> | survey/anomaly | Suppresses WGS 84 GeoJSON; local map remains allowed. |
| <code>RGB_EVIDENCE_UNAVAILABLE</code> | anomaly | Shows geometry evidence without implying missing imagery is negative evidence. |
| <code>RANGE_EVIDENCE_UNAVAILABLE</code> | anomaly | Prevents an RGB-only result from being presented as LiDAR-supported. |
| <code>OUTSIDE_VALIDATED_RANGE</code> | anomaly | Requires human review and limitation text. |
| <code>LOW_VALID_RETURN_FRACTION</code> | area/anomaly | Warns or blocks based on the processing policy. |

Thresholds are deliberately absent here. Investigation 06 and later validation must own numerical thresholds and their evidence.

### 3.6 Prioritized MVP interface

The MVP needs three views. They may be interactive pages in a local application or sections of a generated report; the data contract is the same in either form.

#### Priority 1 — Survey and baseline selection

Purpose: establish what was captured and what comparison will be made before showing anomaly results.

Required content:

- site and survey identifiers, evidence label, date/time, status, and operator;
- planned route versus actual coverage when available;
- sensor configuration and calibration versions;
- data-completeness summary by modality;
- all blocking and warning flags;
- eligible historical baselines with date, coverage, modality, and compatibility reason;
- explicit baseline confirmation; and
- processing-run selector so an old report cannot silently display the newest run.

Primary actions are “select baseline,” “open existing run,” and “start a new run.” The interface must not allow a current survey to be its own baseline.

#### Priority 2 — Candidate map and review queue

Purpose: let a maintenance-oriented reviewer understand where attention is needed and why.

Required content:

- local site image/plan or WGS 84 map only when georeferencing is valid;
- current and baseline dates plus run ID;
- candidate markers/areas synchronized with a sortable list;
- filters for anomaly type, detection channel, review priority, review status, and quality flags;
- candidate type, signed change magnitude and unit when supported, approximate dimensions, confidence definition, and field-verification status;
- stable-control and no-data areas so an empty part of the map is not mistaken for verified unchanged pavement; and
- visible total counts before and after filtering.

Color must not carry meaning alone. Each marker also needs a label, shape, or icon. “No candidate detected,” “not surveyed,” and “invalid data” require different visual states.

#### Priority 3 — Candidate evidence, provenance, and review

Purpose: support a defensible human decision and make the result traceable.

Required content:

- anomaly ID, type, detection channel, local position/frame, and optional geographic position;
- current and baseline RGB crops when available;
- current and baseline range/profile evidence plus a change plot for geometric candidates;
- dimensions, signed magnitude, uncertainty, score, and plain-language definition of each value;
- inherited quality flags and their effect on the claim;
- source sample/artifact IDs, processing version, parameter hash, calibration, and configuration;
- append-only desktop-review decision and note;
- separate field-verification status, visit date, evidence, and reviewer; and
- export/print link to the frozen report snapshot.

Every one of these views and every generated figure based on public or synthetic input must carry this exact statement from investigation 07:

> Pre-hardware software demonstration using public and/or synthetic data. Not a field validation of PaveWatch or the SICK picoScan150.

#### Later enhancements, not MVP requirements

- side-by-side synchronized image pan/zoom and profile cursor;
- time-series trend charts across more than two surveys;
- team assignments, comments, and notifications;
- mobile field-verification form with offline synchronization;
- role-based multi-user authentication and approval workflow;
- organization-specific severity/maintenance rules after validation;
- cloud replication and cross-site portfolio summaries; and
- integration with a customer asset-management or work-order system.

## 4. Interfaces and data flow

### 4.1 End-to-end state transitions

```text
planned
  -> capturing
  -> ingesting
  -> incomplete OR accepted
  -> processing
  -> processed_with_warnings OR processed
  -> under_review
  -> report_released
  -> archived
```

Failures do not erase evidence. A failed ingest remains in a quarantine location with a validation record. A failed processing run records its code/configuration and error summary. A dismissed candidate remains linked to its original algorithm result and review event.

### 4.2 Ingest contract from onboard logging

Investigation 04 must deliver or agree on:

- a unique survey/mission identifier before capture;
- one monotonic capture clock plus UTC relationship where available;
- raw LiDAR, IMU, RGB, pose/telemetry, and autopilot-log paths;
- graceful-close marker and incomplete-close detection;
- byte counts and SHA-256 values computed during or immediately after offload;
- sensor serial/model/firmware and full configuration snapshot;
- dropped-message/frame counters and device-status evidence;
- start/end times and time-base definitions; and
- safe-offload behavior that never deletes the onboard source merely because a copy command returned success.

The reporting layer must accept incomplete packages and expose missing evidence. It must not invent empty files, interpolate silently, or mark an ingest complete because a directory exists.

### 4.3 Coordinate and time contract

Each sample or artifact that contains geometry must identify:

- coordinate frame ID;
- axis direction and handedness;
- length and angle units;
- parent frame and transform version;
- timestamp field, unit, epoch, and clock domain; and
- interpolation method used to associate pose with a LiDAR beam/profile or RGB exposure.

The canonical local engineering frame should be right-handed and expressed in meters, but the exact origin and orientation must be selected centrally with investigations 03, 05, and 06. WGS 84 latitude/longitude is an optional publication coordinate. It does not replace the local metric frame used for deformation dimensions.

### 4.4 Baseline selection rules

A baseline candidate is eligible only when:

1. it belongs to the same site and overlapping survey area;
2. it is accepted rather than quarantined or rejected;
3. its coordinate-frame relationship is known;
4. required modalities are present for the requested comparison;
5. calibration and configuration differences are understood by the processing version; and
6. blocking integrity flags are absent.

The interface may recommend an eligible baseline by date, but the operator must confirm it. The selected baseline ID, reason, selection time, and selector identity are saved. Every processing run freezes this selection. Reassigning the site's preferred baseline never changes an existing run.

### 4.5 Processing output contract

Investigation 06 should emit:

- current and baseline survey IDs;
- exact input artifact/sample IDs;
- registered transforms and residual/coverage metrics;
- algorithm and model names/versions;
- code revision and environment lock or container digest;
- complete parameters and random seed where applicable;
- anomaly geometry in the local frame;
- change magnitude, dimensions, units, sign convention, and uncertainty when supported;
- score plus a precise definition of what that score means;
- links to current/baseline RGB and range evidence;
- metrics and all quality flags; and
- run start/end, resource use, and success/failure status.

The reporting layer should reject an anomaly record that says <code>rgb_plus_geometry</code> but has no range/depth evidence link, or downgrade it with a blocking flag rather than silently relabeling it.

### 4.6 Export contract

| Export | Contents | Conditions |
|---|---|---|
| HTML | Complete human-readable report with bundled plots/evidence thumbnails | Canonical presentation for the MVP; works with networking disabled. |
| PDF | Frozen printable report | Generated from the HTML; records generator/browser version and report hash. |
| CSV | One row per candidate with flattened summary fields | Includes IDs, units, frame ID, flags, and review state. Geometry beyond centroid uses a separate field or file. |
| JSON | Full report summary and provenance links | Validated against a versioned JSON Schema. |
| GeoJSON | WGS 84 anomaly geometries and selected properties | Generated only when a validated local-to-world transform exists. Longitude precedes latitude. |
| Local Parquet/JSON | Full local-frame geometry and numeric evidence | Always preferred for engineering measurements and reproducibility. |

Exports are snapshots. Each carries <code>exported_utc</code>, report/run ID, schema version, generator version, and SHA-256. A later review produces a new export rather than altering a previously released package in place.

### 4.7 Access control, retention, and recovery

#### MVP access control

- Store the working catalog and survey roots on an MSU-managed or team-controlled encrypted workstation when available.
- Use operating-system accounts and directory permissions for the MVP.
- Bind any local dashboard server to loopback by default; do not expose it to the campus network merely for convenience.
- Separate “viewer” export access from “reviewer” write access in the application, even if both initially map to a small team.
- Keep credentials, network addresses, private site notes, and student personal data out of public reports.
- Record review identity and time, but do not claim a tamper-proof audit trail without an authenticated multi-user system.

If a future cloud or multi-user system is adopted, it needs authenticated users, role-based authorization, transport encryption, managed backups, and an institution-approved privacy/security review. That is outside the MVP.

#### Retention classes

| Class | Treatment |
|---|---|
| Raw evidence and acquisition manifests | Retain while any released report or research result depends on them. Never delete automatically from the UI. |
| Calibration/configuration and code/environment records | Retain with every dependent run. |
| Released reports and review events | Retain as versioned records; supersede, do not overwrite. |
| Reproducible caches and thumbnails | May be regenerated and pruned after storage pressure is documented. |
| Failed temporary files | May be removed after their failure log and needed diagnostic evidence are preserved. |
| Public dataset copies | May be re-downloaded only if version, license, checksum, and source remain available; manifests remain. |

The exact time period is an open policy decision for the team, MSU, and any future site owner. The MVP should implement retention **classes**, not invent a legal duration. Material deletion must be an explicit administrative operation that records the target IDs, reason, operator, time, and whether another verified copy exists.

#### Backup and recovery

- Make catalog backups through SQLite's backup mechanism or from a cleanly closed/checkpointed database.[3]
- Back up manifests, schemas, raw evidence, calibrations, review records, and released reports together.
- Maintain at least one disconnected or separately controlled copy during the capstone demonstration period.
- Test restoration; a backup that has never been opened and verified is not sufficient evidence of recoverability.
- Rebuilding the catalog from survey manifests is a required fallback. Review events and baseline selections therefore also need exportable append-only records.

## 5. Development sequence and dependencies

### Phase 1 — Freeze identifiers and contracts

1. Agree on site, survey, flight, configuration, calibration, run, artifact, anomaly, quality-flag, and review identifiers.
2. Approve time, coordinate-frame, unit, missing-value, and evidence-label conventions.
3. Write JSON Schemas for survey, run, anomaly, quality flag, and report summary.
4. Write the first SQLite migration and enable/test foreign keys.
5. Define the authoritative artifact roles and controlled enumerations.

This phase should precede dashboard work. Otherwise the interface will encode unstable assumptions into forms and filenames.

### Phase 2 — Synthetic ingest and catalog

1. Ingest the deterministic baseline/current fixture proposed by investigation 07.
2. Validate manifests and compute artifact hashes.
3. Populate the catalog without copying large blobs into SQLite.
4. Deliberately omit a modality, corrupt a checksum, and invalidate a schema to exercise quarantine and flags.
5. Prove the catalog can be rebuilt from manifests.

### Phase 3 — Static report first

1. Generate the survey summary, anomaly list/map, and one anomaly-detail page.
2. Bundle plots and thumbnails for offline use.
3. Add the exact mandatory public/synthetic pre-hardware statement defined in Section 3.6 to every applicable page and figure.
4. Export JSON, CSV, local-frame data, and WGS 84 GeoJSON only when eligible.
5. Print the HTML to PDF and store its export metadata and hash.

The static report is the low-cost fallback and should be completed before an interactive dashboard.

### Phase 4 — Review interface

1. Add survey/baseline selection with compatibility checks.
2. Add filters and map/list synchronization.
3. Add anomaly detail with current/baseline RGB and LiDAR/range evidence.
4. Add append-only review events and field-verification state.
5. Regenerate a signed-off report snapshot after review.

“Signed-off” here means an identified reviewer approved the report content for demonstration. It is not a professional engineering seal or pavement-safety certification.

### Phase 5 — Hardware substitution

Replace synthetic adapters one source at a time:

1. real picoScan150 stationary/bench stream;
2. real camera and timestamped pose stream;
3. controlled ground or tethered acquisition;
4. supervised repeat UAV survey; and
5. controlled field truth and repeatability results.

The record and report schemas should remain stable while evidence labels change from simulated to measured. New hardware-specific fields may be added through versioned extensions.

### Required cross-investigation decisions

| Owner | Needed decision/interface | Why item 8 cannot decide it alone |
|---|---|---|
| 02 — picoScan150 acquisition | Raw packet/replay format, sensor timestamp semantics, device/config/diagnostic fields, invalid-return representation, real data rate | Determines what raw evidence and configuration must be retained. |
| 03 — RGB/position/synchronization | Camera encoding, frame timestamps, intrinsics/distortion, extrinsics, pose clock, frame tree, time-alignment uncertainty | Determines whether image, pose, and range evidence can be compared and traced. |
| 04 — onboard compute/logging | Mission package, atomic close, dropped-data counters, checksum/offload process, storage media, recovery behavior | Owns the raw handoff and incomplete-survey detection. |
| 05 — mission planning | Site/route IDs, planned versus flown track, altitude/speed/heading, area/segment identifiers, repeat-survey tolerance | Enables compatible baseline selection and map context. |
| 06 — processing/fusion | Canonical anomaly types, score definition, registration metrics, uncertainty, threshold policy, output contract | Prevents the report from assigning unsupported confidence or severity. |
| 07 — demonstration data | Fixture IDs, source manifests, normalized sample IDs, public-data license/citation, mandatory pre-hardware text | Provides the first reproducible inputs for this workflow. |
| Central team | Local-first wording versus cloud promise, retention period, authorized reviewers, site privacy, report release authority | These are project governance decisions, not implementation details. |

The current application statement says data will be offloaded to cloud servers, while the technical brief says an existing laptop can perform post-flight processing without a cloud subscription. For the MVP, change the architecture language during final integration to **“offloaded after flight for local processing, with optional cloud synchronization later.”** This finding does not edit the application text.

## 6. Verification tests and success measures

### 6.1 Provenance and integrity

| Test | Method | Pass condition |
|---|---|---|
| Complete trace | Select an exported anomaly and traverse anomaly → run → surveys → artifacts/config/calibration → hashes | Every required link resolves without using an absolute workstation path. |
| Artifact tamper | Change one byte in a copied input | Verification reports a checksum mismatch and blocks use of that copy. |
| Schema rejection | Remove a required survey field or use an invalid enumeration | Ingest quarantines the record and produces a structured validation error. |
| Foreign-key enforcement | Attempt to insert an anomaly for a nonexistent run | Transaction fails; startup test confirms foreign keys are on. |
| Immutable run | Change a parameter after a successful run | System requires a new run ID and preserves the first run. |
| Catalog rebuild | Restore a blank catalog and ingest saved manifests/review ledger | Surveys, artifacts, runs, flags, baselines, and reviews are reconstructed with the same stable IDs. |

### 6.2 Baseline selection

- A survey from another site is rejected.
- A survey with no overlapping local-frame area is rejected or clearly marked ineligible.
- A baseline missing the modality required by a requested comparison is rejected for that branch.
- Calibration/configuration incompatibility produces a blocking flag unless the selected processing version explicitly supports the difference.
- The UI requires confirmation and records who chose the baseline and why.
- Changing the preferred baseline does not change an already completed run or report.
- Reversing current and baseline reverses the expected sign in a controlled synthetic fixture or is rejected if the algorithm does not support reversal.

### 6.3 Missing data and quality propagation

- Removing one RGB frame creates a localized completeness result; it does not fabricate a blank image.
- Removing range data prevents an RGB result from being labeled image-plus-LiDAR.
- Removing calibration prevents calibrated dimensions/change magnitude while still allowing explicitly qualitative evidence if appropriate.
- A high registration residual propagates from run to affected candidates and report summary.
- A blocking flag prevents release unless an authorized override record states the reason; the original flag remains visible.
- “Unknown” values export as null/blank with a reason, never as zero.
- A report summary count includes candidates hidden by a current filter so filters cannot make the total misleading.

### 6.4 Reproducibility

For the deterministic synthetic fixture:

1. save input hashes, code revision, environment, parameter hash, and seed;
2. run twice on the same supported platform;
3. require identical record IDs, anomaly count/classification, baseline/current associations, and quality flags;
4. compare numeric outputs using declared tolerances where floating-point/library differences prevent bit-for-bit identity; and
5. record any non-deterministic model setting rather than claiming exact reproducibility.

A clean laptop should be able to regenerate the HTML report from documented inputs without network access. Reproducing an old run must create a new execution record that points to the earlier run; it does not overwrite history.

### 6.5 Spatial and export correctness

- Local coordinate values include frame ID and meters.
- A GeoJSON export is suppressed when world georeferencing is missing or invalid.
- A known test point confirms GeoJSON longitude/latitude order and transformation direction.
- CSV and JSON exports preserve sign, unit, evidence label, quality flags, and stable IDs.
- Opening the HTML with networking disabled shows all required text, plots, and thumbnails.
- Report links remain valid after moving the packaged report directory.
- JSON validates against the declared schema version.
- Importing the export into a second parser reproduces candidate counts and identifiers.
- The PDF shows the same report/run ID, evidence label, limitations, and candidate totals as the HTML.

### 6.6 Review and safety-language tests

- A reviewer can retain, dismiss, or request more data without changing the algorithm result.
- Field verification is recorded separately from desktop review.
- The review history shows all events in UTC and does not allow silent deletion through the normal UI.
- Every page containing an anomaly states that it is a candidate for human review.
- The UI does not display “safe,” “unsafe,” “compliant,” “failed,” or “repair required” unless a later validated policy and authorized professional review explicitly justify such language.
- Image-only crack-like features never display a LiDAR-derived depth unless a linked geometric method actually produced and validated that value.

### 6.7 Backup and failure recovery

- Restore a catalog backup and verify all foreign keys and report IDs.
- Simulate power loss during an ingest; restart leaves either the prior accepted state or a clearly incomplete transaction, not a partially accepted survey.
- Copy a database using the supported backup procedure while the application is active and verify the copy opens cleanly.
- Remove a derived cache and regenerate it from raw evidence and the run record.
- Demonstrate that an unavailable cloud/network connection does not prevent ingest, review, or report generation.

### MVP completion criteria

Item 8 is implemented successfully when the team can demonstrate, on a normal laptop and with networking disabled:

1. ingest of a schema-valid synthetic baseline and current survey;
2. integrity verification and cataloging;
3. explicit baseline selection;
4. display of a candidate with current/baseline evidence and inherited quality flags;
5. an append-only human review event;
6. HTML, PDF, JSON, CSV, and eligible/ineligible spatial export behavior;
7. end-to-end tracing from one report value to source artifact and processing parameters; and
8. regeneration of the report from saved inputs.

These are workflow success criteria, not field-accuracy claims.

## 7. Cost, mass, power, or resource implications

### Hardware and software cost

The reporting subsystem adds no UAV mass or flight power. It requires no new onboard hardware beyond storage already owned by acquisition. The MVP can use an existing laptop, Python, SQLite, JSON, and open file formats at **$0 new software-license cost**. An external drive is useful for backup if the team or department does not already have one, but this investigation does not authorize a purchase.

Cloud compute, hosted databases, commercial dashboards, and paid map tiles are unnecessary for the competition demonstration.

### Storage planning

Investigations 02–04 must measure actual byte rates. Until then, use this auditable equation rather than presenting an unsupported sensor-specific number:

```text
raw bytes per survey = duration_seconds ×
  (lidar_bytes_per_second
   + imu_bytes_per_second
   + rgb_frames_per_second × mean_encoded_rgb_bytes
   + pose_and_flightlog_bytes_per_second)

working storage = raw bytes × (1 + derived_fraction + temporary_fraction)
retained storage = raw + accepted derived outputs + reports + backup copies
```

For a **planning example only**, a 15-minute synthetic workload with 2 compressed RGB frames/s at 1.5 MB/frame, a 2 MB/s placeholder for all other streams, and derived/temporary files equal to the raw size requires about:

- RGB: 2.7 GB;
- other placeholder streams: 1.8 GB;
- raw total: 4.5 GB;
- raw plus one working-size equivalent: about 9 GB; and
- baseline plus current working sets: about 18 GB before backups.

These are workload assumptions, not measured picoScan150 or camera rates. Replace them with bench measurements. Investigation 07 separately recommends 15–25 GB of free disk for its public/synthetic data demonstration; the hardware survey store is additional.

Recommended storage controls:

- record bytes per stream and per survey automatically;
- warn before processing if free space is below a configurable multiple of input size;
- generate thumbnails rather than duplicating full images in every report;
- make derived caches safely removable and reproducible;
- keep public datasets and field evidence outside Git; and
- never compress or transcode the only raw copy without preserving its provenance and verifying the replacement.

### Compute planning

Reporting itself is modest compared with registration, reconstruction, and model inference:

| Task | MVP resource expectation |
|---|---|
| Catalog/filter/review | Normal laptop CPU and less than a few hundred MB for typical summary tables; verify with actual data. |
| Hashing | Streaming I/O; runtime proportional to total bytes. Does not require loading files into memory. |
| Report generation | CPU-only; use thumbnails and incremental table reads. |
| Parquet export | CPU-only, chunked; memory depends on selected row-group/chunk size. |
| Processing/fusion | Owned by investigation 06; GPU remains optional unless measured workloads justify it. |

Do not load all RGB images or point samples into the dashboard process. Query summaries from SQLite and load one selected evidence item or downsampled tile at a time.

### Implementation-effort estimate

This is a planning range for students familiar with Python, not a contract:

| Work package | Estimated focused effort |
|---|---:|
| IDs, JSON Schemas, SQLite migrations, controlled values | 3–5 person-days |
| Ingest, hash inventory, validation, quarantine | 3–6 person-days |
| Static HTML/JSON/CSV/spatial exports | 4–7 person-days |
| Three-view local review interface | 5–9 person-days |
| Tests, restore, documentation, integration fixes | 4–7 person-days |
| **Total** | **19–34 person-days** |

Parallel work is possible only after the data contracts are frozen. A realistic fallback is the static report and exports without an interactive write-capable dashboard; that cuts scope while preserving the competition narrative.

## 8. Risks, open decisions, and fallback

### Risks and mitigations

| Risk | Consequence | Mitigation |
|---|---|---|
| Dashboard is built before contracts stabilize | Rework and inconsistent records | Complete phases 1–3 before interactive UI work. |
| SQLite database is treated as the only copy | Single-file loss destroys review history | Keep rebuildable manifests/review ledger and tested backups. |
| Live SQLite file is copied incorrectly | Lost or inconsistent committed data | Use documented backup/close/checkpoint procedure.[3] |
| Raw files are renamed or moved manually | Broken provenance | Relative manifest paths, immutable ingest root, and hash verification. |
| Local XY is exported as GeoJSON | Incorrect real-world placement | Suppress GeoJSON without valid WGS 84 transformation; keep local-frame export. |
| “Confidence” hides poor data quality | Misleading report | Display model score, uncertainty, and quality flags separately. |
| Image-only detection is presented as LiDAR measurement | Overstates picoScan150 contribution | Store detection channel and require modality-specific evidence links. |
| Simulated results appear measured | Misleads reviewers | Persistent evidence banner in UI, plots, report, and exports. |
| Map tiles or web assets require internet | Demo fails offline or leaks site queries | Bundle assets and use local imagery/site diagrams. |
| Storage fills during processing | Incomplete run or lost evidence | Preflight capacity check, chunked processing, cache policy, and byte-rate measurement. |
| Review events are overwritten | No defensible history | Append-only review rows and versioned report snapshots. |
| Export omits quality limitations | Detached spreadsheet becomes misleading | Repeat evidence label, flags, units, frame, and limitations in every export. |
| Site imagery contains people, plates, or sensitive layout | Privacy and release risk | Controlled capture, review/redaction workflow, restricted raw access, sanitized report. |
| Thresholds imply safety or compliance | Unsupported decision-making claim | Call outputs candidate changes and review priorities; require field verification. |

### Open decisions

1. What is the canonical site-local coordinate frame and how is it recreated on a later survey?
2. Which picoScan150 raw and configuration format is authoritative: original datagrams, a ROS bag, or both?
3. What timestamp from each device denotes measurement time rather than receive/write time?
4. What configuration or calibration differences make a baseline incompatible?
5. What registration/coverage values create warning versus blocking flags?
6. How is algorithm confidence calibrated and what statement may the UI attach to it?
7. Which team members may release a report or override a blocking flag?
8. What retention duration does MSU or a future site owner require?
9. Is any site data restricted, and what must be removed from the application attachment?
10. Will the final application promise local post-flight processing with optional cloud sync, replacing the current cloud-only wording?

These should remain explicit until the responsible investigation or team approves them.

### Low-cost fallbacks

1. **No interactive dashboard:** generate a self-contained HTML report, CSV/JSON, and local-coordinate plot. This still demonstrates ingest-to-report traceability.
2. **No reliable world georeference:** show a labeled site image or local metric plan with fiducials. Do not publish GeoJSON or a misleading online map pin.
3. **No RGB evidence:** report geometric candidates with an <code>RGB_EVIDENCE_UNAVAILABLE</code> flag and no visual-class claim.
4. **No usable range evidence:** report RGB-only crack-like observations and explicitly remove LiDAR-supported language from those records.
5. **Processing fails:** publish a data-quality and run-failure report rather than a fabricated empty “no anomalies” result.
6. **Catalog corruption:** restore the verified backup or rebuild from manifests and the exported review ledger.
7. **PDF generation differs across computers:** treat HTML and machine-readable exports as canonical; record the PDF generator version.
8. **Cloud unavailable:** continue entirely offline and transfer a read-only report package through approved local storage.
9. **Public dataset unavailable:** use the deterministic synthetic fixture from investigation 07; retain the pre-hardware disclaimer.

### Illustrative MVP report

The following is the proposed content, not a measured result:

```text
PAVEWATCH — ILLUSTRATIVE PRE-HARDWARE REPORT
Pre-hardware software demonstration using public and/or synthetic data.
Not a field validation of PaveWatch or the SICK picoScan150.
This report is not a safety certification.

Site: Synthetic Walkway 01
Current survey: sur_demo_current_20260915 (simulated)
Baseline: sur_demo_baseline_20260901 (simulated)
Run: run_demo_change_20260919_001
World georeference: unavailable — local meter frame shown

+---------------------------------------+---------------------------+
| LOCAL CHANGE MAP                      | CANDIDATES                |
|                                       |                           |
| baseline/current path                 | 1. Settlement candidate  |
| stable control area                   |    change: -28 mm         |
| [selected candidate at E 8.2, N 1.4]  |    size: 1.1 m × 0.7 m   |
|                                       |    priority: elevated     |
|                                       |    field check: requested |
+---------------------------------------+---------------------------+

Selected candidate
- Detection channel: geometry
- Current versus baseline profile: [plot]
- RGB context: [synthetic texture or “not available”]
- Confidence: not calibrated
- Quality flags: pre-hardware synthetic input; no world georeference
- Review statement: Candidate synthetic surface change for workflow testing.

Trace this result
anomaly -> processing run -> current/baseline samples -> configuration/
calibration -> source artifacts and hashes

Required limitation
This output identifies a candidate for human review. It does not determine pavement
safety, accessibility compliance, or the need for repair.
```

The competition demonstration should let a reviewer select this candidate, compare current and baseline evidence, inspect why the LiDAR/range channel mattered, see limitations without opening a developer log, and trace the value back to its source record in no more than two interactions.

## 9. Sources

External sources were accessed **2026-09-19**.

1. SICK AG, **picoScan150 2D LiDAR Sensors — Operating Instructions**, document 8028323/1THA/2025-09-03. Sensor configuration, interfaces, diagnostics, scan/IMU output, and telegram reference: https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf
2. SQLite, **Foreign Key Support** and **Transactions**. Foreign-key activation/constraints and transaction behavior: https://www.sqlite.org/foreignkeys.html and https://www.sqlite.org/lang_transaction.html
3. SQLite, **Write-Ahead Logging** and **SQLite Backup API**. WAL state, checkpoint/copy cautions, and consistent backup methods: https://www.sqlite.org/wal.html and https://www.sqlite.org/backup.html
4. IETF, **RFC 7946: The GeoJSON Format**, August 2016. Geometry, properties, and WGS 84 longitude/latitude coordinate requirements: https://www.rfc-editor.org/rfc/rfc7946
5. JSON Schema, **Draft 2020-12 Specification**. Versioned structural validation of JSON records: https://json-schema.org/draft/2020-12
6. Apache Parquet, **Documentation: File Format Metadata and Concepts**. Typed columnar organization and file metadata: https://parquet.apache.org/docs/file-format/metadata/ and https://parquet.apache.org/docs/concepts/
7. W3C, **PROV-DM: The PROV Data Model**, W3C Recommendation, 30 April 2013. Entity, activity, agent, and derivation concepts: https://www.w3.org/TR/prov-dm/
8. National Institute of Standards and Technology, **FIPS PUB 180-4: Secure Hash Standard**, August 2015. SHA-256 and digest-based change detection: https://doi.org/10.6028/NIST.FIPS.180-4
9. Local project reference, **PaveWatch dataset and pipeline demonstration**, survey-folder, normalized sample, provenance, quality, and report interfaces: <code>../07-datasets-pipeline-demonstration/findings.md</code>
10. Local project reference, **PaveWatch Technical Architecture and Validation Plan**, reporting fields, local storage, laptop processing, and no-cloud MVP assumption: <code>../../drafts/02_PaveWatch_Technical_Validation_Plan.md</code>
11. Local project reference, **PaveWatch Visual Prototype Appendix**, conceptual map/dashboard elements and required illustrative labeling: <code>../../drafts/04_PaveWatch_Visual_Prototype_Appendix.md</code>
