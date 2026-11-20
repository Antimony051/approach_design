# PaveWatch run payload: field reference

What each field in a run submission means, with values from the sample run [`samples/sample_run/payload.geojson`](../samples/sample_run/payload.geojson).

- Short example covering every field (3 findings): [payload-example.geojson](payload-example.geojson)
- How to send a run (API steps, errors, checklist): [ingestion-spec.md](ingestion-spec.md)
- Machine-readable JSON Schema: [run-submission.schema.json](run-submission.schema.json)

The payload is a standard GeoJSON `FeatureCollection` with two extra top-level fields, `schema_version` and `run`. `run` describes the survey flight. Each item in `features` is one defect, called a *finding*.

## Rules that apply everywhere

- **Coordinates are `[longitude, latitude]`** (GeoJSON order), WGS 84 decimal degrees. A third value (altitude in metres) is optional.
- **Every timestamp includes a time zone**, e.g. `2026-08-05T09:32:00-04:00` or `...Z`. Timestamps without one are rejected.
- **Distances are in metres.** Every measurement states its own unit.
- **Unknown fields are rejected** inside `run`, `properties`, `evidence` and the other PaveWatch objects, so a typo like `severty` is caught. Standard GeoJSON members on the outer objects (`bbox`, `id`) are allowed.

## Overall shape

```
FeatureCollection
├── type: "FeatureCollection"
├── schema_version: "1.0"
├── run                      ← the survey flight (one per file)
│   ├── run_id, company{company_id, name}, site_name
│   ├── started_at, ended_at, status
│   ├── aircraft_id, operator, software_version
│   ├── local_frame_origin{lat, lon, alt_m, heading_deg}
│   ├── flight_path          ← GeoJSON LineString
│   └── data_warnings[]      ← problems with the whole survey {code, message, geometry}
└── features[]               ← one Feature per defect
    ├── type: "Feature"
    ├── geometry             ← GeoJSON Point (GPS position) or null
    └── properties
        ├── finding_id, detected_at, defect_type, subtype, description
        ├── severity, confidence, detection_source
        ├── gps_accuracy_m, position_local_m{x, y, z}
        ├── measurements{ name: {value, unit} }
        ├── quality_warnings[]  ← problems with this finding {code, message}
        └── evidence[]          ← images and files {file, kind, caption, ..., bounding_boxes[]}
```

## Top level

| Field | Required | Meaning | Sample |
|---|---|---|---|
| `type` | yes | Always `"FeatureCollection"` | `"FeatureCollection"` |
| `schema_version` | yes | Version of this data format. Only `"1.0"` is accepted today | `"1.0"` |
| `run` | yes | The survey flight | see [run](#run-the-survey-flight) |
| `features` | yes | The findings. An empty list `[]` is valid and means "no defects found" | 6 findings |

## `run`: the survey flight

| Field | Required | Meaning | Sample |
|---|---|---|---|
| `run_id` | yes | Globally unique ID for this flight. Letters, digits, `.` `_` `-`, max 100 characters. Suggested format: `PW-YYYYMMDD-HHMM-<aircraft>` | `PW-20260805-0932-01` |
| `company.company_id` | yes | Stable customer ID: lowercase letters, digits and `-`, 3–64 characters. A new ID creates a new company in the portal | `northgate-roads` |
| `company.name` | yes | Company name shown in the portal. Sending a different name renames the company | `Northgate Municipal Roads` |
| `site_name` | yes | Place that was surveyed | `Public Works Yard` |
| `started_at` | yes | When the flight started | `2026-08-05T09:32:00-04:00` |
| `ended_at` | no | When the flight ended. Must not be before `started_at` | `2026-08-05T09:49:50-04:00` |
| `status` | yes | `complete`, or `incomplete` if the flight or processing did not cover the planned area | `complete` |
| `aircraft_id` | no | Which drone flew | `PW-01` |
| `operator` | no | Pilot or operator | `R. Okafor` |
| `software_version` | yes | Version of the processing software that produced the findings | `pw-proc 0.3.0` |
| `local_frame_origin` | no* | Start point of the drone's local x/y frame: `lat`, `lon`, optional `alt_m`, optional `heading_deg` (0 = north, clockwise, 0–359.9). See [local frame](#local-frame). *Needed so findings without GPS can still be placed on the map | `lat 43.77011, lon -79.39876, alt_m 127.4, heading_deg 15.0` |
| `flight_path` | no | The route flown: a GeoJSON `LineString` of at least 2 `[lon, lat]` points. Drawn on the survey map | 22 points (back-and-forth pattern) |
| `data_warnings` | no | Problems with the survey as a whole. See below | 2 warnings |

### `run.data_warnings[]`

These let users tell **"no defects found"** apart from **"not enough data to know"**.

| Field | Required | Meaning | Sample |
|---|---|---|---|
| `code` | yes | Warning type in UPPER_SNAKE_CASE. See [warning codes](#warning-codes) | `NOT_SCANNED` |
| `message` | no | Short explanation for people | `Area blocked by parked vehicles` |
| `geometry` | no | The affected place or area: GeoJSON Point, LineString, Polygon or Multi* variants, in lon/lat. Polygons are drawn as shaded areas on the map | Polygon around the parked vehicles |

The sample has two run-level warnings, each with a polygon: `NOT_SCANNED` (area blocked by parked vehicles) and `NO_LIDAR_COVERAGE` (LiDAR returns dropped because of wet surface glare).

## `features[]`: one finding each

| Field | Required | Meaning |
|---|---|---|
| `type` | yes | Always `"Feature"` |
| `geometry` | see note | Best-effort GPS position as a GeoJSON `Point`: `[lon, lat]` or `[lon, lat, alt]`. Use `null` when there was no GPS fix (finding `F-0002` in the sample) |
| `properties` | yes | The finding's details. See below |

> **Position rule:** every finding needs a `geometry`, a `position_local_m`, or both. Send `position_local_m` whenever you have it.

### `properties`

| Field | Required | Meaning | Sample (`F-0003`) |
|---|---|---|---|
| `finding_id` | yes | ID, unique within the run. Same character rules as `run_id`. The portal sorts findings by this ID | `F-0003` |
| `detected_at` | yes | When the defect was detected | `2026-08-05T09:39:47-04:00` |
| `defect_type` | yes | One of `pothole`, `crack`, `depression`, `raised_area`, `vertical_step`, `other` | `pothole` |
| `subtype` | no | More detail, max 64 characters, e.g. `alligator`, `longitudinal`, `transverse`, `block`, `debris` | `null` |
| `description` | no | One plain-language sentence, shown on the finding page | `Pothole about 46 x 59 cm. Edges ravelled; loose aggregate in the bowl.` |
| `severity` | no | `low`, `medium` or `high`. Leave it out if the finding is not rated | `high` |
| `confidence` | no | Detection confidence from 0 to 1 | `0.96` |
| `detection_source` | no | What detected it: `image`, `lidar`, or `fused` (both) | `fused` |
| `gps_accuracy_m` | no | Estimated horizontal GPS error in metres (≥ 0). Drawn as a circle on the map | `3.1` |
| `position_local_m` | see note | Metres from `run.local_frame_origin`: `x`, `y`, optional `z`. See [local frame](#local-frame) | `x 57.63, y 15.38` |
| `measurements` | no | Sizes of the defect. See below | width, length, depth, area |
| `quality_warnings` | no | Problems with this finding only: a list of `{code, message?}` | `[]` |
| `evidence` | **yes, at least 1** | Images and other files that support the finding. See below | 3 files |

### `measurements`

A map from a measurement name to `{value, unit}`. Names use lowercase letters, digits and `_`. Units are free text up to 20 characters.

```json
"measurements": {
  "width":  {"value": 0.46,  "unit": "m"},
  "length": {"value": 0.59,  "unit": "m"},
  "depth":  {"value": 0.087, "unit": "m"},
  "area":   {"value": 0.21,  "unit": "m2"}
}
```

Any name and unit is accepted. The portal labels these well-known names and uses them in list summaries: `width`, `length`, `depth`, `height`, `max_width`, `area`, `volume`. It shows `m2` and `m3` as m² and m³.

### `evidence[]`

The order matters: the first image is shown first. The portal uses an `image_closeup`, if there is one, as the finding's thumbnail in lists.

| Field | Required | Meaning | Sample |
|---|---|---|---|
| `file` | yes | File name only, no folders. Letters, digits, `.` `_` `-`. **Unique across the whole run**, so start it with the finding ID | `F-0003_raw.jpg` |
| `kind` | yes | `image_raw`, `image_closeup`, `lidar_profile`, `lidar_scan`, or your own lowercase name | `image_raw` |
| `caption` | no | Text shown with the file | `Nadir frame, 5.9 m AGL` |
| `captured_at` | no | When the file was captured | `2026-08-05T09:39:47-04:00` |
| `width_px`, `height_px` | recommended for images | Original image size in pixels. **Checked against the uploaded file** | `2304`, `1296` |
| `bounding_boxes` | no, images only | Where the defect is in the image. See below | 1 box |

The sample finding `F-0003` has three evidence files: a raw frame (`image_raw`), a close-up crop (`image_closeup`) and a LiDAR cross-section chart (`lidar_profile`).

Images (`.jpg`, `.png`, `.webp`, `.bmp`, `.tif`) get thumbnails and previews automatically. Other files (for example `.ply` or `.las` 3D scans, `.csv`) are stored and offered as downloads. They cannot have bounding boxes. The limit is 50 MB per file.

### `bounding_boxes[]`

```json
"bounding_boxes": [{"label": "pothole", "bbox": [800, 728, 940, 961], "confidence": 0.96}]
```

| Field | Required | Meaning | Sample |
|---|---|---|---|
| `label` | yes | What the box marks, max 64 characters | `pothole` |
| `bbox` | yes | `[x_min, y_min, x_max, y_max]` in pixels of the **original** uploaded image. The origin is the top-left corner, x goes right and y goes down. The box must have a positive size and lie inside the image | `[800, 728, 940, 961]` |
| `confidence` | no | Detector confidence from 0 to 1 | `0.96` |

- **Do not draw boxes onto the image file.** The portal draws them on top, and users can switch them off.
- Images are shown exactly as stored, without EXIF rotation. Make sure the pixel orientation matches the boxes.

## Local frame

`position_local_m` is measured from `run.local_frame_origin`:

- **x** points along `heading_deg` (0 = north, clockwise)
- **y** points 90° clockwise from x (to the right, as in PX4's forward-right-down frame)
- values are in metres

For findings with no GPS fix, the portal converts this position to map coordinates and marks it as approximate.

## Warning codes

Codes are UPPER_SNAKE_CASE. Any code is accepted, but these have friendly labels and explanations in the portal and in PDF reports:

| Code | Meaning | Where to use it |
|---|---|---|
| `NOT_SCANNED` | Part of the site was not surveyed (blocked, aborted flight) | `run.data_warnings`, with a Polygon |
| `NO_LIDAR_COVERAGE` | LiDAR returns missing, so detection relied on images only | run or finding |
| `POSE_LOW_CONFIDENCE` | Weak drone position or attitude estimate | run or finding |
| `SCAN_IMAGE_MISALIGNED` | LiDAR and camera were not well synchronised | run or finding |
| `GPS_UNAVAILABLE` | No GPS fix for this finding | finding |

## Checks the JSON Schema cannot express

The schema file covers types, required fields, allowed values and patterns. The portal also checks that:

- `finding_id` is unique within the run, and evidence `file` names are unique within the run
- every finding has a `geometry` or a `position_local_m`
- bounding boxes are ordered (`x_max > x_min`, `y_max > y_min`) and inside `width_px` × `height_px`
- `ended_at` is not before `started_at`
- uploaded images match their declared `width_px` and `height_px`
