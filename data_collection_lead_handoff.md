# PaveWatch shared Pi recorder handoff

**For Abhinav Dhakal and the Sensor Payload and Data Acquisition agent · November 19, 2026**

Use the installed `collect` command on the shared PaveWatch Raspberry Pi 4 to record camera and LiDAR together. The installed release is `recorder-v2.0.4` (`5167c101fc24cb3103aa24675e6dc677f2755fe9`). The Pi keeps the source and rollback history in `/opt/pavewatch-recorder`. The existing `lidar start` command remains available for LiDAR-only work.

## What changed

| Previous collection workflow | V2 workflow |
| --- | --- |
| `collect` started LiDAR and camera jobs separately. Launch marks gave an approximate relationship between the streams. | Both streams share one systemd service and host-monotonic recording window. Capture waits for usable camera metadata and CRC-checked Compact packets. |
| The camera saved JPEGs, a relative PTS log, and a separate metadata array. An interrupted PTS file produced incorrect frame counts and a 50.01 fps summary for a 5 fps walk. | Each saved JPEG gets a same-request record with native sensor timestamp, applied exposure, frame duration, sequence when available, and SHA-256. Gaps and interrupted runs are explicit. |
| LiDAR raw packets retained userspace receive time. A long disk stall could exhaust the UDP buffer. | The raw framing remains compatible. A sidecar adds kernel receive time and overflow evidence when available, userspace clocks, native Compact times and counters. The effective socket buffer is 8 MiB on the Pi. JPEG encoding and durable writes use separate bounded queues. |
| The collection summary held start/end power readings and operator settings. | The recorder logs clock brackets, power, storage and loss during the run. The manifest records the active Git release, camera mode, scope, stop reason, and quality flags. |

The service owns scanner startup and idle cleanup. Combined capture and `lidar start` use the same service, which rejects a second recorder and caps capture at 20 minutes. Use the installed `collect` for live combined runs and avoid starting a separate UDP receiver on port 2115.

## Start a collection

Connect over the existing Tailscale share as `pavewatch`. If the SSH alias is configured, use `ssh picoscan-pi`. The documented endpoint is `100.72.89.22`. Use the team-provided key and the endpoint shown by your Tailscale client. Read the Pi’s workspace instructions first. [Pi access guide](integration/raspberry-pi-access.md).

~~~sh
cat ~/README.md ~/AGENTS.md
tail -n 20 ~/WORKLOG.md
collect status
cat /sys/class/net/eth0/carrier
vcgencmd get_throttled
libcamera-hello --list-cameras
~~~

Power the scanner and connect it directly to the Pi’s `eth0`. The configured path is scanner `192.168.0.1` to Pi `192.168.0.100:2115`. Carrier `0` indicates the Ethernet link is down even though SSH may still work over Tailscale. Confirm the recorder is idle, verify the actual storage mount, and check the camera framing and exposure before a moving pass.

~~~sh
collect --seconds 30 --label sidewalk-bench \
  --note "Ground run, measured marker spacing, camera and LiDAR facing down"
collect status
~~~

The ordinary command returns with `Recorder: recording` when both streams are ready. Begin moving after that message. If it reports that startup is still in progress, check `collect status` first. Add `--wait` to wait through finalization and service shutdown. SSH disconnection leaves the bounded job running. To end a run early, use `collect stop`. For a live run, confirm the service is inactive, measurement is stopped, and UDP output is off with `lidar status`.

| Profile | Camera mode | Default cadence |
| --- | --- | ---: |
| `imx219-bench` | Module 2, 1640 × 1232 binned | 10 fps |
| `imx219-full` | Module 2, 3280 × 2464 | 5 fps |
| `imx708-bench` | Module 3, 2304 × 1296 binned | 12 fps |
| `imx708-flight` | Module 3, 4608 × 2592 | 3 fps |

The default selects the binned profile for the installed sensor. The starting settings are a 1 ms exposure and gain of 1. Check the applied exposure and image brightness in a sample. Module 3 profiles use manual focus. Set `--lens-position` and check sharpness at the test height. The `collect LABEL SECONDS` syntax still works with V2.

Field runs default to `~/data/collections-v2/`. For a survey drive, check the actual mount with `findmnt --mountpoint /media/survey` and pass `--out /media/survey`, using its real mount path. The path must already exist, be writable by `pavewatch`, and have at least 1 GiB free above any space needed for the run. Use `--context-file` for rig notes and exported scanner settings, including filter state. Use `--calibration-file` for existing calibration and `--pose-file` for an independently recorded native-time pose log. The recorder copies the pose log at shutdown, so coordinate its flush with the end of capture.

## Verify and hand data to processing

| In the run folder | Use |
| --- | --- |
| `manifest.json` and `health.jsonl` | Check release, storage, start/stop state, flags, and health. Check worker summaries for stream-specific problems. |
| `camera/frames.jsonl` and JPEGs | Match by the `image` field. Use `SensorTimestamp_ns`, `ExposureTime_us` and `FrameDuration_us` for timing work. Preserve the applied settings in `camera/configuration.json`. |
| `lidar/raw.bin` and `lidar/packets.jsonl` | Preserve the original Compact UDP payloads with legacy-compatible raw framing and packet timing sidecar. Keep the before/after device snapshots with the run. |
| `clock/anchors.jsonl` | Preserve the bracketed Pi realtime, monotonic and boottime readings and clock-segment boundaries. |

Copy the whole finalized run to the processing machine. Verify the raw SHA-256 against the LiDAR summary and JPEG hashes against the frame index. Keep incomplete runs labeled and preserve their original files. Pass the run folder intact to `uv run survey_analyze.py <run-folder> --out <new-review-directory>` from the project’s `data_processing` folder.

The normal capture gates startup on the scanner transmit and Pi receive timestamps being within 100 ms. That is a coarse epoch check. Treat `--allow-unsynced` runs as clock diagnostics. For quantitative camera/LiDAR/pose alignment, verify the scanner timescale and lock, the installed camera’s timestamp event and row model, and the pose clock against an independent timing target. [Camera/LiDAR timing plan](integration/camera-lidar-timing.md).

## What the deployment tests established

The Pi tested as a Raspberry Pi 4 running Bullseye with an **IMX219 Camera Module 2** and the boot microSD. The LiDAR Ethernet link reported no carrier. Tests used the real camera and synthetic Compact packets through the real Linux UDP socket.

| On-Pi diagnostic | Observed result |
| --- | --- |
| 60 s binned at 10 fps | 600 JPEGs and 15,000 consecutive Compact packets. One userspace receive stall was logged, with continuous packet counters. |
| 10 s full resolution at 5 fps | 50 JPEGs and 2,500 consecutive Compact packets. |
| Early stop | 23 JPEGs and 591 packets preserved in an incomplete run. |
| Integrity and service behavior | JPEG hashes and dimensions, raw hash, packet CRCs, kernel receive timestamps, and clock records verified. A concurrent start was refused. Rollback and reactivation were tested. |

The diagnostic runs are in `~/data/diagnostics-v2/` under names ending in `v2-final-binned`, `v2-final-full`, and `v2-final-stop`. To repeat a camera-only hardware check with the scanner detached, run `collect --test-camera --seconds 10 --label camera-check --wait`. Keep these runs in diagnostic datasets, since their LiDAR packets are simulated.

## Continue commissioning and maintain the release

1. Restore scanner Ethernet and run a short stationary live capture. Confirm camera and Compact continuity, scan profile, clock plausibility, image exposure, and scanner idle after completion. Preserve any failed startup logs.
2. Check the live scanner’s spatial and temporal averaging settings. Record the filter state and window before any comparison run. Include a measured pavement step or target and a reference trajectory. Keep the operator and mast clear of the review corridor where practical.
3. Qualify Module 3 and the intended USB survey medium under a simultaneous capture of at least ten minutes. Check sustained cadence and writes, clock and pose coverage, power, thermals, loss, and recovery. Use the optical and motion references in the timing plan to score SA2. The diagnostics above establish recorder behavior on the bench setup.

In the Pi repo, `collect_v2.py` handles stream capture and file writes. `managed_collect.py` connects it to the service and operator commands. `lidar_control.py` handles scanner control and the LiDAR-only path. Commit changes in the repo, then deploy from a tagged release with the service idle. Keep credentials and recordings out of Git. Log deployments and verification in `~/WORKLOG.md`.

~~~sh
sudo -n git -C /opt/pavewatch-recorder log --oneline --decorate -6

# Roll back while the service is idle.
sudo -n /opt/pavewatch-recorder/apply-release.sh legacy-before-v2
lidar status

# Return to the tested V2 release.
sudo -n /opt/pavewatch-recorder/apply-release.sh recorder-v2.0.4
~~~

The rollback tag restores the previous collector and service. The release script also restores the previous UDP receive-buffer limit when rolling back. Operator documentation is available on the Pi at `/opt/pavewatch-recorder/COLLECT_V2.md`.
