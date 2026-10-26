# Investigation 02: picoScan150 sensing and acquisition

**Status:** concept-stage recommendation; no project hardware has been received or measured.
**Research checked:** 2026-09-19
**Scope:** SICK picoScan150 only.  Public pages that say “picoScan100” are treated as naming/copy ambiguity unless the page explicitly identifies the device as picoScan150.

## 1. Scope and recommendation

Use the picoScan150 as a rigidly mounted, across-track 2D profile sensor.  Mount the scan plane approximately vertical and perpendicular to the UAV ground track, with the useful portion of the scan looking downward across the pavement.  UAV motion then supplies the along-track dimension.  The LiDAR output is the geometric channel for coarse-to-moderate elevation change; an RGB camera is the visual channel for cracks, joints, staining, texture, and other appearance-only evidence.

The minimum viable acquisition should be independent of ROS:

1. Configure the sensor through SOPASair or the REST API.
2. Stream SICK Compact measurement data over Ethernet UDP to an onboard computer.
3. Capture the raw packets and host receive timestamps, assemble scan segments into complete frames, and retain the sensor timestamps, frame/segment sequence numbers, range, RSSI, echo, and optional IMU data.
4. Record camera, autopilot pose, health, and configuration metadata beside the raw stream.
5. Replay the raw capture offline through the same parser used in flight.

Start at **5–8 m above the pavement**, **±30° from nadir in the cross-track scan plane**, and **15 Hz / 0.33°**.  These are proposed starting values, not SICK performance claims.  They are conservative because the challenge page does not identify whether the supplied unit will be Core, Prime, or Pro, and because a 10 m altitude at ±30° already produces an approximately 11.5 m slant range.  After the actual variant, licenses, firmware, surface reflectivity, and bench results are known, test 25 Hz / 0.25° or a higher-resolution profile where the unit supports it.

The project must not claim that one stationary 2D scan is a complete pavement surface model, that the picoScan150 alone measures fine crack width, or that a single range profile identifies every visual defect.  A stationary scan is one cross-section.  A 3D surface representation requires motion plus sufficiently accurate pose/time registration, and fine cracks require RGB or another close-range imaging method.

## 2. Evidence, naming ambiguity, and assumptions

### 2.1 Naming ambiguity

The current SICK challenge page says selected teams receive a **picoScan150**, lists picoScan150 at-a-glance values, and links picoScan150 resources.  However, the same page contains an “about the picoScan100” heading while the paragraph immediately below repeats picoScan150 language and specifications.  SICK support articles also sometimes retain a “picoScan100” article title or related-product tag while the body explicitly says “picoScan150.”  This appears to be copied product-family web content, not evidence that the challenge sensor is a picoScan100.

This brief therefore uses the picoScan150 Operating Instructions (8028323), the picoScan150-specific support articles, and the SICK challenge page’s explicit picoScan150 statements.  It does not use a picoScan100 datasheet to fill a missing picoScan150 value.  When the sensor arrives, record the type label, part number, serial number, firmware, variant, installed licenses, and exported parameter set before commissioning.

### 2.2 Verified picoScan150 facts

Values below are manufacturer-published facts.  “Typical,” “up to,” and variant qualifiers retain SICK’s wording; they are not project guarantees.

| Topic | Verified picoScan150 fact | Design consequence | Source |
|---|---|---|---|
| Sensor type | 2D LiDAR using the HDDM+ statistical measurement procedure; 905 nm infrared, laser class 1; indoor/outdoor application | It measures ranges in a scan plane, not a native volumetric image | [SICK picoScan150 Operating Instructions, §11.1, pp. 61–69](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Scan aperture | Horizontal aperture angle is 276° | The full aperture is not all usable ground coverage in a downward UAV mounting; use an angle window after verifying sensor coordinates | [Operating Instructions, §11.1](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Frequency and angular resolution | Core: 15 or 25 Hz; Prime: 15, 20, or 40 Hz; Pro: 15–50 Hz.  Core: 0.33°, 0.25°, or 1°; Prime: 0.10°, 0.25°, 0.33°, or 1°; Pro: 0.05°–1°.  Exact combinations depend on the Dynamic Sensing Profile | The actual type/profile must be identified before quoting a resolution or point rate | [Operating Instructions, §11.1](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Working range and blind zone | Core: 0.05–25 m; Prime: 0.05–60 m; Pro: 0.05–120 m.  Blind zone: 0–0.05 m | A challenge unit must not be assumed to be Pro.  The blind zone is irrelevant at normal UAV altitude but matters for close bench tests | [Operating Instructions, §11.1](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Typical dark-target scanning range | At 10% remission, >99% detection probability, and 10 klx: Core typ. 12 m; Prime typ. 25 m; Pro typ. 40 m | At oblique angles, slant range grows.  Altitude and usable angle must be chosen against the installed variant and road reflectivity | [Operating Instructions, §11.1](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Typical high-remission scanning range | At 90% remission, >99% detection probability, and 10 klx: Core typ. 25 m; Prime typ. 47 m; Pro typ. 75 m | These are test conditions and typical values, not a guaranteed detection envelope for wet or angled pavement | [Operating Instructions, §11.1](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Spot size and divergence | Spot size listed as 8 mm at the optics cover, 32 mm at 5 m, 55 mm at 10 m, 126 mm at 25 m, and 244 mm at 50 m for Prime/Pro; typical divergence 0.27° / 4.8 mrad, maximum 0.3° / 5.3 mrad | Angular sample spacing finer than the spot does not mean independent fine spatial resolution; do not infer crack-width capability from 0.05° alone | [Operating Instructions, §11.1](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Echo behavior | Three echoes are evaluated; output can be first echo, last echo, or all echoes.  Minimum distance between echoes is 0.5 m | Capture all echoes during characterization; choose a road-surface echo only after testing dust, rain, vegetation, and multipath conditions | [Operating Instructions, §11.1](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Published error values | Systematic error typ. ±20 mm, maximum ±30 mm; statistical error ≤2 mm from 0.05–5 m and ≤16 mm from 5–60 m in the listed conditions; temperature drift typ. ±0.5 mm/K | These values bound expectations but do not validate the UAV installation, pose error, incidence angle, or pavement result.  Bench calibration and repeatability are required | [Operating Instructions, performance data, pp. 63 and 69](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Output segmentation | A 276° scan is output in segments: 30° at ≤25 Hz and 60° at ≥30 Hz.  Examples in the manual are 10 segments at 25 Hz and 5 at 40 Hz | The receiver must group segments by frame sequence, not treat each UDP packet as a complete profile | [Operating Instructions, §3.5.8.2, p. 24](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Ethernet/data formats | Ethernet supports 10/100 Mbit/s half/full duplex; UDP singlecast or multicast with Compact (recommended by SICK) or MSGPACK; TCP/IP LMDscandata; native ROS2 DDS | Use a direct Ethernet link or isolated switch and Compact UDP as the primary raw acquisition path; keep LMDscandata/ROS optional | [Operating Instructions, interface data, p. 69](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Measurement content | SICK lists distance, RSSI, timestamp, and reflector mark in the Ethernet measurement output; Compact and MSGPACK contain timestamps and serial number | Preserve sensor time and host receive time; RSSI is useful as a quality/context field, not a direct material classifier | [Operating Instructions, §3.5.8 and interface data](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Configuration interfaces | SOPASair web server, SOPAS ET, REST API, and CoLa A/B are listed | The system can be commissioned without ROS; configuration should be exported and hashed with each survey | [Operating Instructions, interface data, p. 69](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Time synchronization | Ethernet interface lists NTP and PTP.  SICK’s license page lists a picoScan time-sync PTP add-on; availability on the supplied unit must be checked | Prefer PTP when the license and host support it; otherwise use NTP/common host time plus measured software offset | [Operating Instructions, §3.5.15 and interface data](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf); [SICK picoScan150 licenses](https://support.sick.com/sick-knowledgebase/article/?code=KA-10714) |
| IMU | The technical data lists a Bosch BHI160B 3-axis gyroscope/3-axis accelerometer at 100 Hz, with a defined position relative to the optical origin | The integrated IMU is an available sensor capability only if the unit/license exposes it; it does not replace UAV position or survey registration | [Operating Instructions, interface data, p. 69](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf); [SICK IMU license entry](https://support.sick.com/sick-knowledgebase/article/?code=KA-10714) |
| Power and mass | Supply 9–30 V DC, reverse-polarity protected; typical power 4.5 W; maximum 17 W with loaded digital outputs depending on system plug.  Mass 220 g without system plug; dimensions 60 × 60 × 82 mm | Size the regulator and battery for the sensor, Ethernet computer, camera, startup/transient margin, and cabling; include the system plug in the payload mass budget when known | [Operating Instructions, mechanics/electronics and dimensions](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Environmental limits | Operating temperature −33 to +50 °C; storage −40 to +70 °C; indirect ambient-light immunity 100 klx; IP65/IP67 protection depends on the connected system plug; operation humidity max. 80% RH non-condensing | Dry-weather MVP flights and an optics contamination/temperature record are appropriate.  IP rating does not make wet pavement or direct sun measurement invariant | [Operating Instructions, environmental data](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf); [SICK outdoor application guidance](https://support.sick.com/sick-knowledgebase/article/?code=KA-09881) |
| Ethernet connector | The operating instructions show a 4-pin D-coded M12 Ethernet connector: 1 TX+, 2 RX+, 3 TX−, 4 RX− | The flight harness needs the correct rugged M12 cable, strain relief, and a computer/switch with a 10/100 Ethernet interface | [Operating Instructions, Ethernet pin assignment](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf) |
| Driver ecosystem | SICK lists ROS1, ROS2, C++, and Python drivers.  Native ROS2 requires a picoScan150 RosConnect license and firmware ≥V2.2.1 in SICK’s tutorial | Treat native ROS2 as an optional integration, not an acquisition dependency; raw Compact UDP remains the fallback | [Operating Instructions, driver list](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf); [SICK native ROS2 tutorial](https://support.sick.com/sick-knowledgebase/article/?code=KA-09438); [SICKAG sick_scan_xd](https://github.com/SICKAG/sick_scan_xd) |

### 2.3 Research and project assumptions

- The challenge-selected sensor has not been received.  Variant, part number, licenses, firmware, system plug, default configuration, and accessories are unresolved.
- The scan plane will be mounted perpendicular to the nominal ground track.  This is a proposed geometry for a UAV profile survey, not a SICK-recommended installation for this project.
- PaveWatch will initially fly supervised, low-speed, dry-weather test missions over a permitted paved area.  Outdoor rain, dust, low sun, wet pavement, vegetation, and multiple-LiDAR interference are risk conditions to characterize later.
- Ground speed, altitude, roll, pitch, and yaw will come from the flight stack or another position/attitude source.  The picoScan150’s 2D scan and optional IMU are not by themselves a complete georeferencing solution.
- The calculations below use a flat horizontal plane and ideal ray geometry.  They are planning calculations, not field validation or accuracy claims.

## 3. Proposed components, sensing concept, and operating parameters

### 3.1 Labeled input/output/data flow

```text
Paved surface
   │ range, echo, RSSI, reflector flag
   ▼
picoScan150 2D scan plane ── Ethernet UDP Compact ──► onboard capture service
   │ optional IMU / encoder / device status                         │
   │                                                                 ├─ raw .pcapng
   │                                                                 ├─ parsed profiles + quality fields
   │                                                                 └─ health/config log
   ▼                                                                 │
Rigid sensor-to-body transform                                      │
   + UAV pose, altitude, ground speed, GNSS/INS timestamps ──────────┤
                                                                     │
RGB camera ── images + exposure/frame timestamps ────────────────────┤
                                                                     ▼
                    offline replay and fusion pipeline
              ┌──────────────────┬───────────────────┬──────────────┐
              │ registered 2D    │ coarse elevation   │ RGB-assisted │
              │ profiles / point │ change / coverage │ defect cues  │
              │ samples           │ evidence          │ and report   │
              └──────────────────┴───────────────────┴──────────────┘
```

The receiver must preserve a distinction between:

- **sensor measurements:** range, angle, echo, RSSI, reflector flag, sensor timestamp;
- **sensor state:** device status, temperature, contamination, configuration, packet counters;
- **vehicle state:** position, attitude, altitude, velocity, flight mode, autopilot time;
- **RGB evidence:** image pixels, camera timestamp, exposure, intrinsics, camera-to-body transform; and
- **derived results:** registered profiles, elevation differences, anomaly classes, confidence, and coverage masks.

### 3.2 Proposed operating parameters (unverified until bench tested)

| Parameter | Proposed starting value | Why / test gate |
|---|---:|---|
| Installed variant | Read and log Core/Prime/Pro from type label and configuration | Do not use the Pro range or 0.05° resolution unless the received unit supports it |
| Scan-plane orientation | Vertical plane, approximately perpendicular to flight direction, optical axis aimed at nadir | Gives a cross-track surface profile while translation creates along-track samples; verify with a level/flat-plane fixture |
| Usable scan window | ±30° from nadir, 60° total | Limits incidence angle and slant range; verify angle sign/zero in SICK coordinates before configuring a filter |
| Altitude | 5–8 m AGL for MVP | At ±30°, slant range is 1.155× altitude: 5.8–9.2 m.  This leaves more margin for a Core unit’s typical 12 m, 10% remission range than a 10–15 m start |
| Ground speed | 1–2 m/s bench/cart equivalent; do not exceed 5 m/s until motion tests pass | Along-track spacing is speed/frequency; lower speed helps registration and avoids overclaiming coverage |
| Baseline frequency/resolution | 15 Hz / 0.33° | Listed for all variants and suitable for first packet/replay tests; not the best possible geometry setting |
| Upgrade profile | Test 25 Hz / 0.25° where supported; test Prime/Pro profiles separately | Finer angular spacing does not remove spot size, range error, or pose error |
| Echo output | Capture all echoes during bench characterization; select first/last/all in the road pipeline only after comparison | Manufacturer supports up to three echoes, but the best echo depends on rain, dust, vegetation, and pavement |
| Data format | Compact UDP unicast to the onboard computer | Lower overhead than MSGPACK according to SICK; raw packet capture remains replayable |
| Time base | PTP if the add-on/license and host support are confirmed; otherwise NTP plus host monotonic timestamps | Measure camera/LiDAR/pose offset on a moving target; do not assume network synchronization equals geometric synchronization |
| Quality filtering | Start with raw range/RSSI and record filter settings; evaluate moving-average, particle, fog, angle, distance, and echo filters separately | Filtering can remove real edge/step evidence or add delay; retain an unfiltered reference during validation |
| Data window | Record the full sensor stream at first; optionally angle-filter to ±30° after parser validation | A full capture makes later coordinate/angle decisions possible, subject to storage bandwidth |
| Camera relation | Rigid camera mount, calibrated intrinsics and camera-to-LiDAR transform; use common time base or measured offset | Proposed RGB/LiDAR fusion requirement, not a picoScan150 fact |

### 3.3 Coverage and sampling calculation

For planning, let (H) be the optical origin height above a flat surface, (eta) the usable cross-track angle from nadir, (f) the scan frequency, (v) the ground speed, and (Delta	heta) the angular resolution in radians:

```text
cross-track half-width       x = H tan(β)
full ground width             W = 2 H tan(β)
slant range at the edge       r = H / cos(β)
cross-track sample spacing    Δx ≈ H sec²(β) Δθ
along-track profile spacing   Δy = v / f
```

For the proposed ±30° window, (W=1.155H), (r=1.155H), and the edge sample spacing is 1.333 times the nadir spacing.  The following is a geometry sweep, not a measurement result.

| Altitude (H) | Ground width at ±30° | Edge slant range | 0.33° spacing at nadir / edge | 0.05° spacing at nadir / edge |
|---:|---:|---:|---:|---:|
| 5 m | 5.77 m | 5.77 m | 28.8 / 38.4 mm | 4.36 / 5.82 mm |
| 8 m | 9.24 m | 9.24 m | 46.1 / 61.4 mm | 6.98 / 9.31 mm |
| 10 m | 11.55 m | 11.55 m | 57.6 / 76.8 mm | 8.73 / 11.64 mm |
| 15 m | 17.32 m | 17.32 m | 86.4 / 115.2 mm | 13.09 / 17.45 mm |

The 0.05° column is available only on appropriate Pro profiles; it is not a project assumption.  Even where the angular step is a few millimeters, SICK lists a 32 mm spot at 5 m and 55 mm at 10 m, plus typical systematic and statistical errors.  Therefore the table describes sample spacing, not crack-width resolution.

Along-track spacing for a single cross-track profile is:

| Ground speed | 15 Hz | 25 Hz | 50 Hz |
|---:|---:|---:|---:|
| 1 m/s | 66.7 mm | 40 mm | 20 mm |
| 2 m/s | 133 mm | 80 mm | 40 mm |
| 5 m/s | 333 mm | 200 mm | 100 mm |

At the proposed 5–8 m and 1–2 m/s MVP, a 15 Hz profile samples roughly every 67–133 mm along track and 29–61 mm across track at 0.33°.  This is appropriate for evaluating coarse heave, settlement, rutting, edge drop, and pothole-like geometry; it is not evidence that narrow cracks will be resolved.

Coverage and error cautions:

- A beam at a larger (eta) travels farther and meets a flat surface at a more oblique incidence.  Range error projects into a larger surface-normal error as incidence becomes grazing; keep the MVP window away from ±90°.
- A rigid-body attitude error creates a false slope.  For example, at (H=10) m and (eta=30°), the edge is about 5.77 m from nadir; an unmodeled 1° tilt produces approximately (5.77	an(1°)approx101) mm of apparent cross-track height change.  This is a planning calculation illustrating why scan-plane orientation and repeat alignment matter.
- Road texture, aggregate, wet/specular patches, black surfaces, dust, rain, vegetation, optical contamination, direct/low sun, and UAV shadow can change return quality.  SICK’s outdoor guidance specifically identifies rain, snow, moisture, dust, vegetation, and direct sunlight as conditions requiring countermeasures or testing.
- The full 276° aperture does not equal a 276° pavement swath in this mounting.  Rays above the local horizon do not intersect the pavement in the same cross-track profile, and UAV structure can occlude part of the aperture.

## 4. Ethernet acquisition, timestamps, and replay

### 4.1 Commissioning path

1. On a bench, connect the sensor through the correct M12 power and D-coded Ethernet cables.  Use a regulated 9–30 V DC source with current/transient margin and an external fuse consistent with the operating instructions.
2. Put the acquisition computer on an isolated Ethernet link.  Discover or assign the sensor IP using SOPASair/SOPAS ET or the documented REST/CoLa interfaces.  Record IP, MAC, serial number, part number, firmware, license list, and current configuration.
3. Configure the scan profile and angle/range filters only after the raw output has been captured once.  Set the measurement-data destination to the host address and enable Compact UDP.  The default/selected UDP port must be recorded from the actual configuration; SICK examples use port 2115, but the project must not silently assume that a received unit has the factory value.
4. Enable optional IMU or encoder streams only if the installed license and application expose them.  Record their destination ports and sequence/timestamp relationship.
5. Synchronize the sensor and host with PTP if available.  If PTP is unavailable, configure NTP or a common host time source and store both sensor and host receive times.  A software offset/latency calibration is mandatory before RGB fusion.
6. Start the raw capture before enabling measurement data.  Log packet arrival, source/destination, length, checksum/parse result, frame sequence, segment index, and drop/out-of-order counts.
7. Poll or subscribe to health data at a slower rate: device state, temperature, contamination, current configuration hash, network state, and capture counters.  A health record is part of the survey, not an afterthought.

SICK’s current support material documents REST endpoints for scan configuration, scan-data Ethernet settings, data format, time, mounting pose, device status, temperature, and contamination.  REST writes require the device’s authorization/challenge flow and do not replace retaining a human-readable commissioning record.

### 4.2 Raw and normalized recording layout

Recommended minimum survey folder:

```text
survey-YYYYMMDD-HHMMSS/
  manifest.json                 # survey ID, operator, firmware, licenses, variant
  sensor-config.json            # exported settings + SHA-256/hash + angle convention
  capture.pcapng                # raw Ethernet packets, primary replay artifact
  lidar_frames.jsonl            # normalized complete-frame index and decoded fields
  lidar_measurements/           # binary/columnar ranges, angles, RSSI, echo, flags
  imu.jsonl                     # if enabled; sensor timestamps and sequence links
  vehicle_pose.jsonl            # autopilot/GNSS/INS pose, frame, timestamp, quality
  camera/                       # images/video plus frame timestamp index
  health.jsonl                  # status, temperature, contamination, packet counters
  calibration.json              # transforms, range bias, time offset, reference markers
  replay_checksums.json         # hashes and parser/version used
```

The normalized LiDAR record should contain at least:

```text
survey_id, sensor_serial, firmware, frame_sequence, segment_index,
sensor_time, host_rx_time, beam_index, angle_rad, echo_index,
range_m, rssi, reflector_flag, valid_flag, parser_status
```

The parser should reject incomplete frames or mark them explicitly rather than silently interpolating missing segments.  A frame is complete only after all segments associated with its frame sequence are present, or after a documented timeout has marked it incomplete.

Replay means feeding `capture.pcapng` or an equivalent packet stream through the same segment assembler and decoder, then comparing the normalized output hash/counts with the live capture.  The raw packet artifact makes the project independent of a ROS bag format and allows the parser to be improved after flight.  If ROS2 is later used, record a ROS bag as a convenience copy, not as the only source.

### 4.3 Data-rate planning

At the upper-bound geometry of 276° / 0.05° / 50 Hz, the simple calculation is approximately 5,520 beams per frame and 276,000 beam samples per second before segment/header and echo effects.  If one range and one 16-bit RSSI value are represented by approximately 6 bytes per beam, that is about 1.7 MB/s before protocol overhead; three echoes would be about 5 MB/s before overhead.  This is an order-of-magnitude planning calculation, not a packet-size measurement.

Design the logger for a proposed **10 MB/s sustained raw-capture target** and verify it with the supplied unit and selected profile.  A 100 Mb/s link has a theoretical 12.5 MB/s line-rate ceiling, so high-resolution/all-echo operation must be measured rather than assumed.  If the logger cannot sustain the selected profile, reduce echo count, angular window, scan frequency, or profile while keeping the raw capture and a clear configuration record.

## 5. LiDAR/RGB capability boundary

| Question | picoScan150 contribution | What still needs RGB or another source |
|---|---|---|
| Heave, settlement, rutting, edge drop | Cross-track range profiles can show elevation discontinuities or broad changes; repeat surveys can compare registered profiles | Reliable absolute change requires pose/reference alignment, not only range data |
| Pothole-like depression or bump | A sufficiently large feature can create a repeatable range-shape signature as the UAV moves | The size limit is set by altitude, spot, angular/measurement error, speed, and registration; it must be bench/field tested |
| Fine crack width | Not a supported claim. A crack narrower than the effective spot/sample/registration envelope may not create a distinct range return | RGB close-range imagery and calibrated image scale are the primary evidence; LiDAR depth can provide context or a geometry cue |
| Crack orientation, sealant, color, staining, patching, aggregate texture | Range/RSSI may provide context or a quality change | RGB appearance is required for classification of many visual defects |
| Wet pavement, standing water, dust, vegetation | Multiple echoes/RSSI/quality flags can expose difficult returns; SICK documents outdoor countermeasures | RGB and environmental records help distinguish a surface defect from a weather/contamination artifact |
| Complete 3D surface from one stationary scan | Not possible: it is a single 2D scan plane | Motion, pose, coverage overlap, and registration are required to build a surface representation |
| Coarse 3D mapping while moving | Possible in principle by transforming each profile using time-synchronized UAV pose; SICK also documents encoder-based 3D workflows for moving/rotating setups | UAV motion/pose quality and timing must be validated; the picoScan150 does not make GNSS position accurate by itself |

The recommended product message for the SICK challenge is therefore specific: the picoScan150 supplies a high-rate, long-range, multi-echo **geometric profile** that makes repeated elevation evidence more measurable, while RGB supplies visual defect evidence.  SICK’s current challenge page describes a previous finalist using a SICK PicoScan, drone-based 3D mapping, video, and AI for stream assessment; that is useful challenge alignment, not validation of PaveWatch performance.

## 6. Calibration and registration plan

1. **Sensor-to-body transform:** measure the six-degree-of-freedom rigid transform from the picoScan optical frame to the UAV body frame.  Use a rigid fixture and surveyed/known targets; store the transform with convention, units, and frame names.
2. **Scan-plane orientation:** place the sensor over a flat wall/floor or a surveyed plane and fit the returned line.  Estimate the scan-plane normal, zero-angle direction, and mounting tilt.  Repeat after vibration and after remounting.
3. **Range bias:** scan a planar wall/target at several known distances spanning the intended altitude/slant range, at representative temperatures and remission levels.  Store a bias estimate and uncertainty; do not subtract a bias without keeping the original values.
4. **Timing offset:** expose the LiDAR and camera to a moving edge or translating target while logging sensor time, host receive time, camera time, and vehicle time.  Estimate the relative offset and test it on a second motion direction.  PTP/NTP synchronizes clocks; it does not remove camera exposure, Ethernet, buffering, or processing latency.
5. **Reference alignment:** use stable surveyed markers or natural stable pavement areas to register repeat surveys.  Report the registration residual and coverage mask separately from the measured surface change.  If GNSS is used, treat it as initial georeferencing unless repeatability is demonstrated.
6. **RGB extrinsics/intrinsics:** calibrate camera intrinsics and the camera-to-LiDAR transform.  Keep RGB projection and LiDAR geometric reconstruction as separate intermediate products so a visual classification result cannot be mistaken for a range measurement.

## 7. Bench tests and pass/fail criteria

All thresholds below are **proposed project acceptance criteria**, not SICK specifications.  Record distance, angle, temperature, lighting, remission/target description, variant, profile, filter settings, and whether the test uses first, last, or all echoes.  A pass supports the next engineering step; it does not validate an outdoor UAV survey.

| Test | Method and expected observation | Proposed pass/fail criterion |
|---|---|---|
| Ethernet and replay integrity | Run the sensor for at least 30 minutes at the chosen profile. Capture raw packets, decode frames, stop/restart, and replay the capture into a clean output directory | **Pass:** no unexplained parser errors; zero missing frames/segments in a controlled wired run, or every loss explicitly counted; frame sequence is monotonic; replay reproduces frame/beam counts and timestamps within documented normalization. **Fail:** silent gaps, corrupted checksums accepted, or live/replay counts disagree |
| Flat wall/range bias | Place a large matte wall/board at 2, 5, and 10 m, normal and at a representative oblique angle. Collect at least 100 complete profiles per condition | **Pass:** after the documented bias model, the median range error is within ±30 mm at each tested condition and the central patch’s 95th-percentile repeat spread is ≤20 mm. **Fail:** systematic bias exceeds the project budget or varies materially with angle/target without being recorded |
| Known height steps | Place 25, 50, and 100 mm steps across the scan plane, with the edge well inside the ±30° window. Fit separate surfaces on both sides | **Pass:** the sign of every step is correct, at least 80% of valid profiles contain the step, and the median step-height error is ≤30 mm for the 50 and 100 mm steps. A 25 mm step is characterization-only unless the actual unit demonstrates margin. **Fail:** step is not repeatable or is indistinguishable from flat-surface noise |
| Ramps | Use a rigid ramp with known 5° and 10° slopes and a flat reference. Fit the returned line after calibration | **Pass:** slope sign is correct, fitted slope is within ±1.5° of the surveyed slope at 5 m, and residuals show no unexplained discontinuity larger than 30 mm. **Fail:** slope estimate is dominated by angle/pose error |
| Dark/light targets | At 2, 5, and 10 m, compare a dark target near 10% remission with a light target near 90% remission under controlled indoor light and indirect outdoor-like light if available. Record valid-return fraction, RSSI, and bias | **Pass:** at the proposed 5–8 m range and ±30° incidence, ≥95% of expected beams on both targets are valid in the controlled dry test and the light/dark median bias difference is ≤30 mm after calibration. **Fail:** use the result to reduce altitude/angle or require RGB confirmation; do not extrapolate beyond tested conditions |
| Repeat scan and remount | Fix the sensor, collect 30 repeated scans, remove/reinstall the mount, then repeat. Use the same wall and reference markers | **Pass:** fixed-mount median profile spread ≤20 mm over the central patch; after remounting, the calibrated plane residual is ≤30 mm and the estimated transform change is logged. **Fail:** remounting changes the plane beyond the registration budget |
| Attitude/scan-plane sensitivity | Intentionally introduce known 0.5° and 1° pitch/roll changes or use a fixture. Compare the fitted flat plane before and after correction | **Pass:** the correction reduces plane slope and residual by at least 50% relative to uncorrected data and documents remaining uncertainty. **Fail:** configuration cannot distinguish attitude-induced slope from surface deformation |
| Time alignment | Move a high-contrast edge or board through the scan while simultaneously recording LiDAR, RGB, and host/pose timestamps | **Pass:** estimated offset is stable within ±5 ms across three runs or the measured larger uncertainty is carried into the fusion gate. **Fail:** a single fixed offset cannot align the streams |
| Motion profile | Move the sensor on a cart/rail past the wall or a known step at 1 and 2 m/s; compare transformed profiles with a stationary reference | **Pass:** frame rate/ground-speed spacing agrees with (v/f) within 10%, no packet loss occurs, and the transformed feature location error is ≤100 mm. **Fail:** motion/pose/timing errors obscure the known feature |
| Optical/environmental stress | Repeat a small subset with dark/light targets, direct/indirect light, a clean/partially obscured optics cover, and safe dry dust/rain substitutes only if permitted | **Pass:** every invalid/quality-degraded segment is detected by health/RSSI/valid flags and the pipeline lowers confidence rather than declaring a pavement defect. **Fail:** degraded data are indistinguishable from valid geometry without a warning |

## 8. Development sequence, minimum implementation, fallback, and resource implications

### Recommended MVP

- picoScan150 on a rigid, vibration-resistant mount with its scan plane across track;
- regulated power input and correct M12 Ethernet/power cabling;
- a Linux onboard computer with a 10/100 Ethernet port, monotonic clock, at least 10 MB/s sustained capture target, and removable/SSD storage;
- small acquisition daemon or service that configures/queries the sensor, receives Compact UDP, validates packets, assembles segments, records host timestamps, and writes raw plus normalized data;
- camera recorder and flight-controller/pose logger operating independently but sharing a time base;
- offline parser/replay and a simple flat-plane/step/profile evaluator before any machine-learning claim;
- dry, supervised bench and low-altitude test flights only after Ethernet, calibration, and motion tests pass.

### Fallbacks

| Preferred path | Fallback that preserves a credible demonstration |
|---|---|
| Native ROS2 DDS | Use SICK Compact UDP directly.  Native ROS2 requires the RosConnect license and a suitable firmware version; do not block acquisition on that license. |
| SICK `sick_scan_xd` ROS driver | Use a small host-side parser based on SICK’s Compact format description/Kaitai definitions, while retaining `pcapng` for later conversion.  SICK’s official driver can be added later for visualization and ROS topics. |
| PTP or hardware trigger | Use sensor timestamps plus host monotonic time, NTP/common clock where available, and a measured motion-based offset.  Widen fusion tolerances and label the result as software-synchronized. |
| Maximum frequency/all echoes/high-rate raw logging | Lower the profile to 15 Hz/0.33°, reduce the angle window, or select one echo after recording a comparison capture.  Keep health counters and document the reduced coverage. |
| Onboard processing | Record raw packets and RGB/pose streams onboard; process on a laptop after landing.  This is adequate for a replayable application demonstration. |
| Hardware not yet available | Use SICK’s official picoScan150 ROS bag samples and a synthetic range generator for parser/replay/registration plumbing only.  Label it software demonstration, not picoScan150 field validation. |

Suggested sequence:

1. Implement capture/replay against SICK sample data and synthetic packet fixtures.
2. When hardware arrives, inventory variant/licenses/firmware and perform a no-flight Ethernet capture.
3. Run wall, step, ramp, dark/light, repeatability, calibration, and motion tests.
4. Freeze the initial configuration and acceptance thresholds with the measured results.
5. Integrate RGB and pose timestamps, then perform a supervised low-altitude survey.
6. Add high-resolution or high-rate profiles only when the installed variant, logging bandwidth, and repeat-registration results justify them.

### Resource implications

- **Sensor mass:** SICK lists 220 g without the system plug.  The delivered plug, Ethernet/power cables, rigid mount, regulator, onboard computer, camera, storage, and fasteners must be weighed together for the UAV payload budget.
- **Sensor power:** SICK lists 4.5 W typical and up to 17 W with loaded digital outputs, depending on system plug.  The flight design must reserve power for the sensor, computer, camera, network hardware, startup/transient behavior, and regulator losses; the sensor’s typical value is not a complete payload budget.
- **Network/storage:** the proposed 10 MB/s sustained raw-capture target is a validation requirement derived from an upper-bound calculation, not a SICK specification.  If the selected computer cannot sustain it, use a lower verified profile and preserve a raw packet sample plus complete health counters.
- **Cost treatment:** the picoScan150 should be treated as challenge-supplied only if the team is selected, not as a purchase in the approximately $1,000 initial-build target.  The acquisition computer, camera, regulator, Ethernet harness, mount, storage, and test fixtures remain shared budget or borrowed-equipment decisions.
- **No purchase decision:** this investigation identifies interfaces and test requirements; it does not authorize purchasing a picoScan150, optional licenses, RTK equipment, a Jetson, or cloud processing.

## 9. Interface requirements and cross-investigation dependencies

| Interface | Requirement for this investigation | Dependency/decision for integration |
|---|---|---|
| Flight power | Regulated 9–30 V DC at the sensor connector; design around 4.5 W typical and reserve margin toward the 17 W maximum with loaded digital outputs; include fuse, startup, ground, EMI, and cable strain relief | Investigation 01 must include the actual system plug, regulator, connector, payload mass, battery budget, and vibration isolation |
| Ethernet | M12 D-coded 4-pin to a 10/100 Ethernet interface; isolated network; fixed/documented IP and destination; UDP packet capture; optional switch only if it does not compromise the logger | Investigation 04 must reserve logger bandwidth/storage and decide whether Ethernet is direct to the computer or shared with flight telemetry |
| Sensor configuration | SOPASair/REST/CoLa access during commissioning; export configuration, firmware, license state, and hash; do not change settings in the field without recording them | Central configuration owner must define who can write sensor settings and how the ground-test configuration is restored |
| Time | Preserve sensor time, host receive time, camera frame time, and autopilot time; use PTP if available, otherwise measured software offset | Investigation 03 must select camera trigger/PTP/NTP strategy and define maximum fusion time error |
| Camera | Rigid bracket, known intrinsics, exposure/frame timestamps, camera-to-LiDAR transform, and enough resolution/altitude for the visual defect classes claimed | Investigation 03 owns RGB calibration and crack/appearance boundaries |
| Vehicle pose | Body pose, attitude, altitude, ground speed, quality flags, and a named coordinate-frame convention; use sensor IMU only as an optional aiding stream | Investigations 01/05/06 must agree on body, LiDAR, camera, local-ground, and map frames and on GNSS/RTK/reference-marker assumptions |
| Storage | Sustained raw-capture target 10 MB/s proposed; rotate files safely; include packet counters and checksums; retain free space for RGB and pose | Investigation 04 must verify storage throughput and mission duration on the selected computer |
| Processing | Decoder must handle segmented Compact frames, echoes, optional fields, timestamps, dropped segments, and angle convention; output range/RSSI/quality separately from RGB inference | Investigation 06 must use the normalized profile interface and report registration uncertainty with every change result |
| Output/report | For each finding: survey ID, location, profile/coverage, baseline/current range evidence, RGB evidence if used, magnitude, uncertainty, and confidence | Investigation 08 must avoid presenting a visual crack classification as a picoScan150 crack-width measurement |

## 10. Risks, unresolved assumptions, and decisions needed

- **Unknown variant:** Core/Prime/Pro and exact Dynamic Sensing Profile are unknown until selection and delivery.  This controls usable range, resolution, rate, and expected data volume.
- **Unknown licenses:** Multi-echo, IMU, PTP, encoder, LMDscandata, field evaluation, and RosConnect availability must be read from the delivered unit.  No implementation should assume the optional features are enabled.
- **Coordinate convention:** “±30° from nadir” is a physical design description.  The exact picoScan150 angle range/zero convention must be verified on a live unit before an angle filter is applied.
- **Surface truth:** There is currently no surveyed pavement test site, calibrated step/ramp kit, or ground-truth elevation instrument in this folder.  Bench criteria are proposed release gates, not measurements.
- **UAV trajectory:** GPS-only repeatability, altitude hold, roll/pitch vibration, and drift may dominate the sensor’s range error.  The team must decide whether borrowed RTK/INS or physical reference markers are needed for a credible repeat-survey demonstration.
- **Camera timing:** The camera, autopilot, and picoScan150 synchronization mechanism is unresolved.  Investigation 03 must select hardware trigger, PTP, NTP, or measured software alignment.
- **Weather envelope:** The MVP should begin dry and daylight-controlled.  Rain, direct/low sun, dust, snow, moisture, and vegetation need a separate test plan and confidence degradation policy.
- **Storage capacity:** The 10 MB/s logger requirement is proposed from a conservative upper-bound calculation; packet sizes, all-echo output, camera rate, and flight duration must be measured together.
- **Challenge supply:** The SICK challenge page says selected teams are supplied a picoScan150 and accessories, but selection and the exact delivered configuration are not yet guaranteed.  Do not treat the sensor as purchased in the capstone budget.

## 11. Sources

All sources below were checked on 2026-09-19.  SICK documentation is subject to change; the final system should archive the exact manual/configuration used for testing.

1. SICK, [picoScan150 Operating Instructions, 8028323, English PDF](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf). Primary source for technical data, segmentation, output formats, Ethernet pinout, power, environment, errors, IMU, and driver list.
2. SICK, [SICK$10k Challenge 2026–2027](https://s.sick.com/us-en-SICK10KChallenge-2026). Challenge eligibility, supplied picoScan150 statement, linked challenge resources, naming ambiguity, and prior finalist context.
3. SICK, [picoScan150 software licenses and functions, KA-10714](https://support.sick.com/sick-knowledgebase/article/?code=KA-10714). License-dependent IMU, PTP, encoder, multi-echo, streaming, and native ROS2 context.
4. SICK, [native ROS2 on picoScan150, KA-09438](https://support.sick.com/sick-knowledgebase/article/?code=KA-09438). RosConnect license, firmware prerequisite, DDS topics, and sensor-position example. The article title retains a picoScan100 label but its body explicitly describes picoScan150.
5. SICK, [picoScan150 outdoor application challenges and countermeasures, KA-09881](https://support.sick.com/sick-knowledgebase/article/?code=KA-09881). Rain, temperature, moisture, dust, vegetation, sunlight, contamination, and multi-sensor interference considerations.
6. SICK, [picoScan150 REST/API and Compact-format integration reference, KA-10756](https://support.sick.com/sick-knowledgebase/article/?code=KA-10756). REST configuration/state endpoints, Compact/MessagePack transport details, frame/segment handling, and parser resources; verify against the delivered firmware/manual.
7. SICK, [picoScan encoder and 3D point-cloud guidance, KA-10734](https://support.sick.com/sick-knowledgebase/article/?code=KA-10734). Official explanation that a picoScan150 measures in one plane and that motion/encoder information is required to assemble a 3D point cloud; the UAV implementation will use flight pose rather than assume an encoder.
8. SICKAG, [official `sick_scan_xd` driver repository](https://github.com/SICKAG/sick_scan_xd). ROS1/ROS2 and native C++/Python integration source, including picoScan launch/configuration examples.
9. SICK, [picoScan150 sample ROS bag recordings, KA-09356](https://support.sick.com/sick-knowledgebase/article/?code=KA-09356). Official sample data resource whose body identifies the captured 2D LiDAR as picoScan150 and includes PointCloud2 plus camera topics. Use for software plumbing only, not field-performance evidence.
10. SICK, [SICK Compact-format parsing with Kaitai Struct, KA-10748](https://support.sick.com/sick-knowledgebase/article/?id=ec3e57e5-1979-f111-ab0f-7ced8d922c57). Official parser/telegram-format guidance and links to SICK-maintained structure descriptions.
11. SICK, [Technical Information: SICK Compact Data Format](https://cdn.sick.com/media/docs/3/23/623/technical_information_data_format_description_en_im0104623.pdf). Official format reference for preserving and decoding raw Compact measurement packets.
