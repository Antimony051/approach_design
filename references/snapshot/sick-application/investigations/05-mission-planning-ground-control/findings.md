# Investigation 05 — Mission planning and ground control

**Status:** concept-stage planning brief. The software choices and limits below are proposed engineering controls, not measured aircraft performance, regulatory approval, or permission to fly.

**Research access date:** 2026-09-19.

## 1. Scope and recommendation

### Recommendation

Use a **Pixhawk-compatible flight controller running a pinned PX4 release with QGroundControl (QGC) as the primary ground-control station**. Plan a supervised waypoint/corridor mission, upload it to the flight controller, and let the autopilot execute the stored route while a remote pilot continuously monitors the aircraft and retains immediate manual takeover. Keep the first demonstration to waypoint autonomy; do not use companion-computer offboard control or an unvalidated autonomous perception loop.

The current PX4 documentation describes missions created and uploaded with QGroundControl, QGC provides survey and corridor pattern tools, PX4 performs mission-feasibility checks, and PX4 supports geofences, rally/safety points, battery/data-link failsafes, and camera-trigger/capture reporting. PX4 also documents MAVLink as the interface for QGroundControl, MAVSDK, companion computers, and external camera components. [PX4 Missions](https://docs.px4.io/main/en/flying/missions), accessed 2026-09-19; [PX4 Safety Configuration](https://docs.px4.io/main/en/config/safety), accessed 2026-09-19; [PX4 Geofence](https://docs.px4.io/main/en/flying/geofence), accessed 2026-09-19; [PX4 Camera Architecture/Integration](https://docs.px4.io/main/en/camera/camera_architecture), accessed 2026-09-19; [PX4 MAVLink Messaging](https://docs.px4.io/main/en/mavlink/), accessed 2026-09-19.

Maintain two mission representations:

1. A **canonical, stack-neutral route manifest** owned by PaveWatch. It records the site polygon, local survey frame, ordered survey legs, altitude/speed/yaw policy, payload profile, markers, safety boundaries, and a content hash.
2. A **stack-specific deployed plan**, initially a QGroundControl .plan file containing the mission, geofence, and rally points. The GCS-generated file is an execution artifact, not the sole definition of route repeatability.

The planned route is not automatically safe merely because QGC or PX4 accepts it. A pilot, spotter, site owner/operator, and the applicable institutional/airspace process must authorize the actual operation. No such approval is established by this investigation.

### Fallback recommendation

If the selected controller or team workflow is better supported by ArduPilot, use **ArduCopter with Mission Planner on a Windows ground station**. Mission Planner has a documented polygon survey/grid generator, distance-based camera triggering, fence and mission planning, and ArduPilot documents mission rewind-on-resume specifically for data-gathering missions. The drawback is that Mission Planner is primarily Windows-native, and the exact behavior of stack-specific commands must be checked on the selected firmware before flight. [Mission Planner overview](https://ardupilot.org/planner/docs/mission-planner-overview.html), accessed 2026-09-19; [Mission Planner camera control and survey missions](https://ardupilot.org/planner/docs/common-camera-control-and-auto-missions-in-mission-planner.html), accessed 2026-09-19; [ArduPilot mission rewind on resume](https://ardupilot.org/copter/docs/common-mission-rewind.html), accessed 2026-09-19.

MAVProxy is a useful **diagnostic, telemetry-forwarding, SITL, and companion-side fallback**, but not the recommended primary operator planner. Its official documentation describes it as a portable command-line developer GCS that can forward MAVLink to QGC or Mission Planner. [MAVProxy overview](https://ardupilot.org/mavproxy/index.html), accessed 2026-09-19; [MAVProxy telemetry forwarding](https://ardupilot.org/mavproxy/docs/getting_started/forwarding.html), accessed 2026-09-19.

## 2. Evidence and assumptions

### 2.1 Flight-stack and GCS comparison

| Candidate | Evidence-backed capability | PaveWatch fit | Decision status |
|---|---|---|---|
| **PX4 + QGroundControl** | PX4 missions are uploaded to the flight controller and executed in Mission mode. PX4 documents mission feasibility checks, geofences, return/safety points, battery and data-link failsafes, and camera-trigger/capture paths. QGC documents survey/corridor patterns, mission upload/download, planned home, geofence, and rally-point editing. PX4 is BSD 3-Clause; QGC is Apache 2.0/GPLv3. | Best cross-platform primary workflow for the proposed Pixhawk-class development kit. It provides a strong plan/fence/rally artifact and a direct MAVLink companion path. Survey tools still need testing with the selected release and custom payload. | **Recommended baseline; not installed or flight-validated.** [PX4 project documentation](https://github.com/PX4/PX4-Autopilot/blob/main/docs/en/index.md), accessed 2026-09-19; [QGroundControl repository](https://github.com/mavlink/qgroundcontrol), accessed 2026-09-19. |
| **ArduCopter + Mission Planner** | ArduPilot Auto mode executes stored navigation and DO commands. Mission Planner documents polygon grid/survey generation, DO_SET_CAM_TRIGG_DIST, fences, mission files, and telemetry/log analysis. ArduPilot documents battery, radio/GCS, EKF, and geofence failsafes. ArduPilot and Mission Planner are GPLv3. | Strong fallback for a multicopter survey, especially if the team needs the Mission Planner survey generator or ArduPilot's documented rewind-on-resume. Windows dependency and stack-specific command behavior add integration friction. | **Fallback candidate; requires a deliberate stack decision.** [ArduCopter Auto mode](https://ardupilot.org/copter/docs/auto-mode.html), accessed 2026-09-19; [ArduPilot mission planning](https://ardupilot.org/planner/docs/common-mission-planning.html), accessed 2026-09-19; [ArduPilot license](https://ardupilot.org/dev/docs/license-gplv3.html), accessed 2026-09-19. |
| **PX4 or ArduPilot + MAVProxy** | Portable command-line MAVLink GCS with map, telemetry-forwarding, logging, and developer/SITL modules. | Useful for link diagnostics, replay, forwarding one vehicle stream to another GCS, and headless companion tests. Not the primary route-authoring UI. | **Support tool, not primary planner.** [MAVProxy documentation](https://ardupilot.org/mavproxy/index.html), accessed 2026-09-19. |

QGroundControl is preferable as the first GCS even if ArduPilot is selected because its project describes support for PX4, ArduPilot, and MAVLink vehicles, and its Plan View has Open, Save, Upload, Download, KML export, mission, geofence, and rally-point operations. The team must still verify every generated command on the connected firmware rather than assuming cross-stack equivalence. [QGC Plan View](https://github.com/mavlink/qgroundcontrol/blob/master/docs/en/qgc-user-guide/plan_view/plan_view.md), accessed 2026-09-19; [MAVLink Mission Protocol](https://mavlink.io/en/services/mission.html), accessed 2026-09-19.

### 2.2 Important assumptions

- The aircraft will be a multicopter or multicopter-like Pixhawk-compatible platform, consistent with the current flight-platform investigation. The final controller, firmware, frame, battery, RC system, telemetry link, and flight parameters are not yet selected centrally.
- The initial survey will be **supervised waypoint autonomy**. The operator can interrupt the mission through an RC mode switch or GCS command, and the remote pilot remains responsible for the aircraft.
- The selected site can provide a safe launch/landing area, a people/vehicle exclusion area, visible reference markers, and a route within the pilot's approved operating area.
- The route will use WGS84 global coordinates for the autopilot mission, with a local ENU survey frame anchored to markers for repeat comparison. Exact GNSS/RTK/reference-marker performance is unresolved.
- The picoScan150 is challenge-supplied only if the team is selected. The delivered sensor variant, firmware, scan profile, licenses, Ethernet configuration, angle convention, and timestamp behavior remain unresolved.
- The RGB camera may be a CSI camera that cannot accept an autopilot hardware trigger. The companion must support payload-local capture/timestamping, with a hardware trigger or visible-LED calibration path when available. Investigation 03 owns the final timing decision.
- All thresholds in this document are **proposed acceptance targets**, not aircraft, sensor, or regulatory specifications. Replace or justify them after SITL, bench, and supervised field testing.

### 2.3 Planning requirements are not approvals or validation

A credible development plan must obtain site-owner permission, complete the applicable institutional safety review, identify the responsible remote pilot and spotter, determine applicable airspace/operational requirements, and validate firmware, GCS, parameters, mission commands, RC takeover, failsafes, payload logging, and route repeatability before an outdoor pavement survey.

These statements do **not** mean the project currently has permission to fly, that the aircraft has been tuned, that the route has been measured, that the failsafes work, or that fully autonomous operation is safe. No hardware measurement or field validation is claimed here.

## 3. Proposed components or software

### 3.1 Primary software stack

| Layer | Proposed choice | Responsibility | Boundary |
|---|---|---|---|
| Flight controller | Pixhawk-compatible board, **PX4** pinned to a recorded stable release | Stabilization, navigation, mission execution, RC/GCS failsafe, battery/geofence action, vehicle log | Owns flight safety and actuation. The companion does not replace estimator, failsafe, or pilot. |
| Operator GCS | **QGroundControl** on a dedicated laptop/tablet | Route editing, plan/fence/rally upload/download, readiness display, start/pause/resume/RTL/land, live telemetry, log download | Operator is the planned authority for mission/mode commands in the MVP. |
| RC link | Independent transmitter/receiver selected by Investigation 01 | Immediate mode change/manual takeover and emergency action according to switch mapping | Must remain usable if GCS or companion fails. |
| Telemetry link | MAVLink radio, USB for bench, or approved network/serial link | Heartbeat, position, attitude, battery, health, mission progress, ACKs, log transfer | Range, latency, loss, and recovery must be tested. Wi-Fi presence is not a failsafe. |
| Companion computer | Investigation 04 selection; Linux SBC or borrowed laptop for MVP | Payload acquisition, storage, timestamps, sensor health, camera capture, manifest, read-only telemetry | Must not send arm, takeoff, navigation setpoints, or mode changes in first-flight workflow. |
| LiDAR network | Isolated Ethernet from companion to picoScan150 | Sensor configuration, health polling, raw/normalized capture | Keep sensor traffic separate from flight control unless bandwidth/isolation are proven. |
| RGB capture | Investigation 03 camera and driver | Fixed settings, frames, sequence/timestamp index, exposure/quality metadata | If no FC trigger exists, companion controls capture and records timing quality. |
| Offline processing | Investigation 06 and later pipeline | Replay, calibration, registration, coverage, change detection, reporting | A live map is not survey acceptance; process the recorded manifest and logs. |

PX4 documents TELEM 2 as a default MAVLink port suitable for a companion and recommends MAVSDK for common MAVLink services, while noting that applications can also use generated MAVLink libraries or pymavlink. The first implementation need not commit to MAVSDK; Investigation 04 should choose the library after the computer is selected. [PX4 Serial Port Configuration](https://docs.px4.io/main/en/peripherals/serial_configuration), accessed 2026-09-19; [PX4 Raspberry Pi Companion with Pixhawk](https://docs.px4.io/main/en/companion_computer/pixhawk_rpi), accessed 2026-09-19.

### 3.2 Command and authority policy

- **GCS to flight controller:** upload/download/clear mission, geofence, and rally plans; set or verify parameters; change flight mode; arm/disarm under the preflight process; start/pause/resume/RTL/land; acknowledge warnings.
- **RC transmitter to flight controller:** immediate manual flight-mode changes and emergency actions. RC takeover must work without companion or GCS.
- **Flight controller to GCS/companion:** heartbeat, mode, armed state, position, attitude, velocity, GNSS/estimator, battery, geofence, current mission item, mission ID where supported, command ACKs, and camera events.
- **Companion to payload:** start/stop acquisition, configure sensor profile, record health, capture RGB, and close files on mission end/abort.
- **Companion to flight controller:** read-only telemetry subscription in the MVP, plus optional camera capture feedback or payload-health status after the path is verified. No navigation setpoints or offboard controller in the initial demonstration.
- **Processing has no live command path:** offline quality/coverage results cause a re-plan or re-flight decision; they do not automatically command the aircraft.

PX4 warns that MAVLink messages are unauthenticated by default and that an unauthorized sender can issue powerful commands. Enable and test MAVLink signing or equivalent access control when the network is selected. [PX4 MAVLink Messaging](https://docs.px4.io/main/en/mavlink/), accessed 2026-09-19.

### 3.3 Proposed state and command diagram

HOLD/LOITER is the immediate pause state. The exact stack-specific command and resume behavior must be verified before flight.

~~~text
[SITE + PLAN DRAFT] --validate route/fence/rally/battery/payload--> [PLAN VALIDATED]
       | plan rejected or unavailable                                  |
       v                                                               | upload + read-back + ACK
 [HOLD / REPLAN] <------------------------------------------------ [PLAN ON FC]
                                                                      |
                                                               arm/takeoff
                                                                      v
                                                               [ARMED / TAKEOFF]
                                                                      |
                                                                mission start
                                                                      v
                                                               [SURVEY RUNNING]
                                                               |       |       |
                                                     pilot pause |       |       | fault/abort
                                                               v       |       v
                                                        [HOLD / LOITER] |  [ABORT / RTL]
                                                               |        |      |
                                                     operator review   |      | low battery,
                                                               |        |      | lost link,
                                                               v        |      | GNSS/EKF,
                                                     [SURVEY RESUMING]  |      | geofence,
                                                               |        |      | people/weather
                                                               +--------+      |
                                                                route gap      v
                                                                or bad pose [RETURN / LAND]
                                                                                     |
                                                                                     v
                                                                             [DISARM / DATA CLOSE]
                                                                                     |
                                                                   complete + valid record?
                                                                                     |
                                                         +---------------------------+-----------+
                                                         |                                       |
                                                        yes                                     no
                                                         v                                       v
                                                [SURVEY ACCEPTED]                    [SURVEY REJECTED /
                                                                                      REPLAN OR RE-FLY]

Any airborne state can also transition immediately to:
[PILOT TAKEOVER / MANUAL] --pilot decision--> [HOLD, RTL, LAND, or ABORT]
~~~

Normal commands are UPLOAD, READ BACK, ARM, TAKEOFF, START MISSION, HOLD/PAUSE, RESUME, RTL, LAND, DISARM, and CLOSE RECORD. Failsafe transitions are generated by the flight controller according to configured and tested parameters; do not assume that lost GCS link, low battery, geofence breach, or estimator fault has a safe outcome until tested on the selected stack.

## 4. Interfaces and data flow

### 4.1 End-to-end data flow

~~~text
Site polygon + markers + route policy
                |
                v
      PaveWatch route_manifest.json
                |
      QGC/PX4 plan compiler or manual review
                |
                v
  mission.plan + fence + rally points + hash
                |
      MAVLink Mission/Command/Parameter services
                |
                v
       Pixhawk flight controller  <---- RC receiver / pilot
         |       |       |
         |       |       +---- FC log (PX4 ULog; ArduPilot fallback log)
         |       +------------ MAVLink telemetry / mission state / events
         v                                  |
    Navigation /                       companion computer
    pose / time                       |        |        |
                                      |        |        +--> health + manifest
                             Ethernet |        +----------> RGB frames/index
                                      v                   |
                                 picoScan150              |
                                      |                   |
                                      +--> raw packets / normalized scans
                                                          |
                                     local storage + closed record
                                                          |
                                                          v
                          offline replay, coverage, registration, processing
~~~

### 4.2 Required interfaces

| Interface | Required fields or behavior | Acceptance/ownership |
|---|---|---|
| Mission upload/download | MAVLink mission protocol, MISSION_ITEM_INT where supported, sequence, frame, command, parameters, ACK/result, mission count, and read-back | GCS compares read-back to planned hash or normalized item hash before arm. MAVLink documents mission, geofence, and rally upload/download with retransmission and acknowledgement. [MAVLink Mission Protocol](https://mavlink.io/en/services/mission.html), accessed 2026-09-19; [MAVLink common messages](https://mavlink.io/en/messages/common.html), accessed 2026-09-19. |
| Flight status | Heartbeat, armed state, mode, position, altitude, velocity, attitude, GNSS/estimator, battery, geofence, mission item, ACK | GCS shows it live; companion records it with payload streams. Missing status is a fault/quality flag, not silently interpolated. |
| Mission progress | MISSION_CURRENT, MISSION_ITEM_REACHED where provided, mission ID/opaque ID where supported, normalized planned sequence | Associates payload records with route legs. Processing still uses recorded pose and timestamps, not file modification times. |
| FC-to-camera timing | Trigger/capture event and timestamp if available; otherwise companion capture timestamp plus measured calibration offset and timestamp quality | Investigation 03 owns timing. PX4 documents trigger/capture feedback; actual end-to-end error remains to be measured. [PX4 CameraTrigger](https://docs.px4.io/main/en/msg_docs/CameraTrigger), accessed 2026-09-19; [PX4 Camera Architecture](https://docs.px4.io/main/en/camera/camera_architecture), accessed 2026-09-19. |
| Companion-to-LiDAR | Isolated Ethernet, IP/configuration, raw packets, frame/segment sequence, sensor timestamp, host timestamp, health, configuration hash | Investigation 02 owns the parser/profile. Mission ID and route hash are required in the acquisition manifest. |
| Clock/frames | FC boot/UTC/GNSS time, companion monotonic/UTC, sensor timestamp, camera sequence, clock quality, and M/S/B/L/C frame names | A survey with contradictory time/frame metadata is rejected for change comparison. |
| Payload command boundary | Payload service starts/stops/configures/ closes acquisition; it cannot arm, navigate, or override pilot | A sensor/logging failure cannot become a flight-control failure. |

### 4.3 File outputs

The following layout is proposed; Investigation 04 should reconcile it with the final logger and Investigation 02 sensor layout.

~~~text
survey_<survey_id>/
  route_manifest.json              # canonical route, site, policy, hashes
  mission_<survey_id>.plan         # QGC plan: mission + geofence + rally points
  mission_<survey_id>.kml          # human-review/export view, if generated
  mission_readback.json            # normalized plan read back from FC
  flight_config.json               # FC identity, firmware, parameters, GCS version
  payload_config.json              # sensor/camera serials, profiles, calibration IDs
  preflight_checklist.json         # operator, time, result, exceptions
  telemetry.tlog                   # optional MAVLink telemetry capture
  autopilot.ulg                    # PX4 flight log; ArduPilot uses its native log
  vehicle_pose.jsonl               # pose/attitude/time/quality
  mission_events.jsonl             # arm, mode, mission current, pause, resume, RTL, faults
  camera/
    frames/                        # RGB files or video segments
    frame_index.csv                # sequence, timestamp, exposure, quality, file path
  lidar/
    raw/                            # raw packet capture, never silently discarded
    lidar_frames.jsonl              # normalized frame/segment index and health
  health.jsonl                     # FC, companion, payload, storage, clock, link health
  coverage.json                    # planned vs observed leg/track and missing intervals
  acceptance.json                  # pass/fail and reviewer/signature fields
  checksums.sha256                 # closed-record integrity manifest
~~~

The QGC .plan format is JSON and can contain mission items plus optional geofence and rally-point information; its developer documentation also identifies firmware type, vehicle type, planned home, altitude mode, and mission items. The project-specific route_manifest.json is still necessary for survey markers, local frame, payload profile, route-generation version, route hash, and acceptance policy. [QGC Plan File Format](https://github.com/mavlink/qgc-dev-guide/blob/master/en/file_formats/plan.md), accessed 2026-09-19.

### 4.4 Route-repeatability mission template

This is a reproducible starting template, not a final flight command set. Values marked **proposed** must be tuned and measured.

~~~yaml
mission_template: pavewatch_corridor_v1
survey_id: PW-YYYYMMDD-SITE-PASSNN
site:
  boundary_file: site_polygon.geojson
  coordinate_reference: WGS84 for FC mission; local ENU S frame for comparison
  origin: marker_M0
  reference_markers: [M0, M1, M2, M3]
  marker_visibility: required at launch/landing and at least two survey-control locations
route:
  geometry: paved-corridor parallel legs / lawnmower inside boundary
  route_orientation: pavement centerline bearing measured during planning
  leg_spacing_m: derived from measured payload footprint
  turnaround_margin_m: derived from aircraft stopping/turning behavior; outside comparison polygon
  entry_leg: fixed and recorded by route manifest
  heading_policy: face planned leg bearing; record every waypoint yaw
  direction_policy: alternate legs only if body-to-sensor transform and processing support sign reversal;
    otherwise use same-heading survey legs with a separate non-survey return path
  waypoint_acceptance_m: proposed 0.5; validate against track data and coverage need
altitude:
  reference: AGL/terrain reference chosen centrally and recorded for every item
  target_m: proposed 8.0 for initial planning; reconcile with Investigations 02 and 03
  tolerance_m: proposed +/-0.5 or approved percentage, whichever is larger
  terrain_following: disabled until terrain and obstacle behavior are validated
motion:
  survey_speed_mps: proposed 1.5 (initial low-speed test range 1-2)
  speed_tolerance_mps: proposed +/-0.2
  acceleration_limit: fixed in FC configuration and recorded with mission
  yaw_tolerance_deg: proposed +/-10 relative to planned leg heading
payload:
  lidar_profile: selected verified picoScan150 profile; record variant, window, rate, echo policy
  lidar_orientation: transverse scan plane documented relative to B body frame
  rgb_profile: fixed resolution/focus/exposure/gain/white balance; record calibration ID
  capture_policy: trigger only if actual camera path supports it; otherwise companion capture
  timing_policy: PTP/hardware feedback when available; otherwise calibrated software timing
  mission_id_in_record: required
safety:
  geofence: polygon/cylinder with site margin and tested breach action
  rally_points: at least one approved alternate recovery point when safe
  rtl_or_land: configured, reviewed, and tested before outdoor survey
  low_battery: thresholds selected from measured battery/flight reserve
  lost_gcs_link: action and timeout selected, documented, and tested; RC remains available
execution:
  preflight: checklist required; upload/read-back/hash match required
  mission_control: supervised waypoint mode only
  pause: HOLD/LOITER or stack-supported pause; record event and exact state
  resume: operator review; validated stack-specific resume/rewind behavior
  end: RTL/LAND, disarm, close logs, checksums, acceptance review
~~~

QGC survey documentation exposes altitude, trigger distance, grid spacing, transect angle, turnaround distance, entry-point rotation, and optional terrain following. It warns that flat-ground assumptions can alter overlap or put the vehicle near terrain/obstacles. Use a validated local surface and obstacle review rather than assuming map elevation is correct. [QGC Survey Pattern](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/plan_view/pattern_survey.html), accessed 2026-09-19.

For the ArduPilot fallback, the deployed mission may use MAV_CMD_DO_SET_CAM_TRIGG_DIST for distance-based camera triggering and MAV_CMD_DO_SET_RESUME_REPEAT_DIST for a measured rewind distance. ArduPilot documents that MIS_RESTART=0 is needed for rewind-on-resume and that rewind distance must let the aircraft regain the planned path and heading. Confirm these commands in the actual firmware/GCS combination before use. [ArduPilot mission commands](https://ardupilot.org/copter/docs/common-mavlink-mission-command-messages-mav_cmd.html), accessed 2026-09-19; [ArduPilot mission rewind](https://ardupilot.org/copter/docs/common-mission-rewind.html), accessed 2026-09-19.

### 4.5 Operator workflow and checklists

#### Step-by-step supervised mission workflow

1. **Select and authorize the site:** identify the pavement area, launch/landing area, obstacles, people/vehicle exclusion zone, reference markers, weather limits, spotter, remote pilot, and the applicable permission/safety-review path.
2. **Create the site record:** assign a survey ID, record the WGS84 site boundary, local ENU origin and marker coordinates, route orientation, intended altitude/speed, payload profile, and route-manifest version.
3. **Generate the route:** create the parallel corridor legs, fixed entry leg, turnaround margins, takeoff, RTL/LAND, geofence, and rally/safety points. Save the canonical manifest and stack-specific plan.
4. **Review and validate the plan:** inspect the map and terrain/obstacle profile, calculate route length and estimated reserve, check heading/altitude/speed/leg spacing, confirm payload settings, run the plan through SITL or an offline validator, and record the route hash.
5. **Commission the equipment:** connect the FC, RC, GCS, companion, camera, and LiDAR on the bench. Record firmware/parameters, sensor serials, calibration IDs, clock status, storage headroom, and network addresses. Start logging before enabling payload streams.
6. **Upload and read back:** upload mission, geofence, and rally points; verify ACKs; download/read back; normalize and compare to the canonical manifest. Do not arm if the plan, home, boundary, route hash, or payload profile is not the intended one.
7. **Arm and take off under supervision:** complete the preflight checklist, arm in the designated manual/assisted mode, take off to a safe height, verify attitude/position/telemetry/payload health, and only then start the supervised mission.
8. **Execute and monitor:** watch the aircraft, RC link, GCS link, battery, GNSS/estimator, geofence, mission item, track, altitude, speed, heading, storage, LiDAR health, RGB capture, and timestamp quality. The pilot remains ready to leave mission mode.
9. **Pause or abort when required:** use HOLD/LOITER or the validated pause action for a temporary interruption. Use manual takeover, RTL, or LAND for people/vehicle intrusion, unsafe weather, estimator/GNSS fault, low battery, lost link, obstacle, geofence concern, or payload condition that makes the record unusable. Record the event before resuming.
10. **Return, land, and disarm:** complete the planned RTL/LAND or pilot-controlled recovery, confirm touchdown and motor disarm, and do not approach until the aircraft is safe.
11. **Close and accept the record:** stop payload streams cleanly, save FC/GCS/companion logs, write checksums, verify file completeness and mission identity, run coverage/timing/metadata checks, and mark the survey accepted, rejected, or requiring a targeted re-flight.

#### Preflight checklist

- [ ] Site permission, institutional safety review, applicable operating requirements, remote pilot, spotter, weather/wind limits, and exclusion zone are confirmed. These are planning gates, not claims that approval already exists.
- [ ] Survey ID, site boundary, local frame, marker coordinates, route version, route hash, mission plan, firmware, parameters, and payload profile are the intended versions.
- [ ] Mission, geofence, and rally/safety points are uploaded, acknowledged, read back, and visually checked. Home and RTL/landing destinations are suitable.
- [ ] Route altitude reference, altitude, speed, heading, leg spacing, turnaround margin, camera settings, LiDAR profile, trigger/timing method, and expected coverage are recorded.
- [ ] FC pre-arm/readiness checks pass; GNSS/estimator, compass/IMU, battery monitor, vibration, storage, and sensor health have no unexplained warnings.
- [ ] RC transmitter, manual takeover switch, RTL/LAND switch, GCS link, telemetry range, and operator display are working. The pilot knows the immediate abort action.
- [ ] Companion, camera, LiDAR Ethernet, payload power, clock/PTP or timing fallback, storage headroom, and acquisition service are healthy. Logging starts before the mission.
- [ ] Props, mount, cable strain relief, payload CG, battery retention, connectors, and sensor field of view are physically checked. Reference markers are visible and in place.

#### In-flight checklist

- [ ] Pilot maintains visual/operational awareness and can take over without waiting for the companion or GCS.
- [ ] Monitor flight mode, armed state, track, mission item, altitude, speed, heading, GNSS/estimator, battery, RC link, GCS link, geofence, and return reserve.
- [ ] Monitor payload heartbeat/health, packet/frame counters, storage headroom, clock/timestamp quality, camera sequence, and LiDAR valid-return status.
- [ ] Mark every HOLD/PAUSE, RESUME, manual takeover, mode change, RTL, warning, payload restart, and coverage gap in mission_events.jsonl.
- [ ] Pause/abort for an exclusion-zone intrusion, aircraft/obstacle conflict, unsafe wind/visibility, geofence uncertainty, low battery, link loss, estimator/GNSS fault, unstable altitude/track, or payload data that cannot support acceptance.
- [ ] Do not continue a mission merely to finish a route after a safety threshold or data-quality gate has failed.

#### Postflight checklist

- [ ] Aircraft is landed, disarmed, motor-safe, and physically inspected before data handling.
- [ ] Mission end, landing, disarm, payload stop, and any faults are recorded with timestamps.
- [ ] FC log, GCS/MAVLink log, companion log, camera files/index, LiDAR raw/normalized files, health log, and mission events are closed without open/partial files.
- [ ] The deployed mission read-back, route hash, survey ID, firmware/parameter set, sensor serials, calibration IDs, clock status, and operator notes are saved.
- [ ] File counts, sequence ranges, packet/segment counters, storage errors, checksums, and time ranges are checked. Any gap is explicitly marked.
- [ ] A backup copy is made before processing. No source raw packet, image, pose, or autopilot log is overwritten by a derived product.

#### Survey-acceptance checklist

- [ ] Survey identity and route identity match: survey ID, site, mission hash, route manifest, deployed plan, frame convention, units, and calibration IDs are consistent.
- [ ] The executed route contains every required leg and entry/exit; coverage mask shows no gap exceeding the approved policy and no unplanned route excursion.
- [ ] Track, altitude, speed, heading, and timing residuals are within the approved measured limits, or the deviation and its effect are recorded for review.
- [ ] RGB frame sequence and image-quality checks pass; LiDAR frame/segment sequence, valid-return/health checks, and packet-loss accounting pass; no stream is silently filled in.
- [ ] FC pose, camera, LiDAR, and companion clocks have known clock domains and quality flags; synchronization uncertainty is within the fusion/processing gate or the record is rejected for change comparison.
- [ ] Marker visibility/registration and local-frame residuals meet the processing investigation's threshold, or the result is labeled non-comparable.
- [ ] Metadata validation passes, including time zone/UTC convention, coordinate frame, altitude reference, sensor variant, profile, firmware, and operator/site fields.
- [ ] A named reviewer records ACCEPTED, REJECTED, or TARGETED RE-FLIGHT in acceptance.json with reasons and links to the relevant evidence.

These checklists are proposed controls. They do not replace a flight-test plan, site permission, pilot judgment, manufacturer guidance, institutional approval, or field validation.

### 4.6 Fallback workflow

If PX4/QGC cannot be used:

1. Freeze the same stack-neutral route_manifest.json, site boundary, markers, route orientation, altitude, speed, payload settings, and safety policy.
2. Use ArduCopter and Mission Planner to draw/import the polygon, generate the grid, set altitude/speed/yaw, add takeoff and RTL/LAND, configure fence/rally points, and save the native mission plus KML review copy.
3. Add distance triggering only if the actual camera path supports it. Otherwise run companion capture and record the limitation in payload_config.json.
4. Upload via MAVLink, read back, normalize commands/frames/coordinates, compare to the canonical manifest, and record firmware/parameter version.
5. Validate pause/resume with the exact configuration. Use rewind-on-resume only after proving that the preceding leg is not skipped and payload coverage remains valid.
6. Use MAVProxy as a headless link logger/forwarder if needed. It must not be the sole safety monitor for a first outdoor flight.

If neither stack has been selected or validated, the fallback is a **SITL or bench-only demonstration**: generate the plan, simulate the state machine, replay synthetic/published payload logs, and demonstrate coverage/metadata acceptance without operating the aircraft.

## 5. Development sequence and dependencies

1. **Central flight-stack decision:** select Pixhawk board, frame, PX4 or ArduPilot release, GCS version, RC/telemetry, and parameter ownership. Record firmware hash and GCS build.
2. **Route-manifest schema:** define stack-neutral JSON, coordinate-frame names, units, route hash, mission ID, markers, and plan normalization.
3. **SITL mission loop:** upload/read back; run takeoff/survey/hold/resume/RTL/land; inject link loss and battery conditions; save telemetry/logs.
4. **Bench FC/GCS integration:** verify USB/telemetry, preflight status, parameter backup, plan/fence/rally upload, RC switch, ACKs, log download, and mission-event recording with motors disabled.
5. **Bench payload integration:** connect companion, RGB camera, and picoScan150 path when available; verify packet/frame counts, timestamps, mission ID, storage headroom, and record closure.
6. **Controlled flight tuning:** conduct approved manual/position-hold flights first. Measure hover, stopping, turning, GNSS/estimator, battery, link, and altitude behavior.
7. **Single-leg supervised test:** use a short route, low speed, large clearance, pilot takeover, and known surface. Confirm payload record and coverage before adding legs.
8. **Full corridor demonstration:** use approved site plan, markers, fence/rally points, weather limits, checklists, and operator/spotter assignments.
9. **Repeatability test:** repeat the same mission under documented conditions, register both in the local survey frame, and report route/altitude/heading/time differences with uncertainty.
10. **Evidence package:** retain canonical plan, deployed plan, read-back, logs, payload record, quality metrics, rejected records, and reviewer decision. SITL/public-data results must be labeled software demonstration, not UAV field validation.

Dependencies: Investigation 01 owns aircraft/power; Investigation 02 owns sensor/acquisition; Investigation 03 owns RGB/position/timing; Investigation 04 owns companion/storage/telemetry. Processing/reporting investigations consume this manifest and acceptance contract.

## 6. Verification tests and success measures

All numerical limits below are proposed starting targets. Record firmware/GCS, plan and route hashes, site/weather, battery, payload profile, and whether the run is simulated, bench, controlled flight, or field demonstration.

### 6.1 Required mission and route tests

| Test | Method | Proposed pass condition |
|---|---|---|
| Plan integrity/read-back | Create manifest and .plan; upload mission/fence/rally; download and normalize frames, coordinates, parameters, and command order. Repeat with a changed waypoint and invalid frame. | Read-back matches canonical hash/normalized fields; changed, unsupported, or invalid item is reported before arm; planned home/fence/rally are reviewed. |
| Route repeatability | Run in SITL twice, then conduct two approved supervised passes over marked test area. Compare waypoint order, local ENU track, altitude, speed, yaw, timing, and payload coverage. | No missing leg; proposed 95th percentile cross-track <= 0.5 m, altitude <= 0.5 m, speed <= 0.2 m/s, yaw <= 10 degrees, and no unexplained gap over two selected along-track sample intervals. Replace limits after measurement. |
| Pause/resume | HOLD at a predetermined leg, wait at least 30 s, resume with selected stack action, and repeat after a short pilot diversion. Mark interruption in payload and telemetry. | Pilot retains control; mission state is unambiguous; resume does not silently skip required coverage; gap/restart is recorded; if gap violates policy, reject or deliberately re-fly leg. Verify ArduPilot rewind/MIS_RESTART or PX4/QGC release-specific flow. |
| Lost GCS/telemetry link | SITL first, then bench/no-prop link interruption. Keep RC available and interrupt GCS/MAVLink longer than configured timeout. Restore and inspect logs. | Configured data-link action occurs within timeout; pilot can take over; payload failure is flagged; reconnect does not duplicate/corrupt record. No outdoor test until understood. |
| Low battery | Simulate/inject battery state in SITL; only then perform controlled reserve test. Exercise warning, return, and emergency thresholds with payload load. | Warning/return/landing match configuration; approved reserve remains for return/landing; payload closes/marks record; no unapproved mission continuation after emergency threshold. |
| Incomplete coverage | Remove one leg, create telemetry gap, drop LiDAR segments/RGB frames, or stop companion in simulated/bench record. | coverage.json identifies missing leg/time/stream; acceptance rejects when gap exceeds policy; no interpolation is presented as measured coverage; re-flight can target missing region after review. |
| Invalid metadata | Mismatch survey ID, route hash, frame, serial, firmware, calibration, timestamps, units, or planned/deployed mission hash. | Parser rejects or explicitly marks invalid before change comparison. Unknown frame, clock domain, or mission identity is never accepted as a repeat survey. |

### 6.2 Safety and interface tests

- **Manual takeover:** in SITL and approved controlled flight, switch from mission to designated manual/position mode, confirm response, then exercise RTL and land. Measure reaction time and stopping distance for geofence margin.
- **Geofence:** test an intentionally small simulated boundary and verify configured action; confirm route, turnaround, RTL path, and rally/home locations do not intersect an unsafe boundary. PX4 documents that geofences apply in manual and mission modes and that action occurs after breach, so margin is required. [PX4 Geofence](https://docs.px4.io/main/en/flying/geofence), accessed 2026-09-19; [PX4 Safety Configuration](https://docs.px4.io/main/en/config/safety), accessed 2026-09-19.
- **Mission feasibility:** upload plans with missing takeoff/landing where required, distant first waypoint, fence conflict, unsupported command, and invalid altitude/frame. Confirm GCS and FC surface the problem before takeoff.
- **Payload failure isolation:** stop LiDAR acquisition, unplug payload Ethernet, remove storage, stop RGB, and lose clock synchronization while disarmed or in SITL. Confirm flight control remains controllable and record becomes degraded/rejected.
- **Clock/event correlation:** compare FC events, camera sequence, LiDAR sequence, companion timestamps, and marker/LED/trigger events. Investigation 02 proposes a measured timing gate; Investigation 03 owns the final threshold. A proposed initial target is <= 5 ms residual only when the payload claim requires it; otherwise report measured uncertainty.
- **Recovery/data closure:** interrupt acquisition only in a bench copy. Confirm journaling/checksums and explicit incomplete-record status; never infer a complete survey from partial files.

## 7. Cost, mass, power, or resource implications

- PX4, QGroundControl, ArduPilot, Mission Planner, MAVProxy, MAVLink libraries, and SITL are software resources rather than payload purchases. Record license obligations if project code or a redistributable product is later built around them.
- The baseline needs an operator laptop/tablet, compatible RC transmitter/receiver, tested telemetry, storage for logs, safe test site, and SITL/bench/flight-validation time. Availability is not verified.
- The companion must budget CPU, Ethernet bandwidth, storage write rate, and power for picoScan150, RGB capture, MAVLink logging, and checksums simultaneously. Investigation 02's proposed raw-capture target and Investigation 04 storage test govern mission duration.
- Altitude, speed, route length, turn behavior, and payload configuration control battery reserve. Do not use GCS duration estimates alone; compare with measured current and conservative return/landing reserve.
- The picoScan150 remains challenge-supplied if selected and is excluded from the approximately $1,000 initial-build purchase target. GCS laptop, RC/telemetry, companion, storage, camera, regulator, mount, and borrowed equipment remain separate budget/availability decisions.

## 8. Risks, open decisions, and fallback

### 8.1 Safety constraints

- A qualified/assigned remote pilot must remain able to control the aircraft manually. A spotter should monitor airspace, people, vehicles, and obstacles while the operator monitors GCS and payload.
- Establish a physical exclusion area around takeoff, landing, return, and survey route. Stop or hold/RTL/land for people, vehicles, animals, aircraft, obstacles, unsafe weather/wind, GNSS/estimator warning, battery warning, link loss, or payload obstruction.
- Use pre-arm checks, RC-loss behavior, GCS/data-link loss behavior, battery thresholds, geofence action, RTL/land altitude/destination, and manual mode switches that match the aircraft/site. Record and test values; do not rely on undocumented defaults.
- Use a geofence with stopping/position-error margin, not a boundary coincident with people, roads, buildings, or the survey polygon. Review RTL path and rally/landing points, including lost-position cases.
- Do not use motor kill or flight termination as a routine test. They are emergency actions with severe consequences and require the approved safety procedure.
- Keep first demonstration low speed and conservative altitude with short route, clear landing area, and manual takeover. Do not add offboard guidance, dynamic avoidance, or automatic re-flight until waypoint baseline is accepted.
- Describe these as planned mitigations only. Do not state that the project is approved for autonomous flight, that the site is authorized, or that the vehicle is safe without field evidence.

### 8.2 Decisions required from the integration editor

| Decision | Needed from | Why it matters |
|---|---|---|
| PX4 vs ArduPilot and pinned release | Investigation 01 + integration lead | Determines parameter names, commands, logs, failsafe semantics, GCS workflow, and resume behavior. |
| Pixhawk board, frame, RC, telemetry, manual modes | Investigation 01 | Determines ports, mode authority, RTL/geofence, tuning, flight envelope, battery reserve. |
| Canonical route schema and frames | Investigations 03/05/06 | Prevents WGS84, UTM, local ENU, body FRD, camera, and LiDAR ambiguity. |
| Altitude reference and speed | Investigations 01/02/03/05 | Couples obstacle clearance, LiDAR sampling, camera blur/overlap, battery, track repeatability. |
| Sensor profile, scan orientation, network topology | Investigations 01/02/04 | Controls payload geometry, power, Ethernet, coverage, storage, duration. |
| Camera trigger and timing source | Investigations 03/04/05 | Determines FC trigger versus companion capture and timestamp gate. |
| Marker/reference strategy and GNSS/RTK need | Investigations 03/05/06 | Determines repeat registration and whether ordinary GNSS is adequate. |
| Payload failure response | Investigations 02/04/05 | Defines whether lost payload pauses/aborts/returns or only marks degraded record; aircraft must remain controllable. |
| Survey acceptance thresholds | Investigations 02/03/06/07/08 | Converts coverage, pose, timing, packet, image, and geometry evidence into accept/reject. |
| MAVLink security/network isolation | Investigation 04 + integration lead | Determines signing, routing, Ethernet isolation, and protection from unintended commands. |
| Site/airspace/test approval path | Project lead/institution | A software plan cannot substitute for permission, pilot qualification, safety review, or field authorization. |

### 8.3 Unresolved assumptions

1. Final Pixhawk controller and whether firmware is PX4 or ArduPilot.
2. Exact stable firmware, GCS build, parameters, and supported command subset.
3. Telemetry path, range, latency, link-loss timeout, RC failover, MAVLink signing, and network topology.
4. Measured payload mass, CG, power, current, vibration, turn radius, stopping distance, flight time, wind envelope, and battery reserve.
5. picoScan150 variant, profile, IP setup, clock/PTP behavior, mount orientation, and logging throughput.
6. RGB trigger/capture feedback, frame rate, timestamp semantics, exposure, and camera-to-body calibration.
7. Site polygon, terrain, obstacles, launch/recovery area, markers, permissions, airspace, weather limits, pilot, and spotter.
8. Whether ordinary GNSS track repeatability meets change-detection needs or surveyed markers/RTK are required.
9. Proposed coverage, timing, repeatability, packet-loss, and metadata thresholds have not been measured.
10. QGC .plan and ArduPilot waypoint artifacts may represent complex surveys differently; canonical manifest and read-back normalization are required.

### 8.4 Fallback hierarchy

1. **Preferred:** PX4 + QGC supervised waypoint/corridor mission with companion payload logger.
2. **Stack fallback:** ArduCopter + Mission Planner, retaining the same route manifest and acceptance products.
3. **GCS/link fallback:** MAVProxy for telemetry forwarding/logging plus a validated operator GCS.
4. **Payload fallback:** RGB-only or synthetic/public-data processing demonstration, clearly labeled; no claim that picoScan150 was flown or field coverage achieved.
5. **No-flight fallback:** SITL plus bench payload capture/replay demonstrating state/command, lost-link, low-battery, pause/resume, incomplete-coverage, and invalid-metadata tests.

## 9. Sources

The following are direct official project or manufacturer-maintained documentation URLs used for this brief. All were accessed 2026-09-19.

1. PX4, [project documentation and license](https://github.com/PX4/PX4-Autopilot/blob/main/docs/en/index.md).
2. PX4, [Missions](https://docs.px4.io/main/en/flying/missions).
3. PX4, [Safety (Failsafe) Configuration](https://docs.px4.io/main/en/config/safety).
4. PX4, [Geofence](https://docs.px4.io/main/en/flying/geofence).
5. PX4, [Return Mode](https://docs.px4.io/main/en/flight_modes/return).
6. PX4, [Flight-readiness/preflight checks](https://docs.px4.io/main/en/flying/pre_flight_checks).
7. PX4, [MAVLink Messaging](https://docs.px4.io/main/en/mavlink/).
8. PX4, [Serial Port Configuration](https://docs.px4.io/main/en/peripherals/serial_configuration).
9. PX4, [Raspberry Pi Companion with Pixhawk](https://docs.px4.io/main/en/companion_computer/pixhawk_rpi).
10. PX4, [Camera Architecture/Integration](https://docs.px4.io/main/en/camera/camera_architecture).
11. PX4, [CameraTrigger message](https://docs.px4.io/main/en/msg_docs/CameraTrigger).
12. QGroundControl, [Plan View](https://github.com/mavlink/qgroundcontrol/blob/master/docs/en/qgc-user-guide/plan_view/plan_view.md).
13. QGroundControl, [Survey pattern](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/plan_view/pattern_survey.html).
14. QGroundControl developer guide, [Plan File Format](https://github.com/mavlink/qgc-dev-guide/blob/master/en/file_formats/plan.md).
15. QGroundControl, [repository, supported vehicles, and license information](https://github.com/mavlink/qgroundcontrol).
16. ArduPilot, [ArduCopter Auto mode](https://ardupilot.org/copter/docs/auto-mode.html).
17. ArduPilot, [Mission Planner overview](https://ardupilot.org/planner/docs/mission-planner-overview.html).
18. ArduPilot, [Mission Planner installation/platform notes](https://ardupilot.org/planner/docs/mission-planner-installation.html).
19. ArduPilot, [Mission planning](https://ardupilot.org/planner/docs/common-mission-planning.html).
20. ArduPilot, [Camera control and auto missions in Mission Planner](https://ardupilot.org/planner/docs/common-camera-control-and-auto-missions-in-mission-planner.html).
21. ArduPilot, [Mission commands](https://ardupilot.org/copter/docs/common-mavlink-mission-command-messages-mav_cmd.html).
22. ArduPilot, [Mission rewind on resume](https://ardupilot.org/copter/docs/common-mission-rewind.html).
23. ArduPilot, [Battery failsafe](https://ardupilot.org/copter/docs/failsafe-battery.html).
24. ArduPilot, [Fences](https://ardupilot.org/copter/docs/common-geofencing-landing-page.html).
25. ArduPilot, [GPLv3 license](https://ardupilot.org/dev/docs/license-gplv3.html).
26. MAVLink, [Mission (Plan) Protocol](https://mavlink.io/en/services/mission.html).
27. MAVLink, [Common Message Set](https://mavlink.io/en/messages/common.html).
28. MAVLink, [Standard Modes Protocol](https://mavlink.io/en/services/standard_modes.html).
29. MAVProxy, [overview](https://ardupilot.org/mavproxy/index.html).
30. MAVProxy, [telemetry forwarding](https://ardupilot.org/mavproxy/docs/getting_started/forwarding.html).
