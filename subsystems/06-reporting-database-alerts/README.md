# RD — Reporting, Database & Alerts

Lead: **Saugat Karki**. Charter support: **Pritam Adhikari**. Requirements: **RD1; S2–S5**.

Updated November 16, 2026. **Status: hosted web portal, PostgreSQL/PostGIS, cloud evidence files, and PDF export selected in SRC-034 §3.3.6; provider/schema/resources and implementation pending.**

## Required function

Give reviewers inspectable survey findings with images, supported geometry/units and location, while distinguishing no detected defects from insufficient coverage or invalid references.

## Selected approach and alternatives

A logged-in user browses a hosted dashboard with map markers, defect counts/types, date/type/warning filters, and finding details with images, measurements and scan evidence. Compare earlier surveys when valid comparable coverage exists; a previous survey is unnecessary for current-survey review. Export a PDF with counts, map, findings/photos/measurements, and warnings.

**PostgreSQL with PostGIS** stores linked surveys/findings and geographic search data; cloud file storage holds supporting imagery/scans. The ingestion API validates input and rejects invalid files with actionable errors for correction/resubmission. Findings include stable IDs, defect type, location, measurements/units, producing software version, quality warnings, and evidence links. Define repeat-upload identity and backup/retention rules.

Source alternatives are a **local web app with SQLite** for field/offline fallback and portable PDF/HTML output. GeoJSON-only storage and MongoDB were considered; the final approach chooses relational links and geospatial queries in PostgreSQL/PostGIS. No provider, paid plan, notification service, or operating-cost total is selected. Hosted **reporting** does not decide whether PC processing runs locally or in the cloud.

## Coordinates, warnings, and resources

The source describes local positions from the launch point plus best-effort GPS, while requesting RFC 7946 GeoJSON. IF-16/Q-20 must resolve the precise schema: geographic geometry uses **WGS84 longitude/latitude**; local metric XYZ belong in declared properties or a separate local product. Do not place meter offsets in geographic geometry. Without supported registration, preserve local results with unset/flagged geographic geometry and an appropriate local view. Map appearance is not accuracy evidence.

Retain unscanned regions, invalid/missing pose, timing/alignment uncertainty, missing geometry, interrupted-run status, and partial coverage through ingestion, dashboard and PDF. Image-only findings remain reviewable; absent geometry never implies zero defect depth. Preserve evidence provenance if optional learned depth is used.

Inventory one actual shared operator/processor/reviewer workstation where possible, internet access, upload/backup storage, cloud database/files, authentication/TLS configuration, and recurring costs. Local acquisition/export must remain usable before upload. Verify rejection/retry, stale/invalid references, evidence links/units, filters, map/local coordinates, PDF warnings, and optional comparison. Historical leads: SRC-006/007/027/029.

## Shared design records

Maintain one owning row per component in [the BOM](../../procurement/bom.csv), exact connections in [interfaces](../../integration/interfaces.csv), and affected [power](../../integration/power-budget.csv), [mass/fit](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), [verification](../../verification/plan.md), and [decisions](../../decisions/decision-log.md). Design selection is not purchase authorization or test evidence. Blank installed/price values remain unknown.

Current source: [SRC-034 final approach](../../references/new-evidence/2026-11-16-final-approach/PaveWatch_Approach_Final.docx), [readable text SRC-035](../../references/new-evidence/2026-11-16-final-approach/approach-text.txt), and [reconciliation](../../references/new-evidence/2026-11-16-final-approach.md). Earlier source IDs resolve through [the source index](../../references/source-index.md).
