# Camera/LiDAR timing source incorporation

Date: November 16, 2026. The user requested incorporation of the local **PaveWatch_Camera_and_LiDAR_Timing.docx**, dated November 16. This entry reviews supplied project content; external links were retained from the DOCX and were **not reopened or independently verified** during incorporation. No project measurements or live hardware configuration were performed.

Artifacts: [unchanged DOCX, SRC-036](2026-11-16-camera-lidar-timing/PaveWatch_Camera_and_LiDAR_Timing.docx), [readable extract, SRC-037](2026-11-16-camera-lidar-timing/timing-text.txt), and [unmodified Figure 1, SRC-038](2026-11-16-camera-lidar-timing/rolling-shutter.png). Hashes and original path are in [the manifest](../source-manifest.csv). The extract preserves equations as parenthesized fractions/subscripts, line breaks, table boundaries and embedded hyperlink targets; original layout remains in the DOCX.

## Information incorporated

The maintained [timing design](../../integration/camera-lidar-timing.md) defines row exposure midpoints, verification of timestamp event/clock semantics, active IMX708 line-time checks, boot-to-realtime sample triplets, software PTP with Pi grandmaster, Compact Type 1 beam-time interpolation, native FC time mapping, iterative row-dependent projection, retained metadata and independent optical/encoder tests. Shared contracts, SA/PC/DT briefs, verification, interfaces, compatibility and fixture/BOM records link to it.

## Source claims and boundaries

- **Calculated camera timing:** non-HDR binned 2304×1296 at 13.36 µs/row and 17.30 ms sweep; full 4608×2592 at 26.29 µs/row and 68.12 ms sweep. Values derive from source-cited `rpi-6.18.y` mode tables, not the installed Pi. Verify applied blanking/pixel rate and optical row behavior.
- **Timestamp ambiguity explicitly preserved:** `S - E/2 + y*tau + delta` assumes the source's readout-based timestamp interpretation. An exposure-start timestamp instead needs `S + E/2` for row zero and its corresponding offset. Picamera2/libcamera/Unicam semantics, MONOTONIC versus BOOTTIME, row direction and transformations require installed-stack tests with more than one exposure duration.
- **Clock plan:** software PTP uses Pi CLOCK_REALTIME as common reference, with native camera boot times mapped by bracketed samples about once/second; ≤0.2 ms bracket is an example target. Verify device epoch/timescale, actual grandmaster and sync; do not assume the example `ptp4l` command establishes role/all intervals. Preserve lock loss/steps and avoid interpolation across invalid segments. NTP remains conditional fallback.
- **Variant/licenses:** source names PICOSCAN TIME SYNC PTP **1134388**, PICOSCAN STREAMING **1134356**, Compact Type 1 and software timestamping. These identify features to check, not confirmed entitlements/configuration of the received Pro.
- **Bench profile:** 3 m, 0.25–0.5 m/s, binned 10-bit HDR-off camera at 10–15 recorded fps, ~1 ms exposure and SSD are first bench settings. They do not silently change SRC-034's 5–8 m, user-confirmed 0.25–1 m/s, full-resolution 3 fps and USB survey card. Actual encoding/rate and medium must be logged; SSD remains conditional ground equipment. Full-resolution bandwidth/capacity estimates do not transfer to the new bench mode without measurement.
- **Scan example:** 25 Hz / 40 ms revisits illustrate sampling, not a replacement for the flight proposal's conditional ~50 Hz profile. Linear beam-time interpolation requires verified even timing/order and original indices despite missing echoes.
- **Proposed tighter goals:** cross-sensor absolute residual 95th percentile ≤3 ms, signed median within ±1 ms, drift ≤1 ms/10 min, with maximum/reference uncertainty/coverage reported. These are proposed bench goals, not passed tests, a requirement amendment, or a complete SA2 sensor-to-motion-reference demonstration.
- **Tests:** actual optical-edge/photodiode timing and an independent encoder trajectory are needed. LED command timestamps alone are not optical truth. Freeze calibration before a fresh scored run, score invalid intervals explicitly, and validate geometric projection separately from pure timing.

## Direct links preserved from the supplied document

These are provenance links, not a new verification record. Numbering matches the DOCX.

| Source | Document / section |
| --- | --- |
| [1] | [Picamera2 manual §6.4.1 / Appendix C](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf#page=39) |
| [2] | [Raspberry Pi non-HDR IMX708 driver, rpi-6.18.y](https://github.com/raspberrypi/linux/blob/rpi-6.18.y/drivers/media/i2c/imx708.c) |
| [3] | [Raspberry Pi camera software](https://www.raspberrypi.com/documentation/accessories/camera-software.html), [V4L2 image-source controls](https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/ext-ctrls-image-source.html) |
| [4] | [Camera hardware specifications](https://www.raspberrypi.com/documentation/accessories/camera.html) |
| [5] | [libcamera SensorTimestamp control definition](https://github.com/raspberrypi/libcamera/blob/main/src/libcamera/control_ids_core.yaml) |
| [6] | [Pi Unicam frame-start timestamps](https://github.com/raspberrypi/linux/blob/rpi-6.18.y/drivers/media/platform/broadcom/bcm2835-unicam.c) |
| [7] | [Linux clock_gettime](https://www.man7.org/linux/man-pages/man3/clock_gettime.3.html) |
| [8] | [SICK time synchronization guide](https://sickag.github.io/sick_lidar_developer_guide/shared-features/time-synchronization/) |
| [9] | [picoScan150 license/part-number list](https://sickag.github.io/sick_lidar_developer_guide/picoScan100/picoScan150/licenses/) |
| [10] | [SICK Pi4 software-PTP example KA-10645](https://support.sick.com/sick-knowledgebase/article/?code=KA-10645) |
| [11] | [LinuxPTP ptp4l manual](https://www.linuxptp.org/documentation/ptp4l/) |
| [12] | [SICK Compact Type 1 format](https://sickag.github.io/sick_lidar_developer_guide/data-streaming/compact-format/#type-1-scan-data) |
| [13] | [SICK Type 1 binary schema](https://github.com/SICKAG/KaitaiStructDescriptions/blob/public/formats/type_1_primary_data_spherical_coordinates.ksy) |
| [14] | [MAVLink TIMESYNC protocol](https://mavlink.io/en/services/timesync.html) |
