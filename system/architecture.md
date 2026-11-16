# Current functional architecture — PW-APPROACH-01

Updated November 16, 2026 from SRC-034 §§3.2–3.4. Component names are document selections; connections below are intended contracts pending the pin/power/firmware checks in [interfaces](../integration/interfaces.csv). This is not an executable wiring diagram.

```mermaid
flowchart TD
    GCS["Laptop: QGroundControl and run/export app"] <-->|Separate MAVLink telemetry| FC["MicoAir H743v2 AIO-35A / PX4 1.16.0"]
    POCKET["RadioMaster Pocket ELRS / critical alerts"] <-->|RC and handset telemetry| RX["RP1 V2 receiver"]
    RX <--> FC
    GNSS["M10G GNSS / compass"] --> FC
    FC --> ESC["Four integrated ESC channels"]
    ESC --> MOT["4 x X2216 880 KV / MR 10 x 4.5 props"]
    BAT["4S 14.8 V / 5200 mAh"] --> PWR["Monitoring and distribution"]
    PWR --> FC
    PWR --> ESC
    PWR --> LP["Protected LiDAR branch"]
    PWR --> RP["Regulated recorder branch"]
    LP --> L["Supplied picoScan150 Pro"]
    RP --> PI["Raspberry Pi 4 / Python recorder"]
    L -->|Ethernet scans and native time| PI
    CAM["Camera Module 3"] -->|CSI images and capture time| PI
    FC -->|Serial MAVLink pose and flight state| PI
    PI --> CARD["128 GB survey microSD / USB 3 reader"]
    PI --> HEALTH["HealthMonitor and persistent events"]
    HEALTH -.->|Payload alert bridge: unverified| FC
    CARD -->|Post-flight export and hash check| PC["Offboard processing: local or cloud undecided"]
    PC --> GEOM["GeometryAnalyzer"]
    PC --> VIS["VisualDetector"]
    GEOM --> FIND["FindingAssembler / evidence and warnings"]
    VIS --> FIND
    FIND -->|Validated GeoJSON and evidence references| API["Hosted reporting ingestion API"]
    API --> DB["PostgreSQL / PostGIS"]
    API --> FILES["Cloud evidence files"]
    DB --> PORTAL["Login / dashboard / evidence / PDF"]
    FILES --> PORTAL
```

FP owns aircraft/control and power distribution; DT owns health observability; SA owns the Pi capture/storage; GC owns missions and communications; PC owns post-flight analysis; RD owns the portal/database/evidence. Shared power/mounting/timing live in integration, with one BOM owner per component.

Flight control continues to own stabilization and recovery if the recorder fails. Raw imagery/ranges remain onboard during flight; only low-rate commands/status use operational radios. Pocket alert forwarding needs a supported PX4/ELRS/EdgeTX bridge. The separate laptop MAVLink radio is still to be specified; GC3's historical buffer stream remains undefined.

Each 2D LiDAR cross-section needs acquisition-time pose to reconstruct pavement. Rigid sensor calibration, native/common clock mapping, original pose retention, and independent references are required. Post-processed image alignment is a candidate improvement, not a guarantee. Local survey coordinates need origin/axes/scale/datum and a documented geographic conversion; an origin alone does not establish accuracy.

The baseline produces findings from one survey. Prior-survey comparison and learned RGB-D fusion are optional. **Hosted reporting is selected; processing deployment remains open.** A local SQLite review app is a fallback. The [source note](../references/new-evidence/2026-11-16-final-approach.md) tracks speed, energy, budget, and schema conflicts.

Commission in stages: ground power/capture/timing/telemetry, measured-pose stand/carriage and processing, installed commissioning, then authorized loaded flights. No step is presumed passed from the architecture diagram.
