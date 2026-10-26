# PaveWatch investigation 04: onboard computing, storage, and telemetry

**Research status:** preliminary architecture and verification plan. No computer, storage device, regulator, camera, or flight-controller link has been purchased, weighed, powered, or flight-tested by this project.

**Price/specification date:** USD planning prices and manufacturer documentation were checked on **2026-09-19**. Prices exclude tax, shipping, and university purchasing overhead. A manufacturer list price is a planning reference, not a quotation. The picoScan150 remains challenge-supplied if the team is selected and is not included as a purchase.

## 1. Scope and recommendation

### Recommendation

Use a **headless Raspberry Pi 5 with 2 GB RAM**, Raspberry Pi OS 64-bit, active cooling, and a dedicated **256 GB USB 3 SSD** as the initial onboard recorder. Connect the picoScan150 directly to the Pi's RJ45 Ethernet port, connect the RGB camera through one of the Pi 5's CSI camera ports, and connect the Pixhawk companion link through a dedicated MAVLink serial interface. Keep the flight controller's ground-control radio on its own telemetry port. Use a separate battery-derived 5 V/5 A payload regulator; do not power the Pi, SSD, or camera from a Pixhawk telemetry-port 5 V pin.

The Pi should capture and validate data, not run the complete change-detection pipeline in flight. The initial flight product is a replayable survey folder containing raw LiDAR packets, frame-level RGB files or an explicitly documented video stream, flight-controller telemetry, health events, configuration, calibration identifiers, and checksums. Processing and model inference occur on a laptop after landing. This keeps the first build within the approximately **$1,000 total capstone target**, preserves raw evidence when an algorithm changes, and prevents an onboard computer failure from being a flight-control failure.

The proposed MVP acquisition profile is:

- picoScan150 Compact UDP over its 10/100 Ethernet interface, with a design allowance of **10 MB/s** until the delivered sensor and selected profile are measured;
- global-shutter RGB at **1,440 x 1,080, 15 frames/s, individual JPEG files** as the initial storage-friendly mode, with fixed exposure/gain/white balance where the camera supports them;
- a full MAVLink/flight-controller telemetry record over the companion link, plus the flight controller's native log copied after landing;
- a 256 GB SSD with at least 20% free-space reserve and a 30-minute bench/session target;
- low-rate health/status telemetry to ground control, with raw LiDAR and RGB retained locally rather than sent over the SiK radio.

The 2 GB Pi is intentionally a capture-only configuration. Select a 4 GB Pi 5 only if the sustained-capture test shows memory pressure, the camera pipeline requires larger buffers, or an edge-processing experiment is explicitly approved. The current Raspberry Pi product brief lists the 2 GB board at $65 and the 4 GB board at $110; the extra memory is not part of the MVP requirement. [S1]

### Concrete fallback

The direct flight fallback is a **borrowed Raspberry Pi 4 Model B**, preferably 2 GB or 4 GB, with the same capture service, a high-endurance microSD card or USB 3 SSD, and the same separate 5 V regulator. It has Gigabit Ethernet, USB 3, a CSI camera port, microSD storage, and a 5 V/3 A input, so it can still receive the picoScan150 and a Pi-compatible CSI camera. It is slower and has only one two-lane CSI camera connector, but it is a credible capture-only fallback. Raspberry Pi's current product brief lists the 2 GB Pi 4 at $55 and the 4 GB at $100; a university-owned board should be recorded as **available to borrow** with $0 project purchase cost. [S2]

If no Raspberry Pi is available, a borrowed university Linux laptop or small x86 lab computer can acquire the LiDAR through its Ethernet port and log MAVLink through a USB-to-UART adapter. It must pass the acceptance checks in this brief: 1 Gb/s Ethernet or better, USB 3, at least 16 GB RAM, 256 GB or more of sustained-write storage, Ubuntu 24.04 LTS/Debian-class Linux, and a battery or isolated power arrangement suitable for bench work. A laptop is a **ground/bench and post-flight recovery fallback**, not an assumed aircraft payload: mass, vibration, connector retention, input power, and safe mounting are unresolved until a specific device is offered.

The Jetson Orin Nano Super Developer Kit is a plausible **borrowed or later upgrade** for edge inference. NVIDIA documents two CSI camera interfaces, Gigabit Ethernet, USB 3-class host ports, removable microSD/NVMe options, JetPack support, and configurable 7–25 W operation. However, NVIDIA's current FAQ lists a $399 MSRP while the original launch announcement listed $249, and the kit needs active thermal management and a larger power/weight allowance. It is therefore not a purchase requirement for the capstone MVP. [S3][S4][S5][S18][S19]

## 2. Evidence and assumptions

### 2.1 Status labels

- **Proposed:** an architecture or threshold that the team will test; it is not a project measurement.
- **Planned purchase:** a budget placeholder for hardware not yet acquired.
- **Available to borrow:** a university or team device only if a specific unit is actually assigned and its configuration is recorded. No such unit is confirmed in the repository.
- **Simulated:** a replay, public-data, or synthetic-data demonstration without the complete aircraft hardware.
- **Measured:** a value obtained by this project and stored in the repository. There are currently no measurements for this investigation.
- **Manufacturer-stated:** a fact in a cited manufacturer document. It is not equivalent to a PaveWatch flight result.

### 2.2 Hardware evidence

The Raspberry Pi 5 manufacturer specification supports the recommended interfaces: Gigabit Ethernet; two USB 3.0 ports with simultaneous 5 Gb/s operation; two four-lane MIPI camera/display transceivers; microSD SDR104 storage; a PCIe 2.0 x1 interface for an M.2 adapter; and 5 V/5 A USB-C input. Raspberry Pi recommends active cooling under sustained load and specifies an operating temperature of 0–70 °C. [S1][S6][S7]

The Pi 5 camera connector changed to a 22-pin mini connector. A Pi 5 integration therefore needs the correct standard-to-mini CSI cable; a Pi 4 uses the 15-pin camera connector. Raspberry Pi states that its camera modules are compatible with Raspberry Pi computers that have CSI connectors. [S8]

The Raspberry Pi Global Shutter Camera is a useful official camera fallback: it is a 1.58 MP colour Sony IMX296 camera, outputs RAW10, supports up to 1,456 x 1,088 at 60 Hz, weighs 34 g or 41 g with its adapter/dust cap, and supports an external trigger input. The trigger is a 1.8 V signal and needs the documented level conditioning. Item 03 currently proposes the Arducam B0445 colour global-shutter CSI camera; its actual Pi driver, frame timestamp behavior, mass, and JPEG pipeline remain to be validated. [S8][S9]

Raspberry Pi lists Ubuntu support for Pi 4 and Pi 5, but the recommended image for this capture service is the current 64-bit Raspberry Pi OS because it is the board vendor's primary camera and firmware path. Ubuntu 24.04 server is a valid headless fallback after confirming camera-driver and GPIO behavior on the selected image. [S10]

The earlier investigations establish the following project inputs:

| Input | Planning value | Status and consequence |
|---|---:|---|
| picoScan150 supply | 9–30 V DC; 4.5 W typical; up to 17 W in the cited configuration | Manufacturer-stated; exact delivered system plug and output options unresolved. Use a fused sensor branch and reserve the upper value. [S11] |
| picoScan150 Ethernet | 4-pin D-coded M12, 10/100 Ethernet | Manufacturer-stated; use a direct isolated link in the MVP. [S11] |
| LiDAR capture bandwidth | 10 MB/s sustained design target | Proposed conservative target from Investigation 02, not a measured packet rate. The 100 Mb/s link has a theoretical 12.5 MB/s line-rate ceiling. |
| RGB primary | Arducam IMX296 colour global-shutter CSI camera | Proposed by Investigation 03; driver, timestamp, output size, and storage encoding are unresolved. |
| RGB fallback | Raspberry Pi Global Shutter Camera or a borrowed UVC global-shutter camera | Proposed fallback; external trigger and lens/adapter wiring must be tested. |
| Flight controller | Pixhawk 6C in the proposed Holybro X500/S500 system | Proposed platform from Investigation 01; final flight stack and port assignment are not centrally frozen. |
| Ground control | QGroundControl through the flight controller's telemetry radio | Proposed; raw survey data remains onboard. |
| Time | Pi monotonic clock, sensor timestamp/PTP when available, FC MAVLink time, camera timestamp/trigger | Proposed; end-to-end offset and drift are to be measured. |
| Flight duration | 10–15 minute first flight; 30-minute bench/session target | Planning assumptions, not aircraft endurance measurements. |

### 2.3 Data-rate assumptions

The storage plan uses decimal MB and GB for readability. Binary MiB/GiB will be shown only where it changes a decision. The actual sensor packet lengths, camera compression ratio, flight-controller message rates, and filesystem behavior must be recorded during commissioning.

#### LiDAR

Investigation 02 proposes a **10 MB/s sustained raw-capture target** because a high-resolution, multi-echo picoScan150 stream can approach the 100 Mb/s interface limit. This is not a promise that the supplied unit produces exactly 10 MB/s. The acquisition service must measure bytes, packets, segments, complete frames, out-of-order packets, and parse failures. If the selected profile exceeds the Ethernet or storage acceptance gate, reduce the scan frequency, echo count, angular window, or profile and preserve the exact configuration in the manifest.

#### RGB

The camera sensor's uncompressed RAW10 upper bound is much larger than the practical MVP storage mode:

```text
pixels/frame = 1,440 × 1,080 = 1,555,200
RAW10 bytes/frame ≈ 1,555,200 × 10/8 = 1,944,000 bytes
RAW10 at 30 fps ≈ 58.32 MB/s = 3.50 GB/min
RAW10 at 60 fps ≈ 116.64 MB/s = 6.998 GB/min
```

These values are calculated upper bounds before transport/container overhead. Continuous RAW10 recording is a **stress-test mode**, not the initial flight storage mode.

For the MVP, capture individual JPEG frames so each frame has its own sequence number, timestamp, checksum, and quality flag. Use this planning assumption until the camera is measured:

```text
15 frames/s × 0.75 MB/frame average JPEG = 11.25 MB/s
15 frames/s × 1.00 MB/frame conservative JPEG = 15.00 MB/s
```

The 0.75 MB average and 1.00 MB conservative value are proposed encoding allowances, not measured image sizes. A texture-rich or poorly exposed pavement scene may exceed them. The capture service must report the actual rolling mean, maximum, and percentile frame sizes.

#### Flight-controller logs and health data

Reserve **0.20 MB/s**, or 12 MB/minute, for raw MAVLink/pose/IMU telemetry and an additional **0.01 MB/s**, or 0.6 MB/minute, for health, clock, event, and manifest records. These are intentionally generous planning allowances for a first implementation. PX4's native ULog is a separate binary flight-controller log and its final size depends on the selected topic set; copy it after landing and record its checksum rather than relying on a guessed size. PX4 describes ULog as a self-describing log format with monotonic timestamps for logged message series. [S12]

#### Aggregate storage design point

The conservative flight design point is:

```text
LiDAR raw capture                       10.00 MB/s
RGB JPEG frames                         15.00 MB/s
FC telemetry                            0.20 MB/s
health/events/metadata                  0.01 MB/s
subtotal                                25.21 MB/s
20% filesystem/container/index margin   5.04 MB/s
design write rate                       30.25 MB/s
design storage rate                  ≈ 1.815 GB/min
```

At that design point:

| Session | Stored survey data before reserve |
|---:|---:|
| 10 minutes | approximately 18.2 GB |
| 15 minutes | approximately 27.2 GB |
| 20 minutes | approximately 36.3 GB |
| 30 minutes | approximately 54.5 GB |

The recommended 256 GB SSD therefore provides substantial capacity for a 30-minute survey session, repeated takeoff attempts, and post-flight intermediate products while retaining a 20% free-space reserve. A 128 GB device is acceptable only after a sustained test and with a defined session limit; it is not the preferred initial recorder. If continuous RAW10 is enabled, the rate is approximately 8.7 GB/minute before LiDAR and overhead, so the session target must be reduced or the camera stream changed.

### 2.4 Acquisition and safety assumptions

The onboard computer is not in the flight-control safety loop. Loss of Pi power, SSD failure, camera failure, or LiDAR Ethernet loss must not prevent the Pixhawk from stabilizing, receiving RC input, or reaching a pilot-commanded landing. The Pixhawk's own power module supplies the flight controller; the companion computer and sensor use separate payload branches.

The first system uses dry-weather, supervised, low-altitude testing. The Pi 5's 0–70 °C manufacturer operating range and exposed connectors are stricter for the payload computer than the picoScan150's documented range. The Pi must be mounted in a ventilated, splash-protected enclosure with no claim of waterproof operation. [S1][S6][S11]

No claim is made here that the proposed camera can sustain 15 fps JPEG, that a selected SSD can sustain 30.25 MB/s in a vibrating aircraft, or that PTP is licensed on the delivered picoScan150. Those are verification gates.

## 3. Proposed components and software

### 3.1 Compute-platform comparison

| Option | Ethernet and camera/USB interfaces | Storage and OS | Power/environment | Current planning cost and decision |
|---|---|---|---|---|
| **Raspberry Pi 5, 2 GB** | Gigabit Ethernet; 2 x USB 3.0 and 2 x USB 2.0; 2 x four-lane MIPI camera/display connectors; PCIe 2.0 x1 for an M.2 adapter | microSD SDR104; USB mass storage; NVMe through a separate M.2 adapter; Raspberry Pi OS current 64-bit release; Ubuntu 24.04 server is supported | 5 V/5 A recommended for full peripheral capability; 0–70 °C; active cooling recommended under sustained load | **$65 board list price. Recommended MVP.** [S1][S6][S10] |
| Raspberry Pi 5, 4 GB | Same interfaces as 2 GB | Same OS/storage choices | Same 5 V/5 A and thermal requirements | **$110 board list price. Optional only** if capture tests show memory pressure. [S1] |
| **Borrowed Raspberry Pi 4 Model B, 2/4 GB** | Gigabit Ethernet; 2 x USB 3.0 and 2 x USB 2.0; one two-lane MIPI CSI camera port | microSD; USB mass storage; Raspberry Pi OS or Ubuntu 24.04 server support | 5 V/3 A minimum; 0–50 °C; lower performance and lower thermal ceiling than Pi 5 | **$0 if borrowed; $55 2 GB or $100 4 GB official list price. Flight fallback.** [S2][S10] |
| Borrowed Linux laptop/NUC/mini-PC | Must have 1 Gb/s Ethernet, USB 3, and a USB-UART adapter; CSI is not assumed, so use a UVC camera or separate camera recorder | Internal NVMe/SSD with at least 256 GB free; Ubuntu 24.04/Debian-class Linux; easy access to full desktop tools | Exact input voltage, temperature, mass, connector retention, and vibration tolerance depend on the offered unit | **$0 project cost if borrowed. Bench, recovery, and post-flight fallback; not an aircraft requirement.** |
| Borrowed or later **Jetson Orin Nano Super Developer Kit** | NVIDIA documents Gigabit Ethernet, USB 3-class host ports, two camera paths, and a carrier with microSD/NVMe options | JetPack/Jetson Linux; CUDA/TensorRT/VPI available for later edge inference; current guide supports microSD or NVMe installation | Configurable 7–25 W; active fan/thermal design and dedicated DC input; no weather rating assumed | **Borrow only or defer.** NVIDIA's current FAQ lists $399 MSRP; an older launch article lists $249, so price is not stable enough for the MVP budget. [S3][S4][S5][S18][S19] |

The Pi 5 is selected because it has enough I/O and write bandwidth for capture while keeping the flight payload and software stack small. A Jetson's accelerator is valuable only after an image/LiDAR inference workload is demonstrated on the laptop and shown to need edge execution. A borrowed laptop is more useful for development, replay, and recovery than for flight.

### 3.2 Recommended MVP bill of materials

| Component | Status | Planning cost | Mass/power allowance | Notes |
|---|---|---:|---:|---|
| Raspberry Pi 5, 2 GB | Planned purchase or borrow | $65 | 70 g, unmeasured; capture-only 5 V rail design up to 25 W | Official board list price and interfaces are in [S1]. Measure assembled board with headers and cables. |
| Raspberry Pi Active Cooler or equivalent protected fan/heatsink | Planned | $5–$15 | 10–20 g; less than 1 W design allowance | Pi 5 sustained capture should not rely on passive cooling. Verify vibration and fan tachometer behavior. |
| 256 GB USB 3 SSD with short retention cable | Planned | $35–$60 planning allowance | 45–80 g, unmeasured; 1–4 W planning allowance | Preferred recorder. Exact model, sustained write, temperature, and connector retention are unresolved. |
| High-endurance 128/256 GB microSD | Planned fallback | $15–$35 planning allowance | 5–15 g, unmeasured | OS boot media or lightest recorder only after actual sustained-write test. Keep data separate from the OS where possible. |
| 5 V/5 A buck regulator, battery-rated for 16.8 V, fuse, LC filter, enable, and undervoltage protection | Planned or borrow | $35–$55 | 50–80 g, unmeasured | Separate payload branch. Do not use the Pixhawk TELEM 5 V pin. Verify transient response with the SSD/camera attached. |
| 22-pin Pi 5 CSI cable and strain relief | Planned | $5–$15 | 5–15 g | Required for Pi 5; connector type differs from Pi 4. |
| Pixhawk companion cable or isolated USB-UART adapter | Planned or borrow | $10–$25 | 10–25 g | TX/RX/GND only for the MVP; do not connect the cable's 5 V supply to the Pi. |
| Ventilated, splash-protected enclosure/plate, vibration isolators, tie-down, and cable retention | Fabricate/planned | $25–$50 | 40–80 g, unmeasured | Protect the Pi and SSD from prop wash and vibration without sealing heat inside. |
| **Item 04 preferred acquisition package, excluding sensor, camera, airframe, and radio** |  | **approximately $180–$280** | **approximately 230–370 g allowance** | This excludes the optional microSD fallback. Add approximately $15–$35 and 5–15 g if it is purchased as a second storage option; all allowances must be weighed. |

The package is compatible with the prior investigation's approximately $1,000 initial-build budget only if the picoScan150 is supplied, the flight kit and radio/charger are borrowed or already included, and the acquisition hardware is selected at the lower end of the range. If the aircraft mass budget cannot absorb the SSD/enclosure allowance, first test a 256 GB high-endurance microSD; if it fails the sustained-write gate, use the SSD and revisit the airframe/mount budget rather than silently accepting data loss.

### 3.3 Software decomposition

Use one mission supervisor and independently restartable acquisition workers. The first implementation can be a small systemd-managed Linux service set; ROS 2 is optional and must not be an acquisition dependency.

```text
missiond / state machine
├── sensor_capture       raw UDP/pcap capture, packet index, LiDAR counters
├── lidar_decode          Compact UDP segment assembly and normalized frames
├── camera_capture       CSI/UVC capture, frame sequence, metadata, JPEG writer
├── mavlink_logger       FC serial stream, heartbeats, pose/IMU subset, events
├── healthd              temperatures, voltage, free space, process liveness
├── clockd               monotonic/UTC relation, PTP/NTP status, offset events
├── storage_writer        queues, atomic files, rotation, fsync/checkpoints
└── finalizer             manifest, checksums, stop marker, replay summary
```

The workers must use bounded queues. If a writer queue fills, the worker must report a dropped packet/frame and increment a counter; it must not silently block the health worker or grow memory without limit. Raw packets and frame files are the primary evidence. Normalized JSONL/index files are convenience products and can be regenerated from raw data.

## 4. Interfaces and data flow

### 4.1 Component-level compute/network/storage diagram

```text
                                      ┌────────────────────────┐
                                      │ Ground laptop / QGC     │
                                      │ mission upload, status  │
                                      └───────────▲────────────┘
                                                  │ SiK radio / MAVLink
                                                  │
             4S battery                           │
                 │                                 │
       ┌─────────┴──────────┐                ┌─────┴────────────┐
       │ flight power/PDB    │                │ Pixhawk 6C        │
       │ + PM02 for FC       │                │ PX4/FC, GNSS, IMU │
       └────┬─────────┬──────┘                └──┬───────────┬────┘
            │         │                            │           │
       fused 9–30 V   │ 5 V FC rail                │ TELEM1    │ TELEM2
       LiDAR branch   │                            │ 915 MHz   │ MAVLink
            │         │                            │ radio     ▼
            ▼         ▼                            │     ┌───────────────┐
       picoScan150  5 V/5 A payload buck            │     │ Raspberry Pi 5 │
       10/100 M12       │                            │     │ mission logger │
            │           │                            │     └─┬────┬────┬──┘
            │           └──── Pi + cooler + SSD     │       │    │    │
            │                                      │       │    │    │
            └──────── direct RJ45 / static IP ───────────────►│    │    │
                                                           │    │    │
                                CSI-2 camera ──────────────►┘    │    │
                                GPIO/PPS/LED trigger ──────────┘    │
                                USB 3 SSD / microSD ────────────────┘

  Time products: Pi monotonic + UTC mapping, sensor timestamp/PTP/NTP status,
  FC MAVLink time, camera exposure/driver/trigger time, and measured offsets.
  Raw data remains local; only low-rate health/status crosses the telemetry link.
```

### 4.2 Network topology

#### MVP direct link

1. Give the picoScan150 and Pi a documented static point-to-point subnet, for example sensor `192.168.10.10/24` and Pi `192.168.10.2/24`. The exact address must be read from the delivered sensor configuration and stored in `sensor-config.json`.
2. Connect the sensor's D-coded M12 Ethernet cable directly to the Pi RJ45. Use the correct M12 cable and a strain-relieved RJ45 patch lead; the Pi connector is not a locking industrial connector.
3. Keep the LiDAR interface on its own link. Do not bridge it to Wi-Fi, the SiK radio, or the ground-control network during flight. This prevents telemetry traffic and accidental network configuration from competing with a link whose theoretical ceiling is only 100 Mb/s.
4. If a switch is needed for bench commissioning or a borrowed x86 computer, use a managed or known-good 100/1000 Mb/s switch, record its model/configuration, and validate that the selected LiDAR profile stays below the measured packet-loss limit. The switch is optional and not an airborne MVP component.

The Pi's built-in Gigabit Ethernet is faster than the sensor interface; the limiting factors are the picoScan150 100 Mb/s interface, packet-processing overhead, and storage path. A LiDAR link utilization approaching 80% of line rate is an investigation warning, not an acceptable assumption for an untested flight profile.

#### Flight-controller link

Use Pixhawk `TELEM2` for the companion computer with MAVLink `Onboard` mode. PX4 documents TELEM2 as a normal companion-computer port and recommends 921,600 baud or higher for a high-rate wired companion link. Use a verified 3.3 V UART/USB-UART interface, connect TX to RX, RX to TX, and common ground, and leave the red +5 V wire disconnected unless a specific isolated adapter and power plan explicitly requires it. [S13][S14]

The Pixhawk `TELEM1` port remains dedicated to the ground-control SiK radio in the proposed X500/S500 system. The Pi may receive a copy of selected low-rate messages through MAVLink routing, but routing is optional. If the Pi is off, the flight controller and ground-control radio must still operate independently.

### 4.3 Power and grounding topology

```text
4S LiPo, 12–16.8 V in use
 ├── flight-controller PM02/PDB branch ──► Pixhawk 6C, GPS, RC/SiK radio
 ├── fused direct/regulator-qualified branch ──► picoScan150, 9–30 V input
 └── fused 5 V/5 A buck, LC-filtered ──► Pi 5 + active cooler + SSD + CSI camera
                                      └─► optional isolated UART interface
```

- Use a star/common return near the payload power entry, with the high-current motor return kept away from the sensor Ethernet/camera/UART bundle.
- Put the picoScan150 external fuse and branch protection at the supply-cable start as required by its operating instructions. Do not assume the system plug's internal protection replaces the aircraft branch fuse. [S11]
- Use a regulator rated for the fully charged 4S input of 16.8 V, with transient margin, 5 V/5 A continuous output capability, short-circuit protection, and an enable line that the mission supervisor can observe. The 5 V/5 A figure is the Pi's recommended full-peripheral supply capability, not a measured Pi consumption. [S1][S6]
- Bond shields according to the selected cable/regulator manufacturer's instructions. Do not create a long unplanned shield-current loop through the Pixhawk or compass mount. Test Ethernet errors and camera resets with motors off and during a restrained propeller/bench electrical test performed under the course's safety procedures.
- The Pi branch must have a local voltage measurement or regulator telemetry if available. If not, use a calibrated external measurement during commissioning and log the regulator output at the acceptance test.

### 4.4 Time and camera interface

The Pi records `CLOCK_MONOTONIC_RAW` (or an equivalent monotonic source) for every packet/frame/event and periodically records a UTC/GNSS relation. The picoScan150 sensor timestamp and host receive timestamp are both retained. If the supplied sensor exposes the licensed PTP function, the Pi can act as the host time source and log PTP lock/offset. If PTP is unavailable, retain the independent clocks and estimate an offset with a moving target or visible LED test. A synchronized clock does not remove camera exposure, driver, Ethernet, or buffering latency.

The primary camera path is CSI-2. The camera service must write camera sequence number, driver timestamp, exposure/gain/white-balance settings, resolution, format, and host monotonic timestamp. The Raspberry Pi Global Shutter Camera's external trigger is an optional later timing path: Raspberry Pi documents an XTR input, a 1.8 V signal level, and a trigger-controlled frame rate. It requires careful level shifting and a measured trigger-to-exposure delay. [S8]

The initial acceptance criterion is not “PTP enabled”; it is a recorded, repeatable time mapping. The manifest must state one of:

- `timestamp_quality = hardware_trigger_calibrated`;
- `timestamp_quality = ptp_plus_driver_timestamp`;
- `timestamp_quality = software_offset_calibrated`; or
- `timestamp_quality = uncalibrated_order_only`.

Only the first three are candidates for metric RGB/LiDAR association, and each still needs its proposed error gate in Section 6.

### 4.5 Real-time versus post-flight telemetry

#### Required in real time

The Pi should monitor locally at 1–10 Hz and expose only a compact status summary to ground control:

- mission ID, state, and elapsed recording time;
- Pi input/rail voltage if measurable, CPU temperature, SSD temperature if exposed, CPU load, and process liveness;
- free storage and estimated minutes remaining;
- LiDAR link/device state, packet/segment/frame counters, incomplete-frame count, bytes/s, sensor temperature/health where available;
- camera frame rate, last sequence number, dropped-frame count, queue depth, and timestamp mode;
- FC heartbeat age, flight mode, armed/disarmed state, GNSS fix quality, and the fact that the native FC log is active;
- clock mode, PTP/NTP lock, estimated offset, and time-quality flags; and
- a concise list of quality flags and the most recent fault.

Status may be emitted as low-rate MAVLink `STATUSTEXT`/named values or a documented custom message. It must not flood the SiK radio. Raw LiDAR, images, and the full status JSON remain local.

#### Required post-flight

The following are not needed over the flight radio and must be retained locally for replay and diagnostics:

- every raw LiDAR packet and host receive time;
- every RGB frame or source video plus frame index;
- complete MAVLink byte stream and the FC native ULog/BIN copied from the flight controller;
- sensor configuration, firmware, license list, network address, camera controls, calibration IDs, and mount orientation;
- packet/frame/sequence statistics, process restarts, PTP events, temperatures, voltage, free-space samples, and power-loss recovery events;
- hashes, finalization status, and the parser/software commit used to produce normalized data.

### 4.6 Replayable survey-folder layout

The folder must be self-contained enough for a laptop to replay data without connecting to the aircraft or sensor:

```text
PW-YYYYMMDD-HHMMSS-site-route-runNN/
├── manifest.json                 # IDs, operator, time modes, software versions
├── sensor-config.json            # exported picoScan settings + config hash
├── camera-config.json            # camera mode, controls, lens/calibration ID
├── calibration.json              # intrinsics, transforms, clock offsets, dates
├── raw/
│   ├── lidar/
│   │   ├── capture-000.pcapng    # packet bytes, rotated by size/time
│   │   └── packet-index.jsonl    # mono time, wall time, offset/length, link stats
│   ├── camera/
│   │   ├── frame-00000001.jpg    # or explicitly documented source video
│   │   └── frames.jsonl          # seq, times, settings, path, checksum, flags
│   ├── flight/
│   │   ├── mavlink.bin          # raw companion-link byte stream
│   │   └── flight-controller.ulg # copied after landing when available
│   └── system/
│       └── boot.txt              # OS/kernel/service versions and boot IDs
├── normalized/
│   ├── lidar-frames.jsonl        # assembled frame/segment records
│   ├── vehicle-pose.jsonl        # parsed pose/IMU/time mapping
│   ├── health.jsonl              # periodic samples and quality flags
│   └── events.jsonl              # state transitions and operator actions
├── checksums.sha256
├── replay-summary.json
└── STOP.OK                       # present only after clean finalization
```

File naming uses a mission ID plus monotonically increasing sequence numbers, never file modification time as the sensor timestamp. A raw packet/frame file is written to a temporary name, flushed and `fsync`'d at a checkpoint, then atomically renamed. Rotation at 512 MB–2 GB is proposed so a power interruption loses at most one small tail rather than a whole session. The finalizer writes `STOP.OK` only after all queues are drained, hashes are complete, and the manifest records the final counts.

Minimum `manifest.json` fields are:

```text
mission_id, project_version, software_commit, start_utc, stop_utc,
clock_domains, timestamp_quality, sensor_serial/variant/firmware/licenses,
sensor_ip/config_hash, camera_model/lens/mode, FC model/firmware,
route/altitude/speed plan, calibration_ids, power_profile,
raw_paths, sequence_counts, drop_counts, quality_flags,
free_space_start/end, temperatures, clean_stop, replay_status
```

The replay tool must read the raw packet stream and camera index, rerun the same segment assembler and timestamp association used during acquisition, and compare counts, sequence gaps, timestamps, and checksums with the live normalized output. A ROS bag may be generated as a convenience copy later; it must not be the only artifact.

## 5. Acquisition lifecycle and diagnostics state machine

### 5.1 Startup, recording, and shutdown

**Preflight and boot:**

1. Power the payload rail and let the Pi boot. Mount the SSD read/write and verify a minimum free-space reserve; if the SSD is absent, do not silently fall back to the OS card without an operator warning.
2. Record board serial, OS/kernel, service versions, boot ID, storage UUID, regulator output, and initial temperature.
3. Bring up the isolated LiDAR interface, read the sensor identity/configuration, and hash the exported configuration. Start raw packet capture before enabling the selected measurement profile.
4. Open the camera and validate resolution, pixel format, frame interval, fixed controls, and capture timestamps. Start the FC MAVLink reader and require a valid heartbeat.
5. Start clock/health sampling. Generate a mission ID and write the manifest before the aircraft is armed.
6. Enter `READY` only when the sensor, camera, FC, storage, and time checks pass. A `READY` state with degraded timing must display that fact to the operator.

**Start of recording:**

1. Create the survey directory and record the `record_start_requested` event.
2. Start the raw LiDAR, camera, and MAVLink writers; give each a common monotonic start event and independent sequence counter.
3. Confirm one complete LiDAR frame, one camera frame, and one FC heartbeat before reporting `RECORDING`.
4. Begin periodic health records and low-rate ground status. Do not transmit raw data over the control radio.

**Normal stop:**

1. The operator requests stop after landing/disarming and confirms the aircraft is safe.
2. Stop creating new camera frames, then stop LiDAR measurement input after the last packet boundary, then stop the MAVLink reader. Continue health/finalizer workers.
3. Drain bounded queues, write final counts and quality flags, flush/`fsync` each file, generate SHA-256 hashes, and write `replay-summary.json`.
4. Write `STOP.OK` last. Only then unmount/eject the SSD or remove payload power.

**Power or communications interruption:**

- A lost SiK/GCS link must not stop local recording.
- A lost FC companion link must set `FC_LINK_LOST`; retain LiDAR/camera if the operator can safely land, but mark the survey degraded because pose/time association may be incomplete.
- A lost LiDAR Ethernet link must set `LIDAR_LINK_LOST`; do not fabricate empty scans. Camera and FC data may continue as a diagnostic record.
- A brownout or hard power loss may leave a partial packet/frame file. The next boot must preserve it, truncate only to the last valid record boundary where the format permits, mark the prior mission unclean, and never overwrite the original evidence.

### 5.2 State machine

```text
                         storage/boot failure
                  ┌──────────────────────────────┐
                  ▼                              │
BOOT ──self-test──► RECOVERY ──operator repair───┘
 │                    │
 │ all required       │ prior unclean run is
 │ services present   │ salvaged and reported
 ▼                    ▼
READY ──start──► RECORDING ──quality fault──► DEGRADED
  ▲                 │  ▲                         │
  │                 │  │ recoverable             │ continue local data
  │                 │  └─────────────────────────┘
  │                 │
  └──── finalized ◄─┴── STOPPING ◄── stop request / landing
                         │
                         ├─ flush, hash, write STOP.OK
                         └─ clean power-down
```

| State | Entry conditions | Required behavior | Exit criteria |
|---|---|---|---|
| **BOOT** | Power applied or service restarted | Mount storage, load configuration, start watchdogs, record versions and boot ID | Self-test complete, or fault sends system to `RECOVERY` |
| **READY** | Sensor identity, camera, FC heartbeat, storage, and clock checks pass | No flight data is accepted as a survey until a mission ID is created; show readiness and quality flags | Operator starts recording, or a timeout/fault returns to recovery |
| **RECORDING** | First LiDAR frame, camera frame, and FC heartbeat confirmed | Capture raw streams, normalize asynchronously, health sample, rotate files, report low-rate status | Stop request, power fault, or quality threshold sends to `STOPPING`/`DEGRADED` |
| **DEGRADED** | Timing unlock, bounded packet/frame loss, high temperature, queue pressure, FC link loss, or low storage | Continue safe local streams when possible; set persistent flags and notify GCS; never conceal gaps | Fault clears and operator accepts return to `RECORDING`, or critical condition sends to `STOPPING` |
| **STOPPING** | Operator stop, landing, storage exhaustion, or critical hardware fault | Stop in order, drain queues, hash, save counts, write `STOP.OK` only on success | Clean finalization returns to `READY`/power-down; interrupted finalization is handled by next boot `RECOVERY` |
| **RECOVERY** | Prior mission lacks `STOP.OK`, partial file, or service restart | Preserve original files, salvage parseable records, create recovery event and new report, require operator acknowledgment | Storage and services pass checks, then `READY`; unrecoverable media remains blocked |

### 5.3 Health flags and proposed thresholds

| Flag | Proposed trigger | Data-quality consequence |
|---|---|---|
| `LIDAR_PACKET_LOSS` | Any missing/out-of-order packet after parser validation | Preserve gap count and affected frame IDs; no silent interpolation in raw/normalized data |
| `LIDAR_INCOMPLETE_FRAME` | Segment timeout or incomplete frame sequence | Mark frame invalid or partial; processing decides whether it can be used |
| `CAMERA_DROP` | Sequence gap or frame interval outside the configured tolerance | Mark affected temporal association; do not duplicate a neighboring frame |
| `FC_LINK_LOST` | No heartbeat for 2 s proposed warning, 5 s proposed critical | Pose/flight-time association becomes incomplete; aircraft remains under FC/RC control |
| `PTP_UNLOCKED` / `CLOCK_DRIFT` | PTP/NTP state lost or measured offset exceeds the chosen fusion gate | Continue capture but change timestamp quality and reject metric fusion until reviewed |
| `STORAGE_LOW` | Warning below 20 GB; stop below 8 GB or 5%, whichever is larger | Finalize safely; never delete an earlier survey automatically |
| `THERMAL_WARN` | Pi 65 °C proposed; `THERMAL_CRITICAL` at 75 °C proposed | Reduce optional work/stop safely before manufacturer throttling region; values are to be tuned by test |
| `POWER_WARN` / `BROWNOUT` | Rail below the regulator acceptance band or Pi undervoltage event | Record exact interval; a reset makes the survey unclean and triggers recovery |
| `CONFIG_MISMATCH` | Sensor/camera/FC configuration hash differs from approved manifest | Require operator acknowledgment; label the run with the actual configuration |
| `UNCLEAN_PREVIOUS_RUN` | Missing `STOP.OK` at boot | Enter `RECOVERY` before accepting a new survey |

## 6. Development sequence and dependencies

### Phase A — software-only replay

1. Implement mission IDs, manifest, state machine, health schema, file rotation, and checksums using synthetic LiDAR packets and synthetic camera frames.
2. Test replay without any hardware. Include missing/out-of-order packets, incomplete segments, frame gaps, non-monotonic timestamps, and a forced process restart.
3. Keep normalized field names aligned with Investigation 02's LiDAR output and Investigation 06's fusion input. Record `survey_id`, sequence, sensor/host time, range/angle/quality, and source file offsets.

### Phase B — bench interfaces

1. Inventory the actual picoScan150 variant, system plug, firmware, licenses, IP configuration, and scan output. Record the delivered packet profile rather than assuming the example port/profile.
2. Capture sensor packets through the direct Pi Ethernet port for at least 30 minutes; run the decoder and compare live/replay counts.
3. Connect the camera, test driver and output modes, and measure per-frame sizes, sequence continuity, capture latency, and CPU/memory use.
4. Connect Pixhawk TELEM2 through the selected UART/USB interface. Verify 3.3 V levels, 921,600 baud or selected rate, heartbeat, pose/IMU subset, and no interference with TELEM1 ground control.
5. Run the Pi, SSD, camera, and LiDAR at the same time from the proposed 4S-to-5 V/payload supply. Measure input current, rail sag, Ethernet errors, camera resets, SSD temperature, and Pi temperature.

### Phase C — restrained electrical and motion tests

1. With propellers removed or under the course-approved safe test setup, operate the payload while the airframe electronics are powered. Check EMI, regulator noise, camera data integrity, sensor packet counters, UART framing, and ground-control telemetry.
2. Put the payload on a cart or vibration fixture and repeat the sustained capture. Check connector retention, file corruption, dropped frames, and timestamp continuity.
3. Perform a visible-LED/known-motion timing test for camera exposure-to-Pi time and LiDAR/FC/Pi clock offsets. Store the calibration result in the survey folder.

### Phase D — supervised flight integration

1. Fly only after the airframe team's mass/CG, battery, sensor mount, and flight-control acceptance checks pass. Item 01 must update its mass/power table with the actually selected compute/storage package.
2. Run a short flight with the camera and Pi recording but no metric claim. Confirm local capture survives telemetry link drop and operator-controlled landing.
3. Run marked pavement passes and review coverage, pose association, LiDAR profile completeness, RGB frame continuity, thermal margins, and replay before attempting change detection.

Dependencies that must be settled centrally are the final autopilot (PX4 versus ArduPilot), the exact camera, picoScan150 firmware/license/PTP availability, battery/regulator branch, onboard mount/mass limit, mission ID/coordinate-frame convention, and whether the ground radio should receive any Pi health message. Investigation 05 owns mission/ground-control behavior; Investigation 03 owns camera timing and calibration; Investigation 02 owns sensor packet/profile details; Investigation 06 owns the normalized fusion contract.

## 7. Verification tests and proposed success measures

All gates below are **proposed initial acceptance criteria**, not current results.

| Test | Method | Pass gate |
|---|---|---|
| Software replay determinism | Feed a captured/synthetic packet set into the live and offline decoder; compare frame IDs, beam counts, timestamps, and error flags | Same valid/invalid counts and same sequence-gap report; no parser accepts a corrupted packet silently |
| Sustained simultaneous capture | Run the exact sensor profile, RGB mode, FC stream, health logger, and selected storage for 30 minutes on the bench | At least 35 MB/s measured sustained write capacity or a lower documented profile; zero unexplained storage/write errors; all counters and stop marker present; no Pi thermal throttling |
| LiDAR packet/segment loss | Use a controlled network impairment or disconnect/reconnect test; compare packet sequence and frame assembly | Every missing/out-of-order packet is counted and flagged; no fabricated samples appear in raw or normalized output; service recovers without process restart when link returns |
| RGB frame loss | Apply a controlled camera restart or load spike; compare frame sequence and index | Every missing frame is counted; subsequent frames retain monotonic IDs/timestamps; `CAMERA_DROP` is persistent in the manifest |
| Timestamp continuity | Run stationary 15–30 minutes, then a moving LED/edge test; inspect all clock domains | No backward timestamps; sequence-to-time gaps are reported; measured camera/LiDAR/FC mapping is stable enough for the selected fusion gate or run is explicitly marked software-only |
| Storage exhaustion | Fill the survey volume past the warning threshold using a test partition/file quota | Warning reaches ground status; recording stops/finalizes before reserved space is destroyed; existing files replay; no automatic deletion |
| Graceful shutdown | Stop from the mission service after a live run; then remove power only after `STOP.OK` | All workers stop in order, hashes and counts are written, `STOP.OK` is last, and replay summary matches the live counters |
| Brownout/power interruption recovery | Use a current-limited bench supply or controlled switch, never an airborne battery experiment; interrupt power during writes | Next boot enters `RECOVERY`, preserves partial files, salvages valid records, reports the unclean interval, and creates no misleading complete survey |
| CPU/memory/thermal | Capture at the design point with active cooling and ventilated enclosure for 30 minutes; record `vcgencmd`/Linux temperature, memory, queue depth, and CPU load | No OOM, queue runaway, camera reset, storage error, or thermal throttling; tune thresholds below the Pi's 80–85 °C throttling region. [S6][S7] |
| Link isolation | Run LiDAR direct link, TELEM2 MAVLink, TELEM1 radio, and camera simultaneously | No LiDAR packet loss caused by telemetry traffic; FC remains controllable with Pi powered down; status remains low-rate |
| Replay after removal | Unmount the SSD and replay the survey on the ground laptop with no live devices | Manifest, checksums, raw packet decoder, frame index, FC log, and normalized products are sufficient to reproduce the survey summary |

Additional proposed gates before a metric flight are:

- at least 20 GB free at mission start and an estimated capacity exceeding the planned route by 2x;
- no unexplained camera frame gaps in a 10-minute stationary run;
- no unexplained LiDAR packet gaps in a 30-minute wired run at the selected profile;
- no Pi undervoltage events and no storage remount/read-only transition;
- the measured payload mass and CG are entered in the aircraft log; and
- a clean recovery is demonstrated after one intentional power interruption.

## 8. Cost, mass, power, and thermal implications

### 8.1 Power budget

The Pi 5 manufacturer requirement is a 5 V/5 A supply capability for full peripheral operation. That is a regulator-sizing ceiling, not a claim that the recorder continuously consumes 25 W. The preliminary engineering allowance for the actual capture package is:

| Load | Average planning allowance | Design/worst-case allowance | Status |
|---|---:|---:|---|
| Pi 5 headless capture, camera pipeline, OS | 8–12 W | 25 W rail capability | Estimated/proposed; measure with selected modes |
| USB SSD | 1–3 W | 5 W | Estimated; model-specific |
| Active cooler and small auxiliaries | 0.3–1 W | 1.5 W | Estimated; measure fan/rail current |
| **Pi payload branch** | **approximately 10–15 W** | **25 W at 5 V** | Proposed design allowance |
| picoScan150 | 4.5 W typical | 17 W documented upper configuration | Manufacturer-stated; exact system plug/options unresolved |
| **Compute + sensor electronics** | **approximately 15–20 W** | **approximately 42 W** | Does not include propulsion, FC, GPS, or radio |

At 14.8 V nominal, a 15–20 W payload electronics load is approximately 1.0–1.35 A before regulator losses. A 42 W design allowance is approximately 2.84 A before wiring/regulator losses. With a 4S 5 Ah nominal 74 Wh battery, 15 minutes of the average 20 W electronics allowance uses approximately 5 Wh; the aircraft's propulsion load and reserve dominate endurance. These are energy calculations, not flight-time predictions. The airframe team must measure total current with the final payload and maintain its flight reserve.

The 5 V branch should be rated at 5 A even if the first test consumes less, because the Pi documentation limits peripherals when only a 5 V/3 A supply is available. The picoScan150 branch should tolerate its specified supply range and be fused separately. [S1][S6][S11]

### 8.2 Mass and mechanical implications

The preferred Pi/SSD/enclosure/regulator/cable package is allowed **230–370 g** until measured. A microSD-only, lightly protected package may be approximately 120–200 g, but storage reliability must decide whether that weight saving is acceptable. The allowance includes the Pi board, cooler, SSD, buck, UART/camera/Ethernet cables, strain relief, vibration isolation, and enclosure; it does not include the picoScan150, its system plug, the RGB camera, or the aircraft battery.

This allowance is larger than the earlier very small Pi-only placeholder in Investigation 01. Investigation 01 must update the aircraft mass and CG budget after the actual storage and enclosure are selected. Do not add ballast to conceal a mass discrepancy. Mount the computer close to the airframe center, isolate it from the LiDAR's rigid optical mount, and leave airflow around the cooler. Secure the SSD and all cables independently of their connectors.

### 8.3 Thermal and environmental implications

The Pi 5 is specified for 0–70 °C and Raspberry Pi recommends active cooling for sustained load. Its documented thermal management begins reducing performance as the processor approaches 80 °C and reaches the hard throttle region at 85 °C. Set a proposed warning at 65 °C and a critical/stop policy near 75 °C, then tune after a representative test. A closed foam box or sealed printed enclosure can invalidate the thermal design even when the outside air is cool. [S1][S6][S7]

The enclosure should be ventilated through a downward/splash-protected path, use a mesh or filter that can be inspected, and shield the SSD and Pi from direct prop wash, dust, and loose fasteners. No water ingress, rain, condensation, or direct sunlight performance is assumed. The SICK sensor's more robust environmental rating does not transfer to the Pi, SSD, regulator, or camera. [S11]

## 9. Risks, open decisions, and fallback

### Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Actual LiDAR packet rate approaches 100 Mb/s ceiling | Packet loss or incomplete profiles | Start with lower profile, measure bytes/second, use direct link, preserve raw counters, reduce echo/window/frequency if needed |
| JPEG output is larger or slower than assumed | Storage exhaustion or frame drops | Measure frame-size distribution; reduce fps/resolution only with a documented mission mode; use SSD; retain frame gaps |
| CSI camera driver does not expose required timestamps | RGB/LiDAR association uncertainty | Use Pi Global Shutter Camera with documented trigger path, or a borrowed UVC/global-shutter camera; calibrate software offset and label quality |
| microSD write performance/endurance is inadequate | Corrupted or dropped survey data | Preferred 256 GB USB 3 SSD; microSD only after actual workload test; keep OS and data separation |
| Pi thermal throttling in enclosure | Timing and capture instability | Active cooler, airflow, temperature logging, early warning, no edge inference in MVP |
| USB/UART/Ethernet connector disconnects in vibration | Missing stream or computer reset | Strain relief, short cables, locking/retention hardware, restrained vibration test, independent service flags |
| Payload power transient resets Pi | Unclean survey and missing data | Separate 5 V/5 A buck, LC/filter/fuse, brownout test, local voltage log, do not share Pixhawk accessory 5 V |
| Time-sync license/PTP unavailable | Misregistered RGB/LiDAR data | Store all clock domains, use measured LED/motion offset, mark software-only runs, keep processing uncertainty |
| FC link loss or wrong port/voltage | Missing pose and possible hardware damage | Use PX4 port map, verified 3.3 V adapter, TX/RX/GND test, TELEM1 remains independent, no flight without heartbeat test |
| Raw local data cannot be recovered after a power loss | Irrecoverable flight evidence | Rotated files, journaled filesystem, frequent checkpoints, recovery state, `STOP.OK`, replay test |
| Jetson is introduced too early | Budget, mass, thermal, and software scope expands | Laptop/Pi post-flight processing is the initial path; Jetson is borrowed/later only after profiling proves need |

### Open decisions to settle centrally

1. Is the final flight stack PX4 or ArduPilot? The proposed port names, message rates, native log format, and ground-control configuration depend on this.
2. Which exact RGB camera will be delivered or purchased? The Pi CSI cable, driver, trigger, timestamp, lens, and JPEG/RAW modes depend on it.
3. What picoScan150 variant, system plug, firmware, licenses, and PTP/IMU features will the challenge shipment contain?
4. Is the final payload regulator isolated or common-ground, and where is its input fuse placed relative to the flight PDB?
5. Is the aircraft allowed to carry the 230–340 g preferred compute/storage package, or must the team accept the microSD fallback after storage testing?
6. What health message can be added to the existing MAVLink/ground-control link without changing safety-critical FC behavior?
7. What timing error and pose gap are acceptable to Investigation 06 for geometric change detection and RGB-assisted defect analysis?
8. Are the first surveys 10–15 minutes or will the team require a 30-minute single-session target? This sets the final storage size and reserve policy.

### Fallback matrix

| Missing/failed item | Fallback that still produces a credible demonstration |
|---|---|
| Pi 5 unavailable | Borrow Pi 4 Model B with the same direct Ethernet/CSI/MAVLink capture service; lower the validated profile if CPU or thermal tests require it |
| Any Pi unavailable | Borrow a Linux laptop/NUC for LiDAR/MAVLink bench acquisition and use a separate camera recorder; label the result as a split, software-synchronization demonstration until timing is calibrated |
| SSD unavailable | High-endurance microSD only after a 30-minute write/replay test; cap session duration and keep 20% free space |
| Arducam CSI driver unavailable | Raspberry Pi Global Shutter Camera with official CSI path and tested XTR trigger, or a borrowed UVC global-shutter camera on USB 3 |
| PTP unavailable/licensed out | Sensor timestamps plus Pi monotonic/host receive time, FC MAVLink time, and measured motion/LED offset; mark `software_offset_calibrated` or `uncalibrated_order_only` |
| Onboard inference too slow | Transfer the replayable folder to a laptop and run all processing offline; the application demonstration remains valid as a capture-and-replay system |
| Jetson unavailable | No change to MVP; do not make CUDA/TensorRT an acquisition dependency |

## 10. Sources

The URLs below are direct manufacturer or project documentation links. **Accessed 2026-09-19.**

1. **Raspberry Pi 5 product brief**, Raspberry Pi Ltd. Current list prices, interfaces, operating temperature, and production life: [https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-4-raspberry-pi-5-product-brief.pdf](https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-4-raspberry-pi-5-product-brief.pdf). Accessed 2026-09-19.
2. **Raspberry Pi 4 Model B product brief**, Raspberry Pi Ltd. Interfaces, 5 V/3 A input, operating temperature, and current list prices: [https://pip-assets.raspberrypi.com/categories/545-raspberry-pi-4-model-b/documents/RP-008344-DS-1-raspberry-pi-4-product-brief](https://pip-assets.raspberrypi.com/categories/545-raspberry-pi-4-model-b/documents/RP-008344-DS-1-raspberry-pi-4-product-brief). Accessed 2026-09-19.
3. **Jetson Orin Nano Developer Kit User Guide**, NVIDIA. Current platform highlights, 7–25 W power range, JetPack support: [https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/). Accessed 2026-09-19.
4. **Jetson FAQ**, NVIDIA. Current FAQ price and developer-kit limitations: [https://developer.nvidia.com/embedded/faq](https://developer.nvidia.com/embedded/faq). Accessed 2026-09-19.
5. **Jetson Orin Nano Developer Kit gets a “Super” boost**, NVIDIA Developer Blog. Earlier official launch price and performance announcement; included because it conflicts with the current FAQ price: [https://developer.nvidia.com/blog/?p=93942](https://developer.nvidia.com/blog/?p=93942). Accessed 2026-09-19.
6. **Getting started / power and networking**, Raspberry Pi Documentation. Boot media, Pi 5 5 V/5 A, Pi 4 5 V/3 A, Gigabit Ethernet: [https://www.raspberrypi.com/documentation/computers/getting-started.html](https://www.raspberrypi.com/documentation/computers/getting-started.html). Accessed 2026-09-19.
7. **Raspberry Pi hardware and thermal management**, Raspberry Pi Documentation. Pi 5 active cooling, throttling behavior, and fan control: [https://www.raspberrypi.com/documentation/hardware/displays/raspberry-pi-5.html](https://www.raspberrypi.com/documentation/hardware/displays/raspberry-pi-5.html). Accessed 2026-09-19.
8. **Camera documentation**, Raspberry Pi. CSI connector compatibility, Pi 5 22-pin connector, global-shutter camera interfaces and trigger documentation: [https://www.raspberrypi.com/documentation/accessories/camera.html](https://www.raspberrypi.com/documentation/accessories/camera.html). Accessed 2026-09-19.
9. **Raspberry Pi Global Shutter Camera product page**, Raspberry Pi Ltd. Sensor, RAW10 output, mass, resolution, and CSI compatibility: [https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/](https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/). Accessed 2026-09-19.
10. **Install Ubuntu on Raspberry Pi**, Canonical hardware support. Supported Pi models and Ubuntu 24.04 images: [https://ubuntu.com/hardware/docs/boards/how-to/ubuntu_supported/raspberry-pi/](https://ubuntu.com/hardware/docs/boards/how-to/ubuntu_supported/raspberry-pi/). Accessed 2026-09-19.
11. **picoScan150 operating instructions**, SICK. Sensor supply, power, mass, environmental limits, Ethernet interface, output data, and timing interfaces: [https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf). Accessed 2026-09-19.
12. **ULog file format**, PX4. Self-describing log structure and timestamp behavior: [https://docs.px4.io/v1.12/en/dev_log/ulog_file_format](https://docs.px4.io/v1.12/en/dev_log/ulog_file_format). Accessed 2026-09-19.
13. **Serial port configuration**, PX4. Companion-computer port assignments and TELEM2 defaults: [https://docs.px4.io/main/en/peripherals/serial_configuration](https://docs.px4.io/main/en/peripherals/serial_configuration). Accessed 2026-09-19.
14. **Raspberry Pi Companion with Pixhawk**, PX4. TELEM2 wiring, 3.3 V signals, MAVLink, and separate companion power warning: [https://docs.px4.io/v1.14/en/companion_computer/pixhawk_rpi](https://docs.px4.io/v1.14/en/companion_computer/pixhawk_rpi). Accessed 2026-09-19.
15. **MAVLink telemetry radios**, PX4. Ground-control telemetry role and SiK radio interface: [https://docs.px4.io/v1.14/en/data_links/telemetry](https://docs.px4.io/v1.14/en/data_links/telemetry). Accessed 2026-09-19.
16. **Investigation 02: picoScan150 sensing and acquisition**, repository reference. Proposed 10 MB/s capture target, Compact UDP, segmentation, and raw replay layout: [../02-picoscan150-sensing-acquisition/findings.md](../02-picoscan150-sensing-acquisition/findings.md). Accessed 2026-09-19.
17. **Investigation 03: RGB imaging, positioning, and synchronization**, repository reference. Proposed Arducam global-shutter camera, timing strategy, and trigger fallback: [../03-rgb-positioning-synchronization/findings.md](../03-rgb-positioning-synchronization/findings.md). Accessed 2026-09-19.
18. **Jetson Orin Nano Developer Kit carrier-board specification**, NVIDIA. Gigabit Ethernet, USB, camera, and storage interfaces: [https://developer.nvidia.com/downloads/assets/embedded/secure/jetson/orin_nano/docs/jetson_orin_nano_devkit_carrier_board_specification_sp.pdf](https://developer.nvidia.com/downloads/assets/embedded/secure/jetson/orin_nano/docs/jetson_orin_nano_devkit_carrier_board_specification_sp.pdf). Accessed 2026-09-19.
19. **Jetson Orin Nano Developer Kit quick start**, NVIDIA. Current microSD/NVMe installation and power/thermal setup path: [https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/quick_start.html](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/quick_start.html). Accessed 2026-09-19.
