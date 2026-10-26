# Investigation 03 — RGB imaging, positioning, and synchronization

**Status:** concept-stage design; no project hardware or field measurements are available yet
**Research date:** 2026-09-19
**Scope:** RGB imagery, navigation/positioning, timing, calibration, and the interfaces needed to associate pavement imagery with picoScan150 profiles.

## 1. Scope and recommendation

### Recommendation

Use a **color global-shutter CSI camera** as the primary RGB sensor: the Arducam B0445 1.58 MP Sony IMX296 module with its manual-focus 6 mm M12 lens. The manufacturer lists 1440 × 1080 RAW10 at 60 fps, a 45° horizontal by 33° vertical field of view, color global shutter, and Raspberry Pi CSI compatibility at a planning price of **$84.99**. The camera board is specified as 38 × 38 mm, but its mass and power are not published on the product page and must be measured before flight. [Arducam B0445 product page](https://www.arducam.com/1-58mp-imx296-color-global-shutter-camera-module-with-m12-lens-for-raspberry-pi.html)

Mount it rigidly and approximately nadir-facing, with the camera and picoScan150 on the same payload plate. Start with a **proposed** 8–12 m above-ground level (AGL), 3–5 m/s ground speed, fixed focus, fixed exposure, and a 30–60 fps capture mode. Use a transverse, vertical picoScan150 scan plane to collect pavement cross-sections as the UAV moves forward. These are starting values, not measured performance.

Use the flight controller's ordinary GNSS/GPS and IMU for route following, attitude, and coarse geotagging. Add four or more high-contrast ground markers around the test area and register each survey to their local coordinates. Do **not** depend on ordinary GPS alone for repeat-survey change detection: GPS.gov gives an open-sky smartphone example of approximately 4.9 m radius accuracy and explains that receiver quality, satellite geometry, blockage, atmosphere, and multipath change the result. That is adequate for finding the site and following a route, but not for proving a small pavement elevation change between dates. [GPS.gov accuracy](https://www.gps.gov/gps-accuracy-0)

Use the companion computer as the file-time authority and PTP grandmaster for the picoScan150 where supported. Record the flight controller's monotonic/boot time, GNSS UTC time, pose/IMU log, camera frame timestamp, LiDAR scan timestamp, frame/scan sequence, and all estimated clock offsets. The preferred camera timestamp is the exposure midpoint from the sensor/driver; a software frame-arrival time is only a fallback. If the selected camera cannot expose a usable trigger/capture signal, periodically flash a visible LED in the camera view while logging the same GPIO event to estimate camera latency and clock offset.

RTK GNSS is an **optional later upgrade**, not an initial-build requirement. If markers are unavailable, image/LiDAR feature registration may still produce a local comparison, but the survey must be flagged as lacking an independently surveyed reference.

### Configuration decision

| Function | Recommended MVP | Status / rationale |
|---|---|---|
| RGB | Arducam B0445 color IMX296 global shutter, 6 mm lens, nadir-facing | **Proposed**; manufacturer facts are listed below; mass, power, actual frame rate, focus, and weather behavior are **to be validated** |
| Position | Flight controller GNSS + IMU, plus 4–6 printed/painted AprilTag-style markers with measured local coordinates | **Proposed**; no separate GNSS/IMU required for the first build |
| Timing | Companion monotonic clock; picoScan150 PTP to companion; camera sensor timestamps when available; LED/capture-feedback calibration | **Proposed**; end-to-end timestamp error is **to be measured** |
| Geometry | Camera nadir; picoScan150 scan plane vertical and transverse to the flight direction | **Proposed**; exact LiDAR mounting rotation is **to be calibrated** |
| Repeat registration | Local ENU frame anchored to markers, then optional UTM/WGS84 output from GNSS | **Proposed**; residual registration error is **to be validated** |
| Fallback | Borrowed GoPro HERO13 Black or DJI Osmo Action 5 Pro for visual demonstration, or Raspberry Pi Global Shutter Camera if CSI and trigger capability are preferred | **Fallback**; action-camera timing and stabilization must be tested before metric use |

## 2. Evidence and assumptions

### 2.1 Camera comparison

The comparison separates manufacturer-published facts from project assumptions. Prices are planning prices captured on 2026-09-19; tax, shipping, availability, lens options, and university/used-equipment access can change.

| Option | Shutter / image facts | Lens / interface | Mass and power | Planning cost and assessment |
|---|---|---|---|---|
| **Arducam B0445 IMX296 color GS** | 1.58 MP; 1440 × 1080; RAW10; 60 fps; color global shutter | Manual-focus 6 mm M12; 45° H × 33° V; IR-cut; MIPI CSI-2 to Raspberry Pi | Board 38 × 38 mm; mass and power not published; **to be measured** | **$84.99**; recommended because it is color, global shutter, low mass in principle, and has an embedded CSI path. [Manufacturer specifications](https://www.arducam.com/1-58mp-imx296-color-global-shutter-camera-module-with-m12-lens-for-raspberry-pi.html) |
| Raspberry Pi Global Shutter Camera | Sony IMX296; 1.58 MP; 1456 × 1088 at up to 60 Hz; exposure as short as 30 µs with adequate light | C/CS mount; CSI; official external XTR trigger is available, but requires board modification and a 1.8 V trigger signal | 34 g camera, 41 g with adapter/dust cap; camera power not specified on the product page | Official launch price **$50**; add a suitable lens. A good trigger-capable fallback if the B0445 driver or lens is unavailable. [Product page](https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/), [trigger documentation](https://www.raspberrypi.com/documentation/accessories/camera.html) |
| Arducam B0499 IMX296 color GS USB | 1.58 MP; 1456 × 1088 at 44 fps over USB 3.0; YUY2; global shutter | 6 mm CS lens; 50° H × 38° V; USB 3.2 Gen 1; Linux/Windows; UVC listed as no extra driver | 34 × 34 mm board; 1.62–1.89 W at 5 V; product listing gives 0.17 kg; **to be weighed in flight configuration** | **$219.99**; integration fallback when a USB camera is more practical than CSI, but it consumes more budget and mass. [Manufacturer product page](https://www.arducam.com/arducam-1-58mp-imx296-color-global-shutter-usb-3-0-camera-module.html) |
| GoPro HERO13 Black | Manufacturer page does not identify a global shutter; treat as a rolling-shutter risk until tested. 5.3K60, 4K120, and 1080p240 are listed; 10-bit HLG; stabilization; GPS; Quik timecode synchronization between HERO13 cameras | Wide action-camera optics; 156° full 8:7 FOV; microSD/USB-C ecosystem; self-contained recording | 159 g camera + mount + battery; battery and thermal behavior depend on settings | **$379.99** official camera price at launch/current shop listing. Best as a borrowed visual fallback; wide distortion, stabilization, and lack of a direct LiDAR trigger make it a poor first metric sensor. [GoPro specifications](https://gopro.com/en/us/shop/cameras/learn/hero13black/CHDHX-131-master.html), [GoPro comparison](https://gopro.com/en/us/shop/cameras) |
| DJI Osmo Action 5 Pro | Electronic shutter speed is listed, but the manufacturer page does not claim global shutter; treat as a rolling-shutter risk until tested. 4K 4:3 at 100/120 fps and 4K 16:9 at 100/120 fps are listed; 120 Mbps maximum bitrate | 155° FOV, f/2.8, 0.35 m–infinity focus range; microSD up to 1 TB and 47 GB usable internal storage | 146 g; camera power/runtime is setting-dependent and not a fixed payload power specification | **$319** standard-combo planning price. A useful borrowed high-resolution visual fallback, but its internal storage and video clock must be correlated to the payload clock. [DJI specifications](https://www.dji.com/osmo-action-5-pro/specs), [DJI store](https://store.dji.com/product/osmo-action-5-pro) |
| Raspberry Pi Camera Module 3 Wide | Rolling shutter; 11.9 MP; 2304 × 1296 at 56 fps and 1536 × 864 at 120 fps; autofocus; HDR up to 3 MP | 120° diagonal FOV; CSI-2; 4 g; standard/wide options | Camera power not specified as a fixed value on the product page; **to be validated** | **$35** official wide-module launch price. Cheapest color fallback, but rolling-shutter distortion and autofocus variability make it secondary for moving metric imagery. [Raspberry Pi product page](https://www.raspberrypi.com/products/camera-module-3/), [official launch pricing](https://www.raspberrypi.com/news/new-autofocus-camera-modules/) |

The global-shutter choices do not make lighting irrelevant. Global shutter removes the frame-skew artifact, but motion blur is still set by exposure time. The Raspberry Pi documentation explicitly describes global shutter as capturing all pixels at once and notes the short-exposure capability; it also documents external triggering. [Raspberry Pi camera documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)

### 2.2 picoScan150 facts used by this investigation

The supplied picoScan150 variant is not yet known, so the following uses the published Core/Prime/Pro ranges rather than silently assuming a particular model. The official operating instructions list a 276° horizontal aperture, scan frequencies from 15–50 Hz depending on variant, angular resolution from 0.05°–1°, 0.05–25/60/120 m working ranges by variant, and a 0.05 m blind zone. They list typical consumption of 4.5 W at 24 V with continuous scan output and no output load, a 9–28 V supply range, and a 4-pin D-coded Ethernet connection. [SICK picoScan150 operating instructions](https://cdn.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf)

The LiDAR is a 2D scanning sensor. In this design it provides moving cross-sections and range/reflectivity features. It does not, by itself, measure fine crack width or produce a complete stationary 3D pavement model. A useful surface map requires motion, pose, scan-plane calibration, filtering, and registration.

### 2.3 Positioning assumptions

- The flight controller, ordinary GNSS receiver, and IMU are available as part of the aircraft or borrowed university equipment; their exact model and flight stack remain an **open decision** for the mission-planning investigation.
- A local test area can have four or more durable, high-contrast markers. Marker coordinates can initially be measured with a tape/laser level or a survey-grade instrument borrowed for testing; RTK is not required to establish a small local frame.
- GNSS is used for route execution and coarse location. Marker registration, stable pavement features, or both are used for repeat-survey comparison.
- A gimbal is not assumed. Camera and LiDAR are rigidly mounted and their boresight is estimated from calibration.
- All altitude, speed, blur, timestamp, and registration limits below are **proposed acceptance targets** until the team measures them.

## 3. Proposed components and operating configuration

### 3.1 Component table

| Component | Interface / responsibility | Planning status |
|---|---|---|
| Arducam B0445 IMX296 color GS + 6 mm lens | CSI-2 to companion; fixed-focus RGB frames; manual exposure and white balance | **Planned primary**; $84.99; actual payload mass, current draw, frame delivery, and driver stability **to be validated** |
| Companion computer from Investigation 04 | CSI camera input, Ethernet to picoScan150, MAVLink/serial to FC, local storage, GPIO/LED sync | Shared dependency; use a Raspberry Pi-class board or borrowed laptop as an MVP. Exact board is **to be selected centrally** |
| picoScan150 | 9–28 V power, D-coded Ethernet, PTP/scan stream; mounted in calibrated vertical transverse plane | Supplied only if selected for the SICK challenge; do not include it as a purchase |
| Flight controller + ordinary GNSS/IMU | route, attitude, vehicle pose, GNSS time, autopilot log, optional trigger/capture feedback | Borrowed/aircraft dependency; exact PX4/ArduPilot selection is **open** |
| 4–6 fiducial markers | visible in images; local survey-frame control points | $10–30 planning allowance for printing, lamination, paint, stakes, and measuring aids |
| GPIO sync LED and level-shifter/isolator as needed | visible flash in camera view plus companion log; optional camera/FC trigger | $5–15 planning allowance; electrical compatibility **to be validated** |
| Rigid plate, vibration-resistant camera mount, lens hood | preserves `T_B_C` and `T_B_L`; shields direct light and splash | $20–50 planning allowance; final mechanical design is **to be validated** |

### 3.2 Camera position and coverage

The primary camera should point approximately down, with its long image axis across the flight direction. A nadir view makes the image-to-ground projection and repeat comparison easier. An optional 15–30° forward oblique tilt can be tested later for crack/shadow visibility, but should not replace the nadir dataset used for geometric comparison.

For the specified 6 mm lens, the first-order ground footprint is:

```text
footprint_width  = 2 * h * tan(45° / 2) = 0.828 h
footprint_length = 2 * h * tan(33° / 2) = 0.592 h
GSD_x = footprint_width  / 1440
GSD_y = footprint_length / 1080
```

| Proposed AGL | Approx. footprint | Approx. GSD | Proposed maximum route-line spacing for 50% side overlap |
|---:|---:|---:|---:|
| 8 m | 6.63 m × 4.74 m | 4.6 × 4.4 mm/pixel | 3.3 m |
| 10 m | 8.28 m × 5.92 m | 5.7 × 5.5 mm/pixel | 4.1 m |
| 12 m | 9.94 m × 7.11 m | 6.9 × 6.6 mm/pixel | 5.0 m |

These calculations are geometric estimates, not field coverage measurements. Actual usable FOV is reduced by mount occlusion, vignetting, distortion, attitude, and the quality mask. The mission planner should generate route lines using the calibrated footprint and a **proposed** 50% side overlap; the survey acceptance step should measure actual valid pixels and LiDAR returns.

At 5 m/s, a 60 fps camera frame is separated by 83 mm of vehicle motion. That gives large along-track frame overlap at the altitudes above, but it does not by itself prove that every frame is sharp. With a proposed one-pixel blur limit at 10 m (about 5.5 mm), the exposure should be no longer than approximately 1.1 ms at 5 m/s. A starting setting of 1/2000 s or shorter in adequate daylight is therefore reasonable; the team must validate noise, saturation, and blur in the actual light.

### 3.3 Positioning and repeat registration

The MVP uses a combination:

1. **GNSS + IMU from the flight controller:** route following, vehicle attitude, approximate altitude, and a coarse WGS84 position for the survey record.
2. **Local visual control:** four or more markers surrounding the pavement area, with known local ENU coordinates. Include at least one marker visible in every accepted image strip when practical; if that is not possible, use overlapping image features and markers at strip ends.
3. **Image/LiDAR registration:** after motion compensation, align the current survey to the baseline using marker observations first, then optionally optimize against stable pavement features. Report the residual rather than hiding poor registration.

A separate GNSS/IMU is not justified for the first build. It adds cost and another time/lever-arm calibration problem. A dual-frequency RTK receiver and fixed base/NTRIP correction is an optional upgrade only if the project later requires absolute centimeter-scale map coordinates, not merely repeatable local change detection.

## 4. Interfaces and data flow

### 4.1 Timestamped synchronization diagram

```text
                         GNSS satellites
                              │ UTC / fixes / optional PPS
                              ▼
                      ┌─────────────────┐
                      │ Flight controller│
                      │ GNSS + IMU       │
                      └───────┬─────────┘
                 pose/IMU log │ MAVLink; optional trigger and capture feedback
                              ▼
                      ┌──────────────────┐
                      │ Companion computer│
                      │ CLOCK_MONOTONIC   │
                      │ optional PTP master│
                      └───┬─────┬─────┬───┘
              CSI-2 frames│     │     │D-coded Ethernet scans / PTP
                           │     │     ▼
                           │     │ ┌─────────────┐
                           │     └►│ picoScan150 │
                           │       │ scan clock  │
                           │       └─────────────┘
                           ▼
                    ┌──────────────┐
                    │ RGB camera    │
                    │ exposure/frame│
                    │ sequence      │
                    └──────────────┘

  Optional GPIO path:
    FC or companion timer ──► camera trigger / sync LED ──► camera exposure
    same event ──► companion GPIO log and/or FC capture input

  Persistent survey folder:
    rgb frames + camera metadata
    lidar packets/scans + LiDAR clock/PTP metadata
    autopilot ULog/BIN + MAVLink events
    manifest.json + calibration IDs + clock-offset estimates + quality flags
```

Every timestamped stream must carry a sequence number and a stated clock domain:

| Stream | Required timestamp | Clock / matching rule |
|---|---|---|
| RGB | exposure midpoint if available; otherwise sensor timestamp, then frame-arrival time as last resort | `camera_seq`, resolution, exposure, gain, white balance, frame clock, and estimated `Δt_camera→companion` |
| picoScan150 | sensor scan timestamp, scan index, angular resolution, scan frequency, echo/quality fields | PTP-aligned to companion where possible; otherwise estimate sensor-to-host offset from packet and clock logs |
| FC pose/IMU | vehicle pose, attitude, velocity, GNSS fix, IMU samples, autopilot boot time and UTC/GPS time | interpolate pose to each RGB exposure and LiDAR scan time; never match only by file modification time |
| Trigger/capture | event sequence, trigger time, capture-feedback time, polarity | use to estimate exposure latency and detect dropped frames |
| LED/marker test | GPIO edge time and the corresponding visible LED frame | calibrates camera pipeline/exposure offset when no hardware feedback exists |
| Survey metadata | mission start/stop UTC, route, AGL, speed, camera settings, sensor serials | copied into `manifest.json` and a human-readable run summary |

The picoScan150 supports IEEE 1588 PTPv2 as an ordinary-clock client; SICK's integration material describes a host as PTP grandmaster and the LiDAR as PTP client, including a Raspberry Pi 4 software-timestamping test. That makes a companion-host timing design plausible, but its end-to-end error in this payload is still **to be measured**. [SICK PTP article](https://support.sick.com/sick-knowledgebase/article/?id=143b54a0-548d-f011-b4cc-7c1e527246ab), [SICK integration performance article](https://support.sick.com/sick-knowledgebase/article/?code=KA-10645)

### 4.2 Timing implementation levels

**Preferred path:**

- Start the companion monotonic clock and record its relation to UTC/GNSS time.
- Configure the picoScan150 as a PTP client of the companion, if the supplied firmware/license exposes the feature.
- Capture RGB frames with driver metadata and fixed exposure/gain/white balance.
- Record FC MAVLink/ULog/BIN pose and any camera trigger/capture messages.
- If the camera exposes a usable hardware trigger, feed it from a known timer through the required voltage conditioning and record the feedback edge.

**Practical no-trigger path:**

- Use the companion's camera driver timestamp as the initial timestamp.
- Put a bright LED in a corner of the RGB image, pulse it from a GPIO at startup and periodically during the survey, and log the GPIO edge with the companion clock.
- Estimate a constant camera pipeline/exposure offset from each LED event; fit drift if the offset changes over the flight.
- Mark the run as `timestamp_quality=calibrated_software` until the measured error passes the survey threshold.

**Action-camera path:**

- Record the action camera's original MP4 and internal metadata without in-camera stabilization if possible.
- Begin recording before takeoff and create a visible LED event at the same time as a logged GPIO event.
- Use the action-camera time only for ordering; map video presentation times to the companion/FC clock using repeated LED events.
- Use fixed shutter, ISO, white balance, focus, and lens/dewarp settings. Do not use the camera's stabilized/horizon-leveled output for metric projection until its geometric effect is characterized.

PX4 documentation is a useful reference for the interface even if the final project uses another MAVLink autopilot: a camera trigger event can produce a `CAMERA_TRIGGER` message with sequence and timestamp, and capture feedback can timestamp the actual capture edge. [PX4 camera trigger/capture](https://docs.px4.io/main/en/camera/fc_connected_camera), [PX4 capture message](https://docs.px4.io/main/en/msg_docs/CameraCapture)

### 4.3 Coordinate frames and transforms

Use these frames in the manifest and processing API:

- `M`: output map frame, normally WGS84/UTM for display only.
- `S`: local survey frame, right-handed ENU with origin at marker `M0`; this is the authoritative comparison frame for the MVP.
- `B`: aircraft body frame, Forward-Right-Down (FRD), fixed to the flight-controller body.
- `L`: picoScan150 frame, fixed to the LiDAR housing; the scan plane and zero angle are documented by the sensor driver and refined by calibration.
- `C`: camera optical frame, with the optical axis and image axes defined by the camera driver/calibration package.
- `G`: GNSS antenna/IMU reference frame if it is physically separate from the flight-controller body.

Store the calibrated rigid transforms as versioned products:

```text
^S T_B(t)       vehicle pose from FC/IMU/GNSS, interpolated at sensor time
^B T_L         rigid LiDAR lever arm and boresight (to be calibrated)
^B T_C         rigid camera lever arm and boresight (to be calibrated)
^C T_L = (^B T_C)^-1 ^B T_L
^M T_S         optional local-frame-to-map transform from markers/GNSS
```

For each LiDAR point, motion-compensate with `^S T_B(t_point)`, apply `^B T_L`, and optionally project the result into the RGB image through `K`, distortion `D`, and `^C T_L`. Do not use a single vehicle pose for a long scan if the test speed makes within-scan motion significant.

Required calibration files include camera intrinsics `K`, distortion `D`, active resolution, focus position, exposure metadata, LiDAR angular/range correction, `^B T_L`, `^B T_C`, GNSS antenna lever arm, scan-plane orientation, camera/LiDAR clock offsets, marker coordinates, and calibration date/operator.

## 5. Calibration and repeatability procedure

### 5.1 Bench procedure

1. **Mechanical reference:** mark the camera, LiDAR, and payload-plate axes. Measure mounting-hole locations, connector strain relief, camera-to-LiDAR baseline, and GNSS antenna-to-body lever arm. Photograph the assembly. Record screw/washer configuration so it can be rebuilt.
2. **Camera intrinsics:** image a printed checkerboard or AprilTag grid at several ranges and tilts covering the intended pavement working distance. Solve `K` and `D`; retain reprojection error, resolution, focus setting, and a hold-out image. Repeat after remounting to quantify repeatability.
3. **Camera focus/exposure:** manually focus the B0445 lens at the expected ground distance. Run a light/dark/gray pavement-like target under bright, cloudy, and shaded illumination. Fix white balance, gain, and shutter for each mission; record saturation percentage and blur.
4. **LiDAR range/plane:** scan a flat wall, a measured step, a ramp, and dark/light targets at several distances in the indoor working range. Estimate range bias, valid-return fraction, angular zero, scan-plane flatness, and the effect of the selected echo/filter mode. This is a bench characterization, not proof of outdoor accuracy.
5. **Camera–LiDAR extrinsics:** put a planar board with high-contrast fiducials in the overlap region. The board should produce a recognizable LiDAR edge/plane while the camera observes the fiducials. Solve `^C T_L` from the known board geometry and corresponding image/LiDAR features; verify on a second board pose. If the geometry is too sparse for a reliable solve, estimate the mechanical transform first and refine it during the controlled outdoor test.
6. **Timing:** pulse a visible LED in the camera view from a logged GPIO. If using the Raspberry Pi Global Shutter Camera's XTR path, also record the trigger edge and verify the specified 1.8 V signal conditioning. Compare LED onset/frame timestamps with the GPIO log over at least 100 events. Repeat after cold start and after a 10–15 minute run to estimate fixed offset and drift.
7. **Static clock check:** record picoscan packets, PTP status, companion clock, and FC MAVLink time simultaneously. Estimate `Δt_Lidar→Companion`, `Δt_FC→Companion`, and their residuals. A failed/unstable PTP lock must set a degraded timing flag rather than being silently accepted.

### 5.2 Controlled outdoor procedure

1. Lay out a small, permissioned pavement test area with four to six numbered markers around the perimeter and one or more measured height steps/boards. Record the marker coordinates in `S`; leave enough clear pavement for the camera and LiDAR footprints.
2. Verify the route and payload settings on the ground: camera resolution, fixed focus, shutter, frame rate, LiDAR profile, PTP state, marker visibility, storage headroom, and mission ID.
3. Fly supervised straight passes at proposed 8, 10, and 12 m AGL and 3 and 5 m/s. Repeat one pass in the opposite direction and one pass after landing/restarting the payload. Keep the remote pilot able to pause, abort, and land.
4. Generate quality products for each pass: coverage mask, blur histogram, saturation mask, timestamp residuals, marker reprojection error, LiDAR valid-return map, and local registration transform.
5. Repeat the same route on at least three runs and, when possible, on another day. Compare marker residuals and stable-surface elevation/image alignment. Label any result as **to be validated** until independent measurements are available.
6. If GNSS drift changes the absolute track but the markers remain visible, report local marker-registered results and the GNSS displacement separately. If neither markers nor stable features can register the survey, reject it for change comparison and retain it only as a visual demonstration.

## 6. Verification tests and proposed success measures

The following are proposed gates for an initial credible demonstration. They are not current performance claims.

| Metric | Definition | Proposed initial gate |
|---|---|---:|
| Image GSD | calibrated ground distance per pixel at the accepted AGL | 4–7 mm/pixel for the 8–12 m operating band; **to be validated** from a measured grid |
| Motion blur | ground displacement during exposure divided by calibrated GSD | median ≤1 pixel and 95th percentile ≤2 pixels on accepted frames; **to be validated** |
| Image saturation | fraction of pavement ROI at clipped black/white values | ≤5% clipped in accepted frames, with a review flag for shadows/wet glare; **to be validated** |
| RGB–LiDAR time error | absolute exposure/scan time residual after offset correction | proposed median ≤5 ms and 95th percentile ≤10 ms; if software fallback exceeds this, propagate the resulting ground displacement uncertainty and flag the run |
| Pose interpolation | pose timestamp gap around each RGB/LiDAR event | no gap >100 ms; **to be validated** from logs |
| Local registration | marker reprojection and stable-feature residual in `S` | proposed ≤0.10 m horizontal residual for an accepted local comparison; **to be validated** |
| Absolute map accuracy | difference between marker/local frame and GNSS map output | report separately; ordinary GPS is not an acceptance criterion for centimeter-scale change |
| Coverage completeness | planned pavement cells with valid RGB pixels and usable LiDAR association | proposed ≥95% RGB coverage and ≥90% LiDAR-associated cells; **to be validated** |
| Repeatability | variation over three repeated passes of a stable target | proposed stable-surface height/image residual below the chosen change threshold; threshold must follow the bench test and is **to be validated** |
| Timestamp continuity | monotonic sequence, no unexplained gaps, recovered sequence numbers | zero unlogged clock resets; dropped frames/scans must be counted and quality-flagged |

For a 5 m/s pass, a 10 ms time error corresponds to approximately 50 mm of along-track position error before pose interpolation. This is why the system must measure time quality and why local marker registration cannot repair a bad RGB–LiDAR association by itself.

### Minimum test set

- **Frame/clock test:** 10–15 minutes with the aircraft stationary; inspect sequence gaps, frame intervals, PTP lock, and clock drift.
- **Motion/blur test:** move the payload or a textured target at known/controlled speed under bright and shaded light; compare 1/1000 s, 1/2000 s, and shorter exposures.
- **Marker test:** image the marker grid at the expected working distances and calculate reprojection error before and after remounting.
- **LiDAR association test:** place a measured step under the camera/LiDAR overlap and verify that the projected range edge lands in the correct image region after applying `^C T_L`.
- **Repeat-flight test:** three supervised passes over the marked test area with different headings/speeds; calculate coverage, local registration, and stable-pavement residuals.
- **Adverse-scene test:** repeat with low-angle sun/shadows, wet-but-safe pavement, dark asphalt, light concrete, and a partly occluded marker. Mark the run invalid when glare, rain, or occlusion prevents quality gates.

## 7. RGB/LiDAR fusion concept and downstream interfaces

### 7.1 Fusion concept

The fusion output should be two related products, not one overstated claim:

1. **Geometric branch:** transform each LiDAR cross-section into `S`, interpolate pose, reject low-quality returns, and accumulate moving profiles. Compare a baseline/current local surface representation for heave, settlement, rutting, edge drop, and larger geometric anomalies. The 2D scan supplies sparse profiles; it does not independently prove fine crack width.
2. **RGB-assisted branch:** run an image-only pavement-defect baseline first. Then project time-aligned LiDAR returns into the image with `K`, `D`, and `^C T_L`; add local range/elevation residual, return quality, and “valid measured surface” masks as features or use late score fusion. Compare image-only and LiDAR-assisted results on the same labeled/synthetic cases. Do not claim an accuracy improvement until the team evaluates it.

The fusion pipeline is:

```text
raw RGB + camera metadata ─┐
raw picoScan150 scans ─────┼─► validate clocks/sequence/quality
FC GNSS/IMU log ───────────┘             │
                                        ▼
                          calibrate + interpolate pose
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
      LiDAR profile/elevation branch                 RGB image branch
                 │                                             │
                 └──────────────► time/space association ◄──────┘
                                        │
                           geometry + visual confidence
                                        ▼
                    change/anomaly result with provenance
```

### 7.2 Interfaces required by other investigations

**picoScan150 / Investigation 02**

- 9–28 V regulated supply and startup/health state.
- D-coded Ethernet link, IP configuration, scan packet/segment format, selected scan frequency/angular resolution/echo mode, scan timestamps, and PTP status.
- Sensor serial/variant, scan-plane convention, range/angle quality fields, and a persistent sensor configuration file.
- Calibrated `^B T_L`, range bias, scan-plane angle, and time offset.

**Onboard computing / Investigation 04**

- CSI-2 camera connector or tested USB fallback; GPIO for LED/trigger/capture; Ethernet path for the LiDAR; MAVLink/serial path to the FC.
- Fixed camera controls: resolution, fps, exposure, gain, focus, white balance, stabilization/dewarp state, and dropped-frame counters.
- Storage for raw/near-raw test frames and a practical compressed/keyframe mode for flights. A 1.58 MP RAW10 stream at 60 fps is approximately 119 MB/s before container/metadata overhead, so continuous raw capture is a stress test rather than an assumed flight-storage requirement.
- `manifest.json`, checksums, calibration IDs, clock offsets, health events, and graceful-stop markers.

**Processing/fusion / Investigation 06**

- RGB frame record: `survey_id`, `camera_seq`, `t_capture`, clock domain, file path/checksum, intrinsics ID, exposure/gain/white-balance, image dimensions, and quality flags.
- LiDAR record: `survey_id`, `scan_seq`, `t_scan`, clock domain/PTP state, sensor configuration, packet/scan path, echo/quality fields, and transform ID.
- FC record: pose/attitude/velocity samples, GNSS fix quality, time mapping, and source log path/checksum.
- Transform package: `K`, `D`, `^B T_C`, `^B T_L`, `^M T_S`, lever arms, clock offsets, calibration version/date, and uncertainty estimates.
- Association result: image pixels/regions linked to LiDAR points or profile cells, projected range/elevation, interpolation method, occlusion/coverage flags, and provenance.

**Mission planning / Investigation 05**

- Route polygon, line spacing, direction, AGL, speed, overlap, heading, camera pointing, LiDAR scan orientation, marker IDs/origin, mission ID, and weather/light restrictions.
- Preflight checks for PTP, camera settings, storage, marker visibility, and payload power.
- In-flight quality telemetry: camera alive/frame count, LiDAR packet/scan count, PTP state, storage, temperature, GPS fix state, and `degraded`/`reject` flags.
- Survey acceptance must reject incomplete coverage, missing calibration IDs, invalid clock state, or excessive registration residual.

## 8. Cost, mass, power, and resource implications

The preferred RGB path adds approximately **$120–170** for the camera, mounting, marker materials, and a simple sync LED/level shifter, excluding the shared companion computer, aircraft, flight controller, and challenge-supplied picoScan150. This keeps the RGB/timing addition compatible with the repository's approximately $1,000 initial-build target if the companion computer and airframe are borrowed or already budgeted by other investigations.

The official picoScan150 instructions give 4.5 W typical sensor consumption at 24 V with continuous scan output and no output load. The camera's exact B0445 current must be measured; budget a separate 5 V regulated payload rail and verify startup current, cable drop, and electrical noise. Do not power the LiDAR directly from a 5 V camera rail. [SICK operating instructions](https://cdn.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf)

The action-camera fallbacks are attractive only if borrowed. A purchased GoPro or DJI camera consumes roughly $319–380 before mounts/storage and is not necessary for the minimum viable build. The Raspberry Pi Global Shutter Camera is cheaper and trigger-capable but needs a suitable C/CS lens and a board modification for the documented XTR path. The Raspberry Pi Camera Module 3 Wide is an inexpensive color fallback for an image-only demonstration, but should be labeled rolling-shutter and non-metric until tested.

## 9. Risks, open decisions, and fallback

| Risk / unresolved assumption | Effect | Mitigation / fallback |
|---|---|---|
| Ordinary GPS drifts by meters or is blocked/multipath-affected | Repeat surveys do not align globally | Use local markers and stable-feature registration; report GNSS and local residuals separately; RTK is optional later |
| No hardware camera trigger or capture feedback | Unknown camera pipeline latency | LED + GPIO sync events at startup and periodically; estimate offset/drift; reject runs whose measured error exceeds the quality gate |
| B0445 CSI driver, frame rate, or camera power is unsuitable | Primary camera cannot be integrated reliably | Use official Raspberry Pi Global Shutter Camera with CSI and documented trigger, or Arducam B0499 USB3; borrow GoPro/DJI for visual-only demonstration |
| Camera saturation, glare, shadows, wet pavement, or low light | False visual defects and missing texture | Fixed exposure per light regime, histogram/saturation mask, sun-angle/weather restrictions, lens hood, and explicit `lighting_quality` flag; collect adverse-light validation data |
| Rolling-shutter action camera or stabilization changes geometry | Misregistration and distorted measurements | Disable stabilization/dewarp where possible; calibrate the action-camera projection; use it only for RGB evidence until validated |
| PTP unavailable or unstable | RGB/LiDAR association error | Save both sensor and host timestamps, run LED/trigger timing calibration, use offline offset estimation, and mark degraded runs |
| Vibration shifts camera/LiDAR boresight | Calibration becomes invalid | Rigid plate, strain relief, witness marks, pre/post-flight calibration target, and mount inspection |
| LiDAR scan plane is poorly oriented or returns are sparse on wet/dark pavement | Incomplete geometry | Use the RGB branch for appearance, choose robust/appropriate echo/filter settings, adjust altitude/speed, and report coverage masks rather than interpolating unsupported surfaces |
| High raw RGB data rate exhausts storage or CPU | Frame drops and incomplete survey | Capture compressed video/keyframes for routine flights, retain raw frames for short calibration runs, use frame/drop counters, and process offline on a laptop |
| Markers are hidden by vehicles/vegetation or not permitted | No control points | Place markers outside the travel lane, use multiple redundant markers, and fall back to stable-image/LiDAR feature registration with lower confidence |
| Final flight stack is PX4 vs. ArduPilot | Different log and trigger details | Standardize the interface at MAVLink/CSV/JSON fields: capture sequence, time, pose, GNSS quality, and calibration IDs; choose the stack centrally in Investigation 05 |

Open decisions for integration:

1. Which flight controller/stack and companion board are actually available to the team?
2. Which picoScan150 Core/Prime/Pro variant and firmware/license will be supplied?
3. Can the selected camera driver expose sensor timestamps, fixed exposure, and a usable trigger/capture signal on the selected companion board?
4. Is the operating flight envelope constrained by the aircraft to a lower altitude, speed, or payload mass?
5. Will the project accept local marker coordinates as the authoritative comparison frame, or is absolute UTM/RTK output required for the final demonstration?

## 10. Sources

All links below were accessed or checked on 2026-09-19.

- [Arducam B0445 1.58 MP IMX296 color global-shutter CSI camera](https://www.arducam.com/1-58mp-imx296-color-global-shutter-camera-module-with-m12-lens-for-raspberry-pi.html)
- [Arducam B0499 IMX296 color global-shutter USB3 camera](https://www.arducam.com/arducam-1-58mp-imx296-color-global-shutter-usb-3-0-camera-module.html)
- [Raspberry Pi Global Shutter Camera product page](https://www.raspberrypi.com/products/raspberry-pi-global-shutter-camera/)
- [Raspberry Pi camera documentation: specifications, triggering, and external trigger](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [Raspberry Pi Camera Module 3 product page](https://www.raspberrypi.com/products/camera-module-3/)
- [Raspberry Pi Camera Module 3 launch pricing](https://www.raspberrypi.com/news/new-autofocus-camera-modules/)
- [GoPro HERO13 Black official specifications](https://gopro.com/en/us/shop/cameras/learn/hero13black/CHDHX-131-master.html)
- [GoPro official camera comparison, including mass](https://gopro.com/en/us/shop/cameras)
- [DJI Osmo Action 5 Pro specifications](https://www.dji.com/osmo-action-5-pro/specs)
- [DJI Osmo Action 5 Pro store pricing](https://store.dji.com/product/osmo-action-5-pro)
- [SICK picoScan150 operating instructions](https://cdn.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf)
- [SICK picoScan150 outdoor application guidance](https://support.sick.com/sick-knowledgebase/article/?code=KA-09881)
- [SICK PTP time synchronization article](https://support.sick.com/sick-knowledgebase/article/?id=143b54a0-548d-f011-b4cc-7c1e527246ab)
- [SICK picoScan ROS/integration timing article](https://support.sick.com/sick-knowledgebase/article/?code=KA-10645)
- [SICK picoScan ROS interface and frame transform example](https://support.sick.com/sick-knowledgebase/article/?code=KA-09438)
- [GPS.gov GPS accuracy](https://www.gps.gov/gps-accuracy-0)
- [PX4 camera trigger and capture interface](https://docs.px4.io/main/en/camera/fc_connected_camera)
- [PX4 CameraCapture message](https://docs.px4.io/main/en/msg_docs/CameraCapture)
- [PX4 PPS time synchronization](https://docs.px4.io/main/en/advanced/pps_time_sync)
