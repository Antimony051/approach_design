# PaveWatch investigation 01: flight platform, power, and mechanical integration

**Research status:** preliminary design research; no component has been purchased, weighed, powered, or flight-tested by this project.

**Price date:** USD planning prices and product availability were checked on 2026-09-19. Prices exclude shipping, tax, and any university purchasing overhead and can change. The picoScan150 is treated as a challenge-supplied sensor, not a capstone purchase.

## 1. Scope and recommendation

### Recommendation

Use the **Holybro X500 v2 PX4 Development Kit with Pixhawk 6C, M10 GPS, and 915 MHz SiK telemetry** as the initial PaveWatch platform. The current manufacturer listing is $579 for the Pixhawk 6C/M10/915 MHz option. It includes the carbon-fiber X500 frame, four motors and 20 A ESCs, power distribution board, propellers, Pixhawk 6C with PM02 V3 power module, M10 GPS, and SiK telemetry radio. The platform has a published 500 mm wheelbase, a 215 mm landing-gear height, a 250 mm two-rod rail mounting system, companion-computer mounting holes, an adjustable battery board, and a manufacturer payload figure of 1,500 g without the battery at 70% throttle. The older X500 documentation also gives a more conservative approximately 1 kg payload figure with a 4S 5,000 mAh battery; that lower value is the planning limit until the actual build is weighed and thrust/current are measured.

The proposed initial payload is a SICK picoScan150, a Raspberry Pi 5 computer, Raspberry Pi Camera Module 3, storage, a separate 5 V regulator, and a rigid adjustable mount. The estimated complete takeoff mass is approximately **1.8–1.9 kg including a 4S 5 Ah battery**, with the largest uncertainties being the actual X500 kit mass, the SICK system plug/cables, and the payload mount. This leaves a nominal payload margin, but it is not a measured performance result.

### Fallback

Use the **Holybro S500 V2 Development Kit with Pixhawk 6C and 915 MHz SiK telemetry** if the X500 is unavailable or the S500 is available to borrow. It is listed by Holybro at $519 and includes the Pixhawk 6C, PM02 V3 power module, M10 GPS, SiK telemetry, frame, four 2216 KV920 motors, four 20 A ESCs, and 1045 propellers. Holybro publishes approximately 915 g with everything installed, a 1,500 g payload figure without the battery at 70% throttle, and a 4S 3,000–5,000 mAh battery recommendation. It has an adjustable battery mount and is a viable integration fallback, but it has less documented room for a custom sensor/computer arrangement and its published all-installed mass needs to be reconciled with the X500 budget before adding payload.

### Platform comparison

| Platform | Current price and included electronics | Verified published specifications relevant to PaveWatch | Decision |
|---|---:|---|---|
| **Holybro X500 v2 PX4 Development Kit, Pixhawk 6C/M10/915 MHz** | **$579**; Pixhawk 6C, PM02 V3, M10 GPS, 915 MHz SiK telemetry, X500 frame, four motors, four 20 A ESCs, PDB, six propellers | 500 mm wheelbase; 215 mm landing gear; 250 mm dual-rod rail; companion-computer holes; adjustable battery board; published 1,500 g payload without battery at 70% throttle; published no-payload hover around 18 minutes with a 5,000 mAh battery | **Recommended.** Best balance of price, mounting access, and mass margin. |
| **Holybro S500 V2 Development Kit, Pixhawk 6C/M10/915 MHz** | **$519**; Pixhawk 6C, PM02 V3, M10 GPS, 915 MHz SiK telemetry, S500 frame, four motors, four 20 A ESCs, 1045 propellers | Approximately 915 g with everything installed; 4S 3,000–5,000 mAh 20C+ XT60 LiPo recommendation; published 1,500 g payload without battery at 70% throttle; published no-payload hover around 18 minutes with a 5,000 mAh battery | **Fallback.** $60 cheaper and adequate on paper; fewer integration details are published for the custom sensor/mount arrangement. |
| **Holybro X650 Development Kit, Pixhawk 6C/M10/915 MHz** | **$1,109**; Pixhawk 6C, PM02 V3, M10 GPS, 915 MHz SiK telemetry, four larger motors/45 A ESCs, PDB, 650 mm frame | 2,000 g full kit without battery; 4.3 kg payload without battery, 3.5 kg with a 750 g battery, 3.1 kg with a 1,200 g battery; 6S 5,000–12,000 mAh recommendation; 30-minute no-payload hover claim with 6S 10 Ah | **Not an initial purchase.** It is a credible borrowed-aircraft or future-upgrade option, but it consumes more than the approximate $1,000 target before the sensing payload. |

The X500 and S500 are Pixhawk-compatible/equivalent development platforms because both include the Pixhawk 6C and use PX4 or ArduPilot-compatible flight-control hardware. The 915 MHz option is the relevant North American listing shown by Holybro; the team should confirm the radio configuration and local operating constraints before purchase or flight.

## 2. Evidence and assumptions

### Status labels used here

- **Available to borrow:** a university drone, compatible transmitter/receiver, batteries, charger, lab scales, vibration meter, or test area if Mississippi State or the capstone laboratory makes one available. None is confirmed in the repository.
- **Proposed:** the X500 layout, separate payload power branch, rigid two-axis mount, and Pi-based acquisition computer.
- **Planned purchase:** items in the cost table that are not part of a borrowed platform or the supplied picoScan150.
- **Estimated:** engineering allowances used for early mass, current, cost, and center-of-gravity calculations.
- **Measured:** none. Manufacturer claims are not project measurements.

### Hardware and source assumptions

1. The team is selected and receives a picoScan150 and its challenge accessories. SICK states that selected SICK$10K teams are supplied a picoScan150 and accessories; the sensor is therefore shown as $0 in the capstone purchase budget, not as a free market purchase.
2. The exact picoScan150 variant, system plug, installed options, and cable lengths are unknown. The mechanical and power design uses the common values in the SICK operating instructions and allocates extra mass for the plug and cables.
3. The SICK operating instructions give 220 g for the sensor without its system plug and 60 mm x 60 mm x 82 mm dimensions. They give 4.5 W typical consumption at 24 V with continuous scan data and no output load. The operating instructions require an external slow-blow fuse rated between 1 A and 3 A at the supply-cable start. The product documentation describes the supply as 9–30 V DC; a 4S pack is nominally 14.8 V and 16.8 V fully charged, so direct sensor power is within that stated range. Verify the received product label and documentation before energizing it.
4. The initial computer is a Raspberry Pi 5 2 GB or an equivalent borrowed Pi 5. Raspberry Pi documents the Pi 5 as having Gigabit Ethernet, two camera/display MIPI ports, and a 5 V/5 A supply interface. The 2 GB price is budgeted at $65 as a conservative planning allowance after the manufacturer's published 2025 price revision; actual purchase price and availability must be checked again. A Pi 5 4 GB is a later upgrade if the acquisition workload needs more memory.
5. The camera is a standard Raspberry Pi Camera Module 3, not an industrial camera. The manufacturer lists it from $25 and specifies a 12 MP IMX708 sensor, autofocus, 75-degree diagonal field of view for the standard version, CSI-2 output, and a 25 mm x 24 mm x 11.5 mm module size. Actual camera mass with cable and protection is an allowance, not a measurement.
6. A 4S 5,000 mAh pack is used for the first budget because it is in the X500/S500 recommendation range. A current supplier listing gives $79.99 for a 4S 14.8 V 5,000 mAh XT60 battery; its mass is not listed there, so 500 g is a conservative design allowance until a selected pack is weighed. The kit's published hover-time values were obtained without an additional payload and must not be treated as PaveWatch flight-time validation.
7. The radio transmitter/receiver, charger, and a ground-station laptop may be borrowed. If they are not borrowed, the cost table includes a low-cost RadioMaster Pocket transmitter and receiver allowance. A transmitter/receiver purchase must be selected as a matched protocol pair and verified with the Pixhawk 6C before flight.

### Key verified interfaces

- Pixhawk 6C uses 5 V power inputs and has two power inputs, three telemetry ports, two GPS ports, an I2C port, two CAN buses, PWM motor outputs, and dedicated SBUS/PPM/DSM RC inputs. Holybro specifies the telemetry-port 5 V output limits as 1.5 A combined for the relevant port groups. The companion computer and picoScan150 must not be powered from a Pixhawk telemetry-port 5 V pin.
- The Holybro PM02 V3 supplied with the Pixhawk 6C accepts 2S–12S input, outputs regulated 5.2 V at up to 3 A, and reports battery current and voltage to the flight controller through its six-pin cable. Its current rating is for the flight-controller power path; it is not the payload computer regulator.
- The picoScan150 Ethernet connector is a four-pin M12 D-coded connection: TX+, RX+, TX−, and RX−. The sensor power/I/O connector is a separate M12 A-coded connection. The data link is therefore sensor-to-computer Ethernet, not a Pixhawk serial sensor connection.
- A separate time association is required. The picoScan150 documentation exposes sensor timing fields and optional IMU data; Pixhawk supplies flight logs/MAVLink time; the computer supplies camera timestamps and host receipt timestamps. The final timestamp strategy belongs jointly to investigations 02, 03, 04, and 05.

## 3. Proposed components and budgets

### Initial purchase/cost budget

This is a planning budget for the recommended X500 platform. It does not include a market purchase of the picoScan150. The target is approximately $1,000, not a fixed quotation.

| Item | Status | Planning cost | Mass allowance | Power/design note | Evidence or reason for allowance |
|---|---|---:|---:|---|---|
| Holybro X500 v2 development kit, Pixhawk 6C/M10/915 MHz | Planned purchase, or borrow | $579 | 800 g allowance for complete ready-to-fly kit before battery; **unmeasured** | Includes propulsion, Pixhawk, GPS, telemetry, PM02, PDB, and frame hardware | Current Holybro listing; its 610 g published X500 base/frame figure is not assumed to equal the complete kit mass. |
| 4S 5,000 mAh XT60 LiPo | Planned purchase | $80 | 500 g allowance; **unmeasured for selected pack** | 14.8 V nominal, 16.8 V full; propulsion battery and direct picoScan input | Current supplier listing at $79.99; Holybro recommends 4S 3–5 Ah on these platforms. |
| Raspberry Pi 5, 2 GB | Planned or borrow | $65 allowance | 80 g including board, cooler, and retention; **unmeasured** | Dedicated 5 V rail; reserve up to 25 W at the rail | Raspberry Pi official price table and power documentation; $65 is a conservative current planning allowance. |
| Raspberry Pi Camera Module 3 standard | Planned or borrow | $25 | 15 g with cable/protection allowance; **unmeasured** | Powered through the Pi CSI path; no separate battery branch | Official Raspberry Pi product listing gives $25 starting price. |
| 128–256 GB high-endurance microSD or small USB SSD | Planned | $15–$40 | 10–80 g depending on choice; **unmeasured** | Storage power is included in the Pi rail allowance | Planning allowance; final storage choice belongs to investigation 04. |
| 5 V, 5 A continuous buck regulator, input rated above 16.8 V, plus output LC filter, fuse, and low-voltage cutoff/enable | Planned | $35–$55 | 60 g allowance; **unmeasured** | Dedicated payload rail; do not use PM02 or Pixhawk accessory 5 V for this load | Raspberry Pi specifies a 5 V/5 A supply for full peripheral capability; exact regulator is not selected. |
| picoScan150 bracket, two-axis adjustment plate, standoffs, vibration isolators, secondary tether, fasteners, strain relief | Planned fabrication | $45–$70 | 100 g allowance; **unmeasured** | Sensor is rigidly attached; computer isolation is separate from sensor alignment | SICK's official aluminum bracket is 63 g before the custom adjustment structure; a printed/plate mount is a proposed lower-cost substitute. |
| LiDAR system plug/cables and shielded Ethernet cable | Challenge accessory if supplied; otherwise allowance | $0 if supplied; reserve $50–$75 | 60 g allowance; **unmeasured** | 9–30 V fused sensor branch; M12 power and D-coded Ethernet | Exact supplied accessory set and cable lengths are unknown. Do not order until confirmed. |
| LiPo charger/balancer | Borrow preferred; otherwise planned | $0 borrowed; $40–$60 purchase allowance | 0 g airborne | Ground equipment only | Must be confirmed with the selected battery chemistry and cell count. |
| RC transmitter and receiver | Borrow preferred; otherwise planned | $0 borrowed; about $85 purchase allowance | 10 g airborne receiver allowance | Receiver uses a Pixhawk-supported RC input/protocol; transmitter remains the manual safety control | RadioMaster Pocket is listed at $64.99 and a small receiver is listed around $19; protocol pairing is still open. |
| Spare propellers, straps, fuses, connectors, wiring, and protective covers | Planned | $25–$40 | 50 g airborne allowance | Includes service loops and spare consumables | Planning allowance. |
| **Expected total if radio/charger are borrowed and picoScan accessories are supplied** |  | **approximately $869–$954** | Payload/mass allowances below |  | Leaves margin for shipping/tax and small integration parts. |
| **Expected total if radio, charger, and LiDAR cable allowance are purchased** |  | **approximately $1,044–$1,174** |  |  | Use borrowed university equipment, the lower storage/mount choice, or a borrowed flight platform to keep the initial build near $1,000. |

The budget remains realistic only if the picoScan150 is supplied, the flight kit includes the listed flight electronics, and at least the charger or radio is borrowed. A Jetson, premium RTK receiver, industrial camera, X650, or gimbal is not a mandatory initial purchase.

### Preliminary mass and center-of-gravity budget

The following is a design calculation, not a scale measurement. Coordinates use an arbitrary origin at the X500 centerline near the main plates; **+x is forward, +y is right, and +z is upward**. The flight controller, motors, and frame are assumed centered. The battery remains movable on the adjustable tray to correct the actual measured CG.

| Component | Mass used | Preliminary x offset | Preliminary y offset | z/layout note | Status |
|---|---:|---:|---:|---|---|
| X500 kit: frame, landing gear, motors, ESCs, PDB, Pixhawk 6C, PM02, GPS, telemetry, props, fasteners | 800 g | 0 mm | 0 mm | Main plates and FC near the body center | Conservative allowance; published X500 figures are not a complete project weighing. |
| 4S 5 Ah battery | 500 g | 0 mm, adjustable | 0 mm | Top/upper adjustable battery board | Allowance; weigh selected pack. |
| picoScan150 sensor + system plug/cable allowance | 280 g | 0 mm | 0 mm | Underside centerline, below landing gear | 220 g sensor is from SICK; plug/cable allowance is unknown. |
| Raspberry Pi 5 + active cooling + storage/enclosure | 80 g | −25 mm | 0 mm | Rear/upper platform, airflow protected | Allowance; weigh final enclosure. |
| Camera Module 3 + CSI cable/protection | 15 g | +40 mm | 0 mm | Forward lower platform, downward or slight-forward view | Allowance; lens and protective window are unresolved. |
| Custom sensor mount, SICK bracket interface, isolators, secondary tether | 100 g | 0 mm | 0 mm | Rigid to sensor; adjustment pivots above sensor | Allowance; fabricate and weigh. |
| Dedicated regulator, fuses, wiring, Ethernet, and strain relief | 100 g | −25 mm | 0 mm | Battery/PDB side, payload branch separated from compass | Allowance; connector choice may change it. |
| RC receiver and antenna | 10 g | 0 mm | 0 mm | Upper plate, antenna clear of carbon and power wiring | Allowance; borrow/purchase decision open. |
| **Preliminary takeoff mass** | **1,885 g** |  |  | Includes battery and payload; no project measurement | **Estimated** |

With the illustrative offsets above, the lateral CG remains on the centerline and the longitudinal moment is approximately:

`(-25 mm x 80 g) + (40 mm x 15 g) + (-25 mm x 100 g) = -4,600 g·mm`

Dividing by 1,885 g gives an estimated **x CG of −2.4 mm** (about 2–3 mm aft of the assumed origin). This is not a claim that the assembled aircraft has that CG. The integration acceptance check should be a scale/knife-edge or suspension check with the actual battery, sensor, cables, and camera installed; target the measured CG within **±10 mm of the motor-plane center** in x and y before powered hover testing. If the Pi or camera changes sides, move the battery laterally rather than adding ballast.

The X500's published older approximately 1 kg payload figure with a 4S 5 Ah battery leaves substantial nominal mass margin for the approximately 585 g of sensor/computer/camera/mount/regulator/receiver payload above, but thrust, current, vibration, and control authority are unmeasured. If the actual complete kit is more than the 800 g allowance or if a larger camera/enclosure is selected, repeat the calculation before flight.

## 4. Interfaces and data flow

### Textual mechanical layout for the integration drawing

1. **Main frame and propulsion:** Draw the X500 as an X quad with the 500 mm motor-to-motor wheelbase, carbon-fiber upper and lower 144 mm plates, four carbon tube arms, and landing gear approximately 215 mm below the body. Show the two 10 mm diameter, 250 mm long rails below/around the payload platform. Keep the LiDAR and camera below the propeller disks and inside the landing-gear envelope; the final clearance must be physically checked with the propellers installed.
2. **Flight controller:** Put the Pixhawk 6C close to the geometric center of the upper/lower plate stack on its recommended vibration-isolating mounting, with the forward arrow aligned to the airframe x axis. Keep the compass/GPS mast away from high-current motor and battery wires. Do not attach the sensor mount to the flight-controller isolation plate.
3. **Battery:** Put the 4S battery on the adjustable battery board, centered over the motor plane. Use two straps and a non-slip pad. Leave at least one battery position available fore/aft for CG correction after the payload is installed.
4. **PicoScan150:** Attach the sensor to a rigid aluminum or carbon interface on the lower platform. The SICK unit is 60 mm x 60 mm x 82 mm and 220 g without the system plug. If using the official SICK bracket, use all five M4 fasteners where practical; SICK's bracket datasheet recommends all five for high shock/vibration applications. The bracket attaches to two orthogonal slotted plates or a small two-axis pivot so pitch and yaw can be adjusted by approximately ±15 degrees during integration. Use locknuts or an approved removable thread locker and a secondary retention tether.
5. **Scan-plane aim:** Orient the picoScan150 scan plane approximately vertical and transverse to the flight direction so the lower portion of the 276-degree scan fan intersects the pavement as a cross-section while forward motion builds along-track coverage. Do not assume the full fan is usable: mask or mechanically clear the arms, landing gear, rail, and propeller-wash region from the intended pavement sector. Final pitch/yaw is a proposed starting setting, not a validated survey geometry.
6. **Camera:** Put the Camera Module 3 on the same lower platform, forward of or adjacent to the LiDAR, with a clear downward view and a small forward look angle only if the RGB investigation requires overlap with the LiDAR pavement sector. Use a rigid camera plate so the camera-to-LiDAR transform does not change after calibration. Do not let the camera bracket cross the LiDAR scan fan.
7. **Computer:** Put the Pi on the platform board or a custom plate above the lower rails, with the board's long axis fore/aft and the connector side facing inward. Use four standoffs, an active cooler, a ventilated splash/dust enclosure, and a removable storage path. The Pi is not a mandatory Jetson substitute for final AI performance; it is the budget acquisition computer. Heavy processing can remain offboard.
8. **Cable routes:** Route the battery lead to the PDB/PM02 through a protected central path. Route a separately fused payload branch along one arm or the inner plate edge, away from compass and GPS wiring. Route the M12 Ethernet cable from the LiDAR to the Pi without tight bends, with connector strain relief and a short service loop. Twist the battery/regulator pair, keep it away from ESC signal wires, and secure every cable so propeller wash cannot move it into a propeller arc.
9. **Calibration references:** Add two reference marks or dowel points on the payload plate and record the measured sensor and camera frames relative to the Pixhawk body frame. Use a level, a flat pavement/planar target, and a known-height target to record mount pitch/yaw and sensor height. Recheck after every mount removal.

### Power tree

```text
4S 14.8 V nominal / 16.8 V full LiPo, XT60
        |
        +-- main fuse / battery monitor / PDB -------------------------+
        |                                                               |
        |                                                               +-- four ESCs -> four motors
        |
        +-- PM02 V3 (2S-12S input, regulated 5.2 V, up to 3 A) ---------+--> Pixhawk 6C POWER1
        |                                                                  `--> Pixhawk GPS, RC receiver,
        |                                                                       SiK telemetry and flight-control accessories
        |
        +-- separate payload fuse + LC filter -> 5 V / 5 A buck regulator
        |                                            |
        |                                            +--> Raspberry Pi 5
        |                                                   `--> Camera Module 3 via CSI
        |                                                   `--> local storage
        |
        `-- separate sensor fuse (slow-blow 1-3 A range; confirm exact value)
             -> picoScan150 power input, 9-30 V accepted by documentation
             `-> picoScan150 M12 D-coded Ethernet -> Raspberry Pi Ethernet
```

The exact fuse values and connector parts must be selected after the received sensor system plug is identified. All payload branches share the battery return at the PDB/star point, but the LiDAR and computer branches are separately filtered and fused. The LiDAR should not draw power from the Pixhawk servo, telemetry, or GPS rails. The computer regulator should be selected for a continuous 5 V/5 A output, input transients at 16.8 V, thermal dissipation, and a controlled startup; its measured ripple at the LiDAR and Pi connectors is an integration acceptance item.

### Power and energy budget

| Load | Rail | Design/current allowance | Evidence and measurement need |
|---|---|---:|---|
| Four motors and ESCs | 4S propulsion branch | Dominant load; no project value yet | Use the manufacturer's no-payload hover result only as a comparison point. Measure battery current during restrained motor test and hover tests. |
| Pixhawk 6C, M10 GPS, RC receiver, SiK telemetry | 5.2 V PM02 output | PM02 capacity is 3 A; reserve 5 W for the whole avionics branch until measured | Holybro PM02 specification; measure rail voltage/current and confirm port limits. |
| picoScan150 | Direct 4S branch, 12.6–16.8 V over normal pack range | 4.5 W typical; plan for up to 17 W if digital outputs are loaded; approximately 0.3 A typical at 14.8 V and 1.2 A at 14.8 V for 17 W | SICK operating instructions; confirm exact variant, output use, startup surge, and actual current. |
| Raspberry Pi 5, camera, storage, cooling | Dedicated regulated 5 V | Design for 5 V/5 A (25 W) even if the first software build measures less; approximately 30 W input allowance at 85% conversion efficiency | Raspberry Pi recommends 5 V/5 A for Pi 5 full peripheral capability. Measure with LiDAR and storage active. |
| Payload wiring/regulator losses | Battery branch | 10% conversion/wiring allowance during early sizing | Measure voltage at both payload endpoints under motor load. |
| **Payload electronics design allowance** | 4S battery | Approximately 35–45 W, separate from motors | Estimated, not measured. |

A 4S 5 Ah pack has approximately `14.8 V x 5 Ah = 74 Wh` nominal energy. A conservative 75% usable-energy planning value is about 55 Wh, but usable energy depends on battery temperature, current, cutoff voltage, age, and reserve policy. If loaded propulsion power is later measured at 400–600 W, 55 Wh corresponds to roughly 5.5–8.3 minutes of energy before additional safety reserve; this is an illustrative range, not a flight-time claim. Initial payload flights should use short 3–5 minute test blocks and land with a deliberately large voltage reserve until current logging establishes a safe mission duration. The manufacturer's approximately 18-minute no-additional-payload hover result is not extrapolated to this payload.

### Electrical, EMI, and noise controls

- Use a star-like battery return at the PDB and keep the high-current motor loop physically short. Do not put the LiDAR or Pi ground return through a Pixhawk port.
- Use separate payload fuses, LC filtering, and twisted positive/return pairs. Use shielded or well-terminated Ethernet and bond the shield according to the received SICK cable guidance; do not improvise an unshielded loose Ethernet lead near ESC phase wires.
- Keep the GPS/compass on its mast and separate from the battery lead, regulator, PDB, and telemetry transmitter. Record compass calibration after the final cable route is fixed.
- Keep telemetry and RC antennas clear of carbon plates, motor wires, and the Pi's high-speed cables. Do not place the SiK radio directly beside the Wi-Fi antenna or regulator in the final layout.
- Log Pi brownouts, regulator output voltage, LiDAR reconnects, and Pixhawk battery voltage/current. A sensor that stays powered but loses Ethernet is a payload fault, not a flight-controller fault; the aircraft must remain controllable without it.
- The Pi 5 needs active cooling and ventilation. The sensor's outdoor enclosure rating is not a reason to expose the Pi or an open camera board to rain, condensation, or dirt during the initial tests.

## 5. Development sequence and dependencies

The sequence below is deliberately incremental. No stage establishes regulatory approval or validates the complete field system.

### Stage 0 — Borrowed-equipment and parts confirmation

Confirm whether Mississippi State/capstone lab can supply an X500/S500-class airframe, 4S battery, charger, RC transmitter/receiver, scales, an adjustable power supply, a ground laptop, and a safe supervised test location. Confirm the challenge sensor variant, system plug, cables, licenses, and desired data format before buying sensor-specific connectors. Resolve the central choice of PX4 versus ArduPilot with mission-control investigation 05.

### Stage 1 — Bench fit check, no propellers

Install the FC, GPS, telemetry, computer, camera, LiDAR bracket, regulator, battery, cables, and secondary tether. Weigh every subassembly and the complete aircraft. Check 215 mm landing clearance, propeller arcs, scan fan clearance, Pi cooling, camera view, connector access, fastener security, and measured CG. Record the sensor-to-camera-to-body transform and the initial scan-plane angle. The exit condition is a documented mass/CG sheet and no cable or mount interference.

### Stage 2 — Restrained motor/power test

Remove propellers for initial electrical checks; later motor tests use the lab's approved restraint procedure and an exclusion zone. Verify correct motor order and direction, battery current reporting, PM02 output, payload regulator output/ripple, LiDAR startup/Ethernet stream, Pi camera capture, and telemetry/RC link. Test the payload branch while the propulsion electronics switch and motor commands are exercised. The exit condition is stable rail voltage, no brownout or connector heating, and a documented abort/shutdown procedure.

### Stage 3 — Empty hover test

Fly only after bench checks, with the sensor/computer payload removed or at the lightest safe configuration. Confirm stable manual/assisted control, landing behavior, battery voltage/current logs, compass behavior, vibration metrics, and failsafe behavior in a controlled supervised test. This is a platform check, not a PaveWatch survey or field-validation result.

### Stage 4 — Payload vibration test

Install the complete payload and battery. Begin with a restrained or very short controlled test, then a low-risk hover. Compare Pixhawk vibration logs and camera/LiDAR stream health against the empty-platform baseline. Inspect all fasteners and cable restraints after landing, check mount deflection, and measure Pi/LiDAR rail voltage during motor transients. Do not proceed if the payload mount resonates, the scan plane moves, or the computer/LiDAR resets.

### Stage 5 — Supervised survey test

Use a small, pre-marked paved test area and a short planned route with an operator maintaining direct supervision and a manual recovery mode. Record LiDAR, camera, position, flight status, and power logs; repeat the route only after the first pass is inspected. Report measured coverage, timing, vibration, and repeatability only after this stage produces data. Any application demonstration that uses public/synthetic data remains a software demonstration, not complete UAV field validation.

## 6. Verification tests and success measures

| Test | Provisional success measure | Not yet established |
|---|---|---|
| Fit/CG | Complete aircraft weighed; CG within ±10 mm of motor-plane center in x/y; no sensor/camera/prop interference | Actual platform mass and all-up payload margin |
| Power | Pi rail remains within its selected regulator tolerance with LiDAR, camera, storage, and motor switching active; no Pixhawk or payload brownouts; LiDAR current and startup captured | Exact regulator, startup surge, EMI margin, and current under hot conditions |
| Ethernet/data | Pi receives continuous sensor data for a bench run; reconnect behavior is logged; sensor IP and format are recorded | Final format/rate and timestamp strategy from investigations 02/04 |
| Camera geometry | Camera image and LiDAR pavement sector overlap the intended test plane; rigid extrinsics are repeatable after remount | Final lens/FOV, shutter behavior, and calibration accuracy |
| Vibration | Pixhawk vibration logs and mount inspection show no unexplained resonance; sensor angle does not drift during test | Numeric vibration threshold and survey-speed envelope; these must be chosen from measured data and sensor requirements |
| Battery/flight | Battery voltage/current is logged and the aircraft lands with the agreed reserve during every test block | Loaded hover current, temperature derating, and safe survey duration |
| Safety/failsafe | Payload power loss does not remove flight control; loose-mount abort procedure, low-battery action, and communications-loss action are rehearsed on the ground before test | Final failsafe parameters and operating-site procedure |

## 7. Interfaces with other investigations

### Investigation 02 — picoScan150 sensing and acquisition

- Confirm the received picoScan150 variant, system plug part number, input voltage range, current/startup behavior, output options, licenses, Ethernet IP settings, and whether Compact, MessagePack, or LMDscandata is the selected stream.
- Define a computer-facing Ethernet cable and connector strain-relief requirement. The FC is not the sensor data path.
- Define scan frequency, angular resolution, usable pavement sector, IMU-data selection, sensor timing fields, and how the acquisition process detects a dropped stream.
- Provide the sensor coordinate convention and a mounting/calibration procedure so the mount's pitch/yaw can be represented in the data.

### Investigation 03 — RGB positioning and synchronization

- Confirm camera model, lens/FOV, frame rate, exposure/shutter requirements, image timestamp source, and whether a hardware trigger is needed.
- Define the fixed camera-to-LiDAR extrinsic transform, lens calibration artifact, and shared body-frame convention. The camera must remain rigid relative to the sensor after calibration.
- Decide whether the camera is connected by Pi CSI, USB, or borrowed camera hardware. Any change affects the power, mass, and mount budgets.

### Investigation 04 — onboard computing, storage, and telemetry

- Confirm Pi 5 memory/storage requirements, cooling/enclosure, image and LiDAR data rates, local retention time, and shutdown behavior on low battery.
- Provide the final 5 V regulator current peak, storage interface, Ethernet switch/adapter need, host timestamp policy, and telemetry uplink bandwidth.
- Define whether heavy processing is offboard after landing. The initial platform budget assumes acquisition and health monitoring onboard, not mandatory onboard neural-network inference.

### Investigation 05 — mission planning and ground control

- Select PX4 or ArduPilot, verify the X500/S500 airframe configuration, and map Pixhawk ports for RC, GPS, telemetry, battery monitor, and optional camera/payload status.
- Define waypoint altitude/speed, route repeatability, operator controls, landing/abort logic, battery thresholds, communication-loss action, and flight-log fields. These are operating decisions, not claims of regulatory approval.
- Provide the ground-station telemetry workflow and the time/coordinate fields that must be joined with the Pi and sensor logs.

### Decisions required centrally

1. Exact sensor variant/system plug and whether challenge accessories include the 12-pin power cable and M12 Ethernet cable.
2. PX4 versus ArduPilot and the canonical body/NED/ENU coordinate convention.
3. Camera choice and synchronization/timestamp method.
4. Pi 5 2 GB versus 4 GB and the final storage device.
5. Battery chemistry/capacity, safe reserve policy, and whether the radio/charger are borrowed.
6. The final sensor pitch/yaw and survey speed after an unobstructed scan-plane test.

## 8. Risks, open decisions, safety, and fallback

### Failure mitigations

| Risk/failure | Mitigation and response |
|---|---|
| Loss of payload power or LiDAR Ethernet | Use a separately fused/filtered branch and monitor Pi/LiDAR health. Payload failure must not remove Pixhawk power. Mark the data interval invalid, abort/land through the flight procedure, and inspect connectors before another test. |
| Loose sensor mount or drifting pitch/yaw | Use all available SICK-bracket fasteners, locking hardware, a secondary tether, witness marks, and a preflight fastener/angle check. Do not fly if the tether is carrying load or the angle mark moved. |
| Excessive vibration/resonance | Balance/inspect props and motors, tighten arms, keep the sensor bracket rigid, isolate the Pi separately, measure/log vibration, and stop if the angle or data stream changes. A soft mount is not a substitute for a calibrated rigid sensor mount. |
| Low battery or voltage sag | Use Pixhawk PM02 voltage/current logging, a conservative land-before-reserve threshold, short first survey blocks, battery temperature/physical checks, and a post-flight cell-voltage check. Do not infer remaining time from the manufacturer's empty-platform flight-time claim. |
| Communications loss | Retain a tested manual RC link and telemetry link, define the mission-control communications-loss behavior on the bench, and keep a direct operator recovery mode. A planned route must never be the only way to stop or recover the aircraft. |
| Propeller wash, dirt, or weather exposure | Keep the sensor/camera below the propeller disk but clear of direct structure occlusion, clean the optical hood before every test, protect the Pi and camera, and begin in dry, low-wind supervised conditions. No weather-performance result is claimed. |
| Landing impact or inadequate clearance | Verify landing-gear clearance with the full sensor/mount installed, use a sacrificial/secondary mount interface where practical, and inspect the sensor, camera, cable, and plate after every landing. |
| Budget overrun | Borrow the airframe/radio/charger/Pi where possible; use the S500 fallback; use Pi 5 2 GB and a printed/plate mount; defer RTK, Jetson, industrial camera, gimbal, and X650 upgrades. |

### Open technical decisions

- The actual X500 complete-kit mass is not published as one unambiguous value in the current page. The 800 g design allowance must be replaced by a scale measurement.
- The actual SICK system plug and cable mass, connector orientation, and minimum bend radius are unknown until the challenge package is received.
- The LiDAR scan-plane orientation relative to the pavement, route direction, altitude, and speed cannot be finalized from this desk study. It must be selected after a static planar-target fit check.
- The computer regulator has not been selected. It must be tested for transient response and thermal performance with the Pi, camera, storage, and LiDAR active.
- No payload vibration, hover current, all-up flight time, image overlap, LiDAR coverage, height accuracy, or change-detection performance is measured by this investigation.
- Any borrowed drone, battery, controller, computer, or camera changes the mass, connectors, power tree, and CG. The integration editor must update the tables rather than silently substituting borrowed specifications.

### Fallback demonstration path

If no flight hardware is available, use the supplied or borrowed picoScan150 on a bench/rolling rig and use public or synthetic data for software pipeline work. Keep that result labeled as a software demonstration. If the SICK sensor is delayed, use a recorded/synthetic LiDAR stream with the same Ethernet/data schema and preserve the mount/power interfaces for later replacement. Neither fallback is complete UAV field validation.

## 9. Sources

The following direct links were consulted on 2026-09-19. Prices are observations on that date, not guarantees.

1. Holybro, [PX4 Development Kit – X500 v2](https://holybro.com/products/px4-development-kit-x500-v2?variant=43018371563709), current Pixhawk 6C/M10/915 MHz listing, included components, frame dimensions, payload, battery recommendation, and published hover figure.
2. Holybro, [PX4 Development Kit – X500 v2 documentation](https://docs.holybro.com/drone-development-kit/px4-development-kit-x500v2), earlier X500 kit details and conservative approximately 1 kg payload wording with a 4S 5 Ah battery.
3. Holybro, [S500 V2 Development Kit](https://holybro.com/products/s500-v2-development-kit), current $519 listing, included components, 915 MHz option, mass, payload, battery recommendation, and hover figure.
4. Holybro, [X650 Development Kit](https://holybro.com/products/x650-development-kit), current $1,109 listing, included components, payload, battery recommendation, frame, and hover figures.
5. Holybro, [Pixhawk 6C](https://holybro.com/collections/all-product/products/pixhawk-6c), Pixhawk 6C electrical ratings, dimensions, plastic-case mass, and controller details.
6. Holybro, [Pixhawk 6C ports](https://docs.holybro.com/autopilot/pixhawk-6c/pixhawk-6c-ports), power, GPS, telemetry, CAN, RC, and PWM pin assignments.
7. Holybro, [PM02 V3 12S power module](https://holybro.com/collections/power-modules-pdbs/products/pm02-v3-12s-power-module), $18.99 price, 2S–12S input, 5.2 V/3 A output, current-sense and mass details.
8. SICK, [picoScan150 operating instructions](https://cdn.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf), sensor mass/dimensions, scan characteristics, supply/power information, Ethernet pinout, fuse guidance, output-load limits, and IMU/timing documentation.
9. SICK, [picoScan150 retrofit/power-I/O pin information](https://support.sick.com/sick-knowledgebase/article/?code=KA-09512), 9–28 V power-I/O pin information and M12 power connector assignment.
10. SICK, [picoScan150 mounting bracket data sheet, part 2134874](https://www.sick.com/media/pdf/6/96/896/dataSheet_Mounting-bracket-picoScan150_2134874_en.pdf), 63 g bracket, dimensions, five M4 fasteners, and high-shock/vibration installation note.
11. SICK, [SICK$10K Challenge](https://www.sick.com/us/en/sick-10k-challenge/w/10K-Challenge), challenge-supplied picoScan150 statement and challenge resources.
12. Raspberry Pi, [Raspberry Pi 5 product page](https://www.raspberrypi.com/products/raspberry-pi-5/), current Pi 5 interfaces, storage/camera/Ethernet capabilities, and power guidance.
13. Raspberry Pi, [Raspberry Pi 5 power documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html), 5 V/5 A recommendation, peripheral current limit, and typical bare-board current.
14. Raspberry Pi, [memory-driven price revision](https://www.raspberrypi.com/news/1gb-raspberry-pi-5-now-available-at-45-and-memory-driven-price-rises/), official 2025 price table used to set the Pi planning allowance.
15. Raspberry Pi, [Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/), $25 starting price, 12 MP sensor, autofocus, CSI-2, FOV, and dimensions.
16. PowerHobby, [4S 14.8 V 5,000 mAh XT60 LiPo](https://www.powerhobby.com/products/powerhobby-4s-14-8v-5000mah-100c-lipo-battery-w-xt60-plug-hard-case-lcg), current $79.99 listing and battery voltage/capacity/connector details.
17. RadioMaster, [Pocket radio controller](https://www.radiomasterrc.com/products/pocket-radio-controller-m2), current $64.99 transmitter listing.
18. RadioMaster, [ELRS receiver listings](https://www.radiomasterrc.com/collections/elrs-receivers), current small-receiver planning prices; final receiver protocol and Pixhawk wiring remain open.
19. PX4, [Holybro Pixhawk 6C wiring quick start](https://docs.px4.io/v1.14/en/assembly/quick_start_pixhawk6c), power, RC, telemetry, and motor-output integration guidance.

Repository references read before this investigation: `AGENTS.md`, `sick-application/AGENTS.md`, `sick-application/investigations/01-flight-platform-power-mechanical/AGENTS.md`, and `sick-application/investigations/README.md`.
