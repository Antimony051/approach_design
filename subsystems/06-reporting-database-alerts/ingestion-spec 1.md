# PaveWatch portal: data ingestion spec (v1.0)

This is for whoever sends processed survey results to the PaveWatch portal, normally the post-flight processing pipeline (`ReportExporter`). It explains what to send, how to send it, and what the portal checks.

**In this folder / repo**

| File | What it is |
|---|---|
| `docs/run-submission.schema.json` | Machine-readable JSON Schema (draft 2020-12) of the payload |
| `samples/sample_run/` | A complete, valid example: `payload.geojson` plus its evidence images |
| `tools/uploader/pavewatch_upload.py` | Single-file Python uploader (standard library only) that does all three steps for you |
| `http://<portal>/docs` | Interactive API docs (try requests from the browser) |

---

## 1. The short version

One survey run = one upload, in three steps:

```
1. POST /api/v1/ingest/runs              GeoJSON payload (run + findings)  -> validated, returns files to upload
2. PUT  /api/v1/ingest/{id}/files/{file} raw bytes of each evidence file   -> checked and stored
3. POST /api/v1/ingest/{id}/complete                                       -> run becomes visible in the portal
```

Nothing appears in the portal until step 3 succeeds, so a failed or half-finished upload never shows up as a half-finished survey. If the payload is invalid, step 1 returns **all** problems at once, each with the exact path to the bad field. Fix them and resend.

### Easiest: use the uploader

```bash
python pavewatch_upload.py path/to/payload.geojson --files path/to/evidence_dir --url http://localhost:8000
```

or from Python:

```python
from pavewatch_upload import upload_run, IngestError

try:
    result = upload_run("http://localhost:8000", "out/payload.geojson", "out/", api_key=None, replace=False)
    print(result["portal_path"])          # e.g. /orgs/northgate-roads/runs/PW-20261114-1502-A1
except IngestError as e:
    print(e.pretty())                      # readable list of every problem
```

It retries network errors and server errors (5xx), and does not retry validation errors (4xx).

---

## 2. Payload format

A GeoJSON `FeatureCollection` ([RFC 7946](https://www.rfc-editor.org/rfc/rfc7946)) with two extra top-level members: `schema_version` and `run`. Each finding is a `Feature`.

```json
{
  "type": "FeatureCollection",
  "schema_version": "1.0",
  "run": { ...survey run... },
  "features": [ { "type": "Feature", "geometry": {...}, "properties": { ...finding... } } ]
}
```

`features` may be an empty array: a complete run with no findings is valid and is shown as "no defects detected".

### General rules

- **Coordinates are `[longitude, latitude]`** (GeoJSON order), WGS 84 decimal degrees. A third value (altitude, m) is optional.
- **Timestamps** are ISO 8601 **with a timezone**, e.g. `2026-11-14T15:02:00-05:00` or `...Z`. Timestamps without a timezone are rejected.
- **Unknown fields are rejected** inside `run`, `properties`, `evidence` and the other PaveWatch objects. This catches typos (`severty`) early. Standard GeoJSON members on the outer objects (`bbox`, `id`) are allowed.
- **Units** are explicit on every measurement. Positions and distances are in metres.

### 2.1 `run`: the survey run

| Field | Type | Required | Notes |
|---|---|---|---|
| `run_id` | string | yes | **Globally unique.** Letters, digits, `.` `_` `-`; max 100. Suggested: `PW-YYYYMMDD-HHMM-<aircraft>` |
| `company.company_id` | string | yes | Stable customer id: lowercase letters, digits, `-`; 3–64 chars, e.g. `northgate-roads`. New ids create a new company in the portal |
| `company.name` | string | yes | Display name. Sending a new name renames the company |
| `site_name` | string | yes | e.g. `Lot C` |
| `started_at` | datetime | yes | |
| `ended_at` | datetime | no | Must not be before `started_at` |
| `status` | `complete` \| `incomplete` | yes | `incomplete` if the flight or processing did not cover the planned area |
| `software_version` | string | yes | e.g. `pw-proc 0.3.1` |
| `aircraft_id` | string | no | e.g. `PW-01` |
| `operator` | string | no | |
| `local_frame_origin` | object | no* | `{lat, lon, alt_m?, heading_deg?}`. Where the local x/y frame starts (see 2.4). *Needed so findings without GPS can be placed on the map |
| `flight_path` | GeoJSON `LineString` | no | Drawn on the survey map. ≥ 2 positions |
| `data_warnings` | array | no | Run-level data-quality warnings, see 2.5 |

### 2.2 Finding: `Feature.properties`

| Field | Type | Required | Notes |
|---|---|---|---|
| `finding_id` | string | yes | Unique **within the run**, e.g. `F-0001`. Same character rules as `run_id`. The portal lists findings sorted by this id |
| `detected_at` | datetime | yes | |
| `defect_type` | enum | yes | `pothole`, `crack`, `depression`, `raised_area`, `vertical_step`, `other` |
| `subtype` | string | no | e.g. `alligator`, `longitudinal`, `transverse`, `block`, `debris` |
| `description` | string | no | Plain-language sentence shown on the finding page |
| `severity` | `low` \| `medium` \| `high` | no | Omit if not rated |
| `confidence` | number 0–1 | no | Detection confidence |
| `detection_source` | `image` \| `lidar` \| `fused` | no | |
| `gps_accuracy_m` | number ≥ 0 | no | Horizontal error estimate; drawn as a circle on the map |
| `position_local_m` | `{x, y, z?}` | see below | Metres from the start point (see 2.4) |
| `measurements` | object | no | See 2.3 |
| `quality_warnings` | array | no | `[{code, message?}]`, see 2.5 |
| `evidence` | array | **yes, ≥ 1** | See 2.6 |

**Position:** `geometry` is a GeoJSON `Point` with the best-effort GPS position, or `null` when there was no GPS fix. A finding must have **a `geometry`, a `position_local_m`, or both.** Please send `position_local_m` whenever you have it.

### 2.3 Measurements

A map of name to `{value, unit}`. Names: lowercase letters, digits and `_`.

```json
"measurements": {
  "width":  {"value": 0.42, "unit": "m"},
  "length": {"value": 0.51, "unit": "m"},
  "depth":  {"value": 0.062, "unit": "m"},
  "area":   {"value": 0.17, "unit": "m2"}
}
```

Any name and unit is accepted. The portal labels these well-known names nicely and uses them in list summaries: `width`, `length`, `depth`, `height`, `max_width`, `area`, `volume`. `m2` and `m3` are displayed as m² and m³.

### 2.4 Local frame

`position_local_m` is measured from `run.local_frame_origin`:

- **x** points along `heading_deg` (0 = north, clockwise)
- **y** points 90° clockwise from x (to the right, as in PX4's forward-right-down frame)
- metres

The portal converts it to map coordinates for findings that have no GPS fix and marks those positions as approximate.

### 2.5 Warning codes

Warnings let users tell **"no defects found"** apart from **"not enough data to know"**. Codes are UPPER_SNAKE_CASE. Any code is accepted, but these have friendly text and icons in the portal:

| Code | Use for | Where |
|---|---|---|
| `NOT_SCANNED` | Area inside the site that was not surveyed (blocked, aborted flight) | `run.data_warnings` (with a Polygon) |
| `NO_LIDAR_COVERAGE` | LiDAR returns missing; image-only detection | run (area) or finding |
| `POSE_LOW_CONFIDENCE` | Poor position/attitude estimate | run or finding |
| `SCAN_IMAGE_MISALIGNED` | LiDAR and camera not well synchronised | run or finding |
| `GPS_UNAVAILABLE` | No GPS fix for this finding | finding |

Run-level warnings may carry a `geometry` (Point, LineString, Polygon or Multi* variants, in lon/lat). Polygons are drawn as hatched areas on the survey map.

```json
"data_warnings": [
  {"code": "NOT_SCANNED", "message": "Area blocked by parked vehicles",
   "geometry": {"type": "Polygon", "coordinates": [[[-79.4110, 43.7615], [-79.4109, 43.7615], [-79.4109, 43.7616], [-79.4110, 43.7615]]]}}
]
```

### 2.6 Evidence

Each finding lists one or more evidence files. **Order matters:** the first image is shown first.

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | string | yes | Plain file name, no folders. Letters, digits, `.` `_` `-`. **Unique across the whole run**, so prefix with the finding id (`F-0001_raw.jpg`) |
| `kind` | string | yes | `image_raw`, `image_closeup`, `lidar_profile`, `lidar_scan`, or your own lowercase name |
| `caption` | string | no | |
| `captured_at` | datetime | no | |
| `width_px`, `height_px` | integer | no, recommended for images | Original pixel size. **Checked against the uploaded image** |
| `bounding_boxes` | array | no | Images only, see below |

The portal uses an `image_closeup` (if present) as the finding's thumbnail in lists.

**Bounding boxes**

```json
"bounding_boxes": [{"label": "pothole", "bbox": [410, 220, 780, 510], "confidence": 0.91}]
```

- `bbox` = `[x_min, y_min, x_max, y_max]` in **pixels of the original image you upload**, origin top-left, x to the right, y down.
- Boxes must lie inside the image (`x_max ≤ width`, `y_max ≤ height`) and have positive size.
- **Do not burn boxes into the image.** The portal draws them as an overlay that users can switch off.
- Images are displayed exactly as stored, without EXIF rotation. Make sure pixel orientation matches the boxes.

**Files**

- Images (`.jpg`, `.png`, `.webp`, `.bmp`, `.tif`) get thumbnails and previews automatically.
- Other files (e.g. `.ply`, `.las` 3D scans, `.csv`) are stored and offered as downloads. They cannot have bounding boxes.
- Max **50 MB per file** (server setting `PW_MAX_UPLOAD_MB`).

---

## 3. API reference

Base URL: `http://<host>:8000`. If the portal is configured with an ingestion key, every ingestion request needs the header `X-API-Key: <key>`. With no key configured (the local default), no header is needed.

### Step 1: submit the run

```
POST /api/v1/ingest/runs[?replace=true]
Content-Type: application/json
```

`201 Created`

```json
{
  "ingestion_id": "6b0c…",
  "run_id": "PW-20261114-1502-A1",
  "status": "pending_files",
  "files_expected": ["F-0001_raw.jpg", "F-0001_closeup.jpg", "…"],
  "upload_url_template": "/api/v1/ingest/6b0c…/files/{file}",
  "complete_url": "/api/v1/ingest/6b0c…/complete"
}
```

- **`replace=true`** overwrites an existing run with the same `run_id` (e.g. after re-processing). The old run stays visible until the new one completes. Without it, a duplicate `run_id` gets `409`.
- A `run_id` that belongs to a **different company** is always refused (`409`).

### Step 2: upload each file

```
PUT /api/v1/ingest/{ingestion_id}/files/{file}
Content-Type: image/jpeg            (or the file's type; guessed from the extension if omitted)
<raw bytes>
```

`200 OK` returns `{file, size_bytes, content_type, width_px, height_px, files_remaining: [...]}`.

- Only files listed in `files_expected` are accepted (`404` otherwise).
- Uploading the same file again replaces it, so retries are safe.
- Images are opened and checked: unreadable image → `422`; size differs from `width_px`/`height_px` → `422`; a box outside the image → `422`.

### Step 3: complete

```
POST /api/v1/ingest/{ingestion_id}/complete
```

`200 OK`

```json
{"ingestion_id": "6b0c…", "run_id": "PW-…", "status": "completed",
 "organization_id": "northgate-roads", "findings": 12, "replaced_previous": false,
 "portal_path": "/orgs/northgate-roads/runs/PW-…"}
```

If files are missing you get `409` with one error per missing file. Calling `complete` again after success returns the same result.

### Status / troubleshooting

```
GET /api/v1/ingest/{ingestion_id}     -> status, files received / remaining, errors
GET /api/v1/ingest/schema             -> the JSON Schema (same as docs/run-submission.schema.json)
```

### Errors

Every error has the same shape:

```json
{
  "detail": "Run submission rejected: 2 problem(s) found. Fix them and resend.",
  "errors": [
    {"path": "run.status", "message": "Input should be 'complete' or 'incomplete'"},
    {"path": "features[3].properties.evidence", "message": "List should have at least 1 item after validation, not 0"}
  ],
  "ingestion_id": "a1f…"
}
```

| Status | Meaning | What to do |
|---|---|---|
| 401 | Missing / wrong `X-API-Key` | Check the key |
| 404 | Unknown ingestion id, or a file not in `files_expected` | Check the id / file name |
| 409 | Run exists (send `replace=true`), run id owned by another company, files still missing at `complete`, or ingestion already rejected | See `detail` |
| 413 | File larger than the limit | Compress or ask for a higher limit |
| 422 | Payload or file failed validation | Fix every item in `errors` and resend |
| 5xx | Server problem | Retry later (the uploader does this) |

Rejected submissions are logged on the server with their errors (`GET /api/v1/ingest/{ingestion_id}`).

### Checks the JSON Schema cannot express

The schema file covers types, required fields, enums and patterns. The server also checks:

- `finding_id` unique within the run; evidence `file` names unique within the run
- each finding has `geometry` or `position_local_m`
- bounding boxes ordered (`x_max > x_min`, `y_max > y_min`) and inside `width_px`/`height_px`
- `ended_at` not before `started_at`
- run id conflicts, and uploaded images matching their declared size

---

## 4. Example with curl

```bash
BASE=http://localhost:8000
RESP=$(curl -s -X POST "$BASE/api/v1/ingest/runs" -H "Content-Type: application/json" --data-binary @payload.geojson)
ID=$(echo "$RESP" | python -c "import json,sys; print(json.load(sys.stdin)['ingestion_id'])")
for f in $(echo "$RESP" | python -c "import json,sys; print(' '.join(json.load(sys.stdin)['files_expected']))"); do
  curl -s -X PUT "$BASE/api/v1/ingest/$ID/files/$f" -H "Content-Type: $(file -b --mime-type "$f")" --data-binary @"$f" > /dev/null
done
curl -s -X POST "$BASE/api/v1/ingest/$ID/complete"
```

## 5. Pre-flight checklist

- [ ] `schema_version` is `"1.0"`; `run_id` is new (or you are sending `?replace=true`)
- [ ] Coordinates are `[lon, lat]`; timestamps include a timezone
- [ ] Every finding has ≥ 1 evidence file, and `geometry` and/or `position_local_m`
- [ ] Evidence file names are unique across the run and exist in your upload folder
- [ ] Bounding boxes are in original-image pixels; `width_px`/`height_px` match the files
- [ ] Areas you could not scan are reported as `NOT_SCANNED` with a polygon; `status` is `incomplete` if coverage fell short
- [ ] Validate locally against `docs/run-submission.schema.json` (optional) before sending

## 6. Versioning

The payload carries `schema_version`, and today the portal accepts exactly `"1.0"`. Future additive, optional changes will become `1.1`, `1.2`, …, and the portal will keep accepting older 1.x payloads. A breaking change would become `2.0`. It would be announced in advance, and both versions accepted during a transition period.
