# SA — Sensor Payload & Data Acquisition

Lead: **Abhinav Dhakal**. Charter support: **Saugat Karki**. Requirements: **SA1–SA3; S3–S6**.

Updated November 16, 2026. **Status: Pi 4/Camera Module 3/USB survey card selected in SRC-034 §§3.2.1/3.3.3/3.4; simultaneous performance and integration pending.**

## Required function

Record real LiDAR/images concurrently, retain capture-time pose association and continuity evidence, and deliver a replayable, integrity-checked survey package for offboard analysis.

## Selected sensor and recorder stack

SRC-034 reports the supplied **picoScan150 Pro received and streaming Ethernet**. Confirm the physical label, firmware/licenses, system plug, cables, and supported modes; reference [20]'s PICS150-01000 Pro/1134610 is a cited datasheet identifier, not a checked label. Streaming alone is not SA1–SA3 acceptance evidence.

Use **Raspberry Pi 4 Model B** native Ethernet for LiDAR, **standard color Camera Module 3** over CSI, and a **SanDisk Extreme 128 GB microSD in a USB 3 reader** for survey data, separate from the OS card. The source's reader reference is SanDisk MobileMate SDDR-B531-GN6NN; exact card SKU/Pi RAM/OS versions still need freezing. Selection rationale is native Ethernet, USB 3 storage, and greater image detail than the earlier InnoMaker options. Orange Pi Zero 3, Pi Zero 2 W/hub, InnoMaker U20CAM-9281M/1080P, OS-card-only storage, and Samsung T7 remain alternatives. The SSD is no longer the primary storage item.

## Existing Pi and service access — SRC-039–041

Local records now identify an **existing Pi4 Model B, Debian11 Bullseye arm64 and roughly32GB boot card**, with successful administrator OpenSSH access recorded on November16 through Tailscale. [The connection guide](../../integration/raspberry-pi-access.md) gives the Tailscale member route, host identity, shared `pavewatch` login with the user-provided private key (D-026), and wired fallback. The selected Pi family is therefore supported by existing bench hardware, while RAM, power-adapter rating, driver/camera stack, recording performance and installed flight supply remain unverified. Do not price another Pi as necessary solely from the earlier $109 comparison estimate.

The user identifies the on-Pi LiDAR workspace as `/home/pavewatch/03-sensor-payload-acquisition`, with `tools/` for scripts and `docs/` for sensor documentation. Recorded sessions live separately in `~/data/sessions/` (`/home/pavewatch/data/sessions/`). Start with the Pi home `~/README.md` and `~/AGENTS.md` before operating tools.

The reused card retains existing accounts/projects and documented unrepaired filesystem findings; later SSH success is not a survey-storage pass. Initial card setup/repair scripts are not login steps. Sensor Ethernet/PTP remains a separate configuration to inventory and qualify; using the Pi Ethernet port for direct maintenance changes the sensor topology and must be recorded.

## Capture settings and estimates to test

- Downward transverse LiDAR plane and downward camera on one rigid removable plate. Whole-plate isolation, if used, preserves relative calibration; the full 276° scanner plane is not all usable pavement coverage.
- **~50 Hz at 0.25°–0.33°**, conditional on available scan profiles; **5–8 m, 0.25–1 m/s** plan. At 5 m near nadir, idealized spacing is ~22–29 mm across and 5–20 mm along track. Check full-envelope coverage, actual rates, and range at 5/6.5/8 m.
- Camera plan: **4608 × 2592 (11.9 MP) JPEG, 3 fps, exposure ≤1 ms, focus locked at survey height**. Encoding extrapolations, ~1.4 mm/pixel at 5 m, blur, rolling-shutter correction, and overlap require real measurements; known speed alone does not establish correction.
- Estimated camera writes **9–15 MB/s**; other streams **<1 MB/s**; ten-minute packages **6–10 GB**. Source card/reader throughput **~60–90 MB/s**, combined mass **~4 g**, and capacity **~12–20 runs** are unverified. Measure sustained per-card writes, shared load, thermals, retention, shutdown/recovery, and free space.
- Sensing-payload estimate **440–550 g** versus **650 g target** excludes aircraft/battery/power distribution by source wording. Reconcile all mounts, protection, cooling, plugs, and cable mass in the shared ledger.

## Acquisition software and timing

The selected direction is **Python** capture with Raspberry Pi camera support; C++ is a possible replacement for a capture bottleneck, while ROS 2 is an alternative rather than a required stack. Exact Raspberry Pi OS, Picamera2/libcamera, LiDAR library/format, MAVLink library, and parallel encoding setup remain to be specified.

RecorderSupervisor coordinates LidarCapture, CameraCapture, and PoseLogger; each writes through bounded queues with native/common timestamps and sequence IDs. HealthMonitor records drops/faults. ManifestWriter stores run identity/configuration, calibration IDs, file inventory/checksums, and complete/incomplete state. ExportService copies and verifies after landing. Interrupted packages remain incomplete even when individual files are usable.

SRC-036 now specifies the working [camera/LiDAR timing design](../../integration/camera-lidar-timing.md): same-request camera metadata and verified row exposure model; Compact Type 1 beam acquisition endpoints/indexing; **Pi4 software PTP / CLOCK_REALTIME common reference**; bracketed native boot-clock maps about once/second; native FC measurement-time mapping, e.g. TIMESYNC if supported; explicit clock-segment validity and independent tests. Check actual PICOSCAN TIME SYNC PTP **1134388** / STREAMING **1134356** features, timestamp event/clock semantics, applied blanking/pixel rate and packet epoch. Preserve native times, host receive times, maps, sync events and uncertainty separately. Readout- versus exposure-start formulas require optical tests at more than one exposure; no installed support or accuracy is inferred.

The source adds a first **timing bench profile**: **2304×1296 10-bit 2×2 binned/HDR off**, ~1 ms exposure, **10–15 recorded fps**, **3 m / 0.25–0.5 m/s**, SSD. Keep this separate from flight full-resolution 3 fps/5–8 m/USB-card planning. Stored encoding/rate remains unspecified for the new mode. The source-calculated **17.30 ms** binned and **68.12 ms** full-mode sweeps must be checked on the installed driver; do not apply one mode's timing or file-size estimates to another.

Independent light-pulse/photodiode and encoder tests target **P95 ≤3 ms, median within ±1 ms, drift ≤1 ms/10 min** as proposed development goals. SA2 remains **≤20 ms over ≥10 min** including sensor-to-motion-reference mapping. Calibrate, freeze, score a fresh run, and repeat under installed flight/media load; no pass is claimed. Ground fixture and optional SSD equipment are tracked in the BOM.

Historical leads: SRC-006/007/011/012/021/022/023/028. Their 15 Hz, USB-camera, SSD, and Pi 5 assumptions are not current selections.

## Shared design records

Maintain one owning row per component in [the BOM](../../procurement/bom.csv), exact connections in [interfaces](../../integration/interfaces.csv), and affected [power](../../integration/power-budget.csv), [mass/fit](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), [verification](../../verification/plan.md), and [decisions](../../decisions/decision-log.md). Design selection is not purchase authorization or test evidence. Blank installed/price values remain unknown.

Current source: [SRC-034 final approach](../../references/new-evidence/2026-11-16-final-approach/PaveWatch_Approach_Final.docx), [readable text SRC-035](../../references/new-evidence/2026-11-16-final-approach/approach-text.txt), and [reconciliation](../../references/new-evidence/2026-11-16-final-approach.md). Earlier source IDs resolve through [the source index](../../references/source-index.md).
