# Shared Pi recorder source

This checkout builds on the Pi’s installed `recorder-v2.0.4` tag at commit `5167c101fc24cb3103aa24675e6dc677f2755fe9`. LiDAR profile verification, IMU capture, and the recorder watchdog are included in this checkout for the next Pi release. [Data collection lead handoff](../../../data_collection_lead_handoff.md).

| File | Role |
| --- | --- |
| `collect_v2.py` | Camera and Compact UDP workers, timestamps, storage and health records. |
| `lidar_telemetry.py` | Profile validation and comparison, scanner readbacks, and the Compact Type 2 decoder. |
| `managed_collect.py` | Operator arguments and the adapter that runs combined captures in the existing service. |
| `lidar_control.py` | Shared service control, scanner lifecycle and LiDAR-only capture. |
| `recorder_watchdog.py`, `pavewatch-watchdog.service` | Independent process that watches recorder health and archives faults. |
| `collect`, `lidar` | Installed command entry points. |
| `pavewatch-recorder.service`, `idle_at_boot.sh` | Service execution and startup idle check. |
| `90-pavewatch-compact-receiver.conf` | Kernel ceiling for the Compact receiver buffer. |
| `apply-release.sh` | On-Pi Git release installer and rollback procedure. |
| `lidar_record.py` | CoLa-A query helper for standalone captures with `--lidar-source`. |

## Watch a capture

The managed recorder starts the watchdog as a separate systemd service. It polls small status files in `/run` once a second. The recorder supplies counters and reuses its existing storage and power readings. The watchdog handles reporting while the recorder owns capture and scanner cleanup.

```sh
collect diagnostics
collect diagnostics --json
journalctl -u pavewatch-watchdog.service -f
```

- During capture, the watchdog checks for a stale recorder heartbeat, loss of valid LiDAR packets, stalled camera saves and missing IMU samples when requested or enabled. It reports invalid samples, stream gaps and drop indicators, Ethernet loss, low storage, Pi power flags and host clock breaks. The camera stall threshold allows at least 1.5 frame periods and is never shorter than one second.
- It flags recorder exit without a terminal record, startup or finalization delays over 30 seconds, and capture beyond the scheduled stop. The final report includes the recorder’s outcome, cleanup errors and quality flags. A graceful operator stop is reported as `stopped`.
- The live JSON is at `/run/pavewatch-watchdog/status.json`. Alert transitions appear in the journal. Each finalized report is saved under `/var/lib/pavewatch-watchdog/<request-id>.json` on the Pi. Its `session` field identifies the corresponding capture, and `faults` retains issues that cleared during the run. Copy this small report along with data when handing off a capture.
- `collect diagnostics` exits with code 1 when the report is unavailable or stale, or its severity is `error`. The separate service stays available between captures. It samples only the request file while idle.

In a 20-second test from a temporary checkout on the Pi, the watchdog used 0.24% of one CPU core and 11.7 MiB of peak resident memory. The IMX219 camera and synthetic Compact UDP input yielded 200 JPEGs, 5,000 scan packets and 2,000 IMU samples. Local fault injection verified detection of a frozen recorder and of a recorder killed without finalizing. The simulated scanner data leaves physical link-loss testing open.

## LiDAR profiles

The default requested profile is `pavewatch-50hz-025deg-276deg`. It expects 50 Hz, 0.25° angular spacing and a 276° azimuth span. It requests all echoes with moving averaging, particle, fog, interval, angular range, radial range and cuboid filtering disabled. Check or set these on the scanner in SOPASair. The recorder reads settings and compares them with the requested profile.

Use `--lidar-profile-file PATH` with either `collect` or `collect_v2.py` to name a different operating profile. Supply the three numeric values and the expected filters. Filter keys and values follow the picoScan150 API. For instance, this profile checks a three-scan moving average and all echoes. The recorder still logs the other reported filters. [SICK picoScan150 API](https://sickag.github.io/sick_lidar_developer_guide/picoScan100/picoScan150/api-rest-openapi/).

```json
{
  "name": "sidewalk-50hz-average-3",
  "scan_rate_hz": 50,
  "angular_resolution_deg": 0.25,
  "field_of_view_deg": 276,
  "filters": {
    "LFPmovingAveragingFilter": {"bEnable": true, "uiAveragingDepth": 3},
    "FREchoFilter": 1
  }
}
```

- `manifest.json → lidar_profile` records the request, the scanner’s before/after readbacks and the observed packet stream. The recorder measures scan rate from native frame timestamps and frame numbers, angular spacing from the scan grid, and field of view from recurring segment bounds. It reports the typical received-frame cadence separately. An angle filter can zero individual returns inside the packet envelope. Consult its reported limits for the configured crop.
- Look for `lidar_profile.verification.status`. `verified` requires stable packet measurements within 0.5 Hz, 0.005° angular spacing and 0.5° of the requested azimuth span, plus matching requested filters before and after the run. `mismatch` flags a measured or reported conflict or a settings change. `unverified` indicates missing or unstable evidence. The capture retains raw data and records a quality flag in the latter two cases.
- Inspect `lidar/config_before.json` and `lidar/config_after.json` for CoLa-A replies, REST values and query errors. The standalone recorder reads settings when given `--lidar-source 192.168.0.1`. The managed recorder already knows the scanner address.

## Built-in scanner IMU

SICK lists a built-in IMU for the PICS150-01000 Pro-1 (1134610) and identifies license part 1134384 for the UDP stream. With the scanner powered and Ethernet connected, check the active feature in SOPASair. Enable IMU data output to the Pi over UDP at `192.168.0.100:7503`. The recorder uses the scanner’s reported port when it can read a matching destination and falls back to UDP 7503. `--imu-port PORT` sets the receiver port for a custom setup. [SICK Pro-1 data sheet](https://www.sick.com/media/pdf/0/50/850/dataSheet_PICS150-01000-Pro-1_1134610_en.pdf), [SICK software licenses](https://support.sick.com/sick-knowledgebase/article/?code=KA-10714), [SICK IMU streaming example](https://sickag.github.io/sick_lidar_developer_guide/beginner-projects/imu-jump-and-run/).

- `imu/raw.bin` saves Compact Type 2 datagrams with the same receive-time and length framing as the scan file. `imu/samples.jsonl` indexes the raw offsets and records sensor-native microseconds, Pi receive timestamps, sensor-frame acceleration in m/s² including gravity, gyro in rad/s, and quaternions in `w,x,y,z` order. [SICK Compact format](https://www.sick.com/media/docs/3/23/623/technical_information_data_format_description_en_im0104623.pdf).
- Check `manifest.json → imu` for `status: recorded`, sample count and rate, reported enable state and destination, and integrity and timing counters. Scan and camera acquisition can finish when the optional IMU stream is unavailable.
- For the first live run, hold the mounted rig still, then tilt it slowly. Check that gyro and quaternion readings respond, the native timestamps increase and bracket the scan timestamps, and the receiver reports any loss. The IMU time is on the scanner’s clock. Its axes and attitude still need to be checked against the mounted rig before using the samples for motion correction.

## Test a checkout

From this folder on Linux, run the recorder with synthetic camera and LiDAR input. The test uses the Python standard library.

```sh
scratch=$(mktemp -d)
uv run --no-project collect_v2.py --simulate --seconds 2 --out "$scratch"
```

The command prints the run folder. Check the manifest for `status: complete`, a verified synthetic LiDAR profile, and about 200 synthetic IMU samples. Each run includes JPEGs and their index, Compact scan and IMU raw files and their sidecars, and clock anchors. Hardware camera operation uses the Pi OS Picamera2 and libcamera packages.

The archived sidewalk packets reported about 50 Hz, 0.25° and 276° in all six runs. Two three-second tests from a temporary checkout on the Pi used the real IMX219 camera and synthetic Compact UDP. Both recorded 30 JPEGs, 750 scan packets and 300 IMU samples. The separate UDP port test flagged a userspace receive stall and saved all expected datagrams. The scanner Ethernet port had no carrier during these tests, leaving live filter readback and IMU streaming to be verified.

## Maintain the shared Pi

The shared Pi uses `/opt/pavewatch-recorder` as its release repo. `apply-release.sh` reads tagged files from the root of that repo and installs them to the system paths used by `collect` and `lidar`. Keep this copy with the hardware design, stage tested recorder changes under the same filenames in the Pi repo, and deploy a tag while the recorder is idle. Record the deployed commit in `~/WORKLOG.md` and update the source revision here when syncing a later release.
