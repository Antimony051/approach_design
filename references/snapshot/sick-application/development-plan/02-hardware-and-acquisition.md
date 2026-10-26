### 5. Flight platform and payload integration

The baseline platform is the Holybro X500 v2 development kit with Pixhawk 6C, M10 GNSS, and 915 MHz telemetry. It combines the frame, propulsion components, power distribution, flight electronics, and mounting provisions needed for a research payload. A 4S 5 Ah battery is the initial energy-storage candidate. The final configuration will be checked against the manufacturer's instructions and the measured installed payload. [3]

| Component | Function and connection | Integration decision |
|---|---|---|
| Pixhawk 6C / PX4 | Flight control, GNSS/IMU, battery monitoring | Dedicated control system; pin a tested firmware release |
| QGroundControl | Mission design, route upload, operator monitoring | Save and read back each mission before flight |
| picoScan150 | Range profiles over Ethernet | Direct connection to Pi; separate fused power branch |
| Camera Module 3, standard color | Downward RGB through CSI | Fixed focus/exposure settings after calibration; record frame metadata |
| Raspberry Pi 5, 2 GB | Capture, timestamp association, health monitoring | Headless recorder with active cooling |
| 256 GB USB 3 SSD | Raw measurements and manifests | Retained cable, monitored free space, replay verification |
| Payload plate and protective parts | Maintain sensor alignment and protect wiring | Rigid optical mount with adjustment and witness marks |

The Pi provides Ethernet, camera interfaces, and USB storage connectivity. Camera Module 3 provides a 12 MP imaging sensor and controllable focus; its rolling shutter requires motion characterization. The initial recording target is 1080p at 15 frames/s with per-frame timestamps. Full-resolution still capture will be tested separately for visual detail. Acquisition modes will be frozen only after simultaneous capture tests. [4, 5]

A global-shutter camera is an upgrade candidate if rolling-shutter distortion prevents useful alignment at the validated flight speed. It will require a new camera calibration, timestamp characterization, and budget revision. Short exposures reduce blur but do not eliminate rolling-shutter distortion.

#### Mechanical arrangement

The LiDAR and camera will share a rigid plate below the aircraft center. The LiDAR scan plane will be approximately vertical and transverse to forward motion; the camera will face downward with overlapping ground coverage. Printed parts may provide enclosures, cable retention, and mounting interfaces. Fastener retention, clearance, and optical alignment will be checked under representative loads.

The design will keep the useful scan sector clear of landing gear, arms, and cabling. The battery position will be adjusted to balance the assembled aircraft. Computer vibration isolation must not permit the camera-to-LiDAR transform to change. All payload items will have positive retention, and wiring will remain clear of propellers.

The preliminary takeoff-mass envelope is approximately 1.9–2.2 kg, based on subsystem allowances rather than a weighed aircraft. The team will measure the complete build, center of gravity, current draw, vibration, and hover behavior before survey flight. Published payload or unloaded endurance figures do not establish performance for this configuration.

#### Power distribution

```text
4S battery → power distribution / battery monitor → ESCs and motors
           → flight-controller power module → Pixhawk, GNSS, control links
           → fused sensor branch → picoScan150
           → fused 5 V / 5 A regulator → Pi, camera, SSD, cooling
```

The received sensor's label and manual will govern its supply limits and fuse selection. Payload startup, cable drop, regulator temperature, and electrical noise will be checked with all recorders active. The Pi will not draw its operating power from a flight-controller telemetry port. Budget up to 25 W for the Pi peripheral rail; this is a supply-sizing allowance, not measured continuous consumption. [2, 4]

### 6. Survey geometry and mission operation

The proposed starting envelope is 5–8 m above the pavement, 1–2 m/s ground speed, and a usable LiDAR sector of ±30° about nadir. The initial sensor profile is 15 Hz / 0.33°, subject to confirmation on the supplied unit. Turns and acceleration segments will be flagged separately from accepted survey legs.

For a flat surface at sensor height H, the ideal scan width is 2H tan(30°). At 5 m this is approximately 5.77 m; at 8 m it is 9.24 m. Nadir sample spacing at 0.33° is approximately 29–46 mm over that height range. At 1–2 m/s and 15 profiles/s, along-track spacing is approximately 67–133 mm. These are sampling calculations; beam footprint, surface reflectivity, vehicle motion, and alignment error determine useful resolution.

The overlapping camera footprint will set the fusion survey width. The team will measure actual coverage and use overlapping passes where necessary. A wider LiDAR sector alone does not imply equivalent RGB coverage.

An operator will define the site boundary, survey legs, height reference, speed, direction, takeoff/landing area, and return behavior. PX4 will execute supervised waypoint missions, with manual control available throughout. Mission and failsafe behavior will be exercised in simulation and on the bench before field use. [6]

The first site will be an authorized, controlled paved area with clear operating boundaries. A pilot and observer will oversee the mission. Flight duration and return reserve will be set from measured loaded-aircraft consumption. The first flights will establish capture and control performance before attempting a complete comparison survey.

### 7. Acquisition, timing, and calibration

The recorder will save original Compact UDP packets and host receipt times, decoded profile sequence numbers, sensor timestamps, range/echo/signal fields, camera frames and metadata, and flight-controller logs. Raw evidence will remain available for reprocessing when a parser or calibration changes.

The Pi monotonic clock will provide the common elapsed-time reference. Sensor, camera, and flight-controller clocks will retain their original values alongside the estimated mapping into that reference. PTP will be evaluated if supported by the supplied sensor; camera exposure timing and motion tests remain necessary even with network clock synchronization.

Camera intrinsics will be calibrated at the selected focus and capture mode. Sensor-to-body and camera-to-LiDAR transforms will be measured using visible and geometric targets. A moving-target test and logged light event will help estimate camera offset and drift. Camera row timing will be included where needed. Acquisition with insufficient timing evidence will be flagged and excluded from strong fusion claims.

At 2 m/s, a 10 ms timing error produces 20 mm of translational mismatch before attitude error is considered. This illustrates why timing thresholds must follow the intended measurement scale. Similarly, an attitude error of 0.1° produces about 14 mm of lateral displacement at 8 m. Neither ordinary GNSS nor the LiDAR's optional IMU alone establishes accurate moving-surface reconstruction.

The processing frame will use right-handed local east/north/up coordinates in meters. Flight-controller coordinates will be converted at one tested boundary. A set of at least four visible site markers will support repeat alignment, with additional independent check targets reserved for evaluation. GNSS will supply navigation and approximate geographic placement; local registration will determine whether repeat surveys are comparable.
