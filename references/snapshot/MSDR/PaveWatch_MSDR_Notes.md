# PaveWatch — Mid Semester Design Review

October 23, 2026 · Aerovengers

## 01 · PaveWatch

Aerovengers is developing a UAV system for inspecting paved surfaces. The system combines laser profiles, images, and aircraft pose to support maintenance review. The review covers requirements, component selection, subsystem responsibilities, and the Capstone I and II development plan.


## 02 · Team and responsibilities

Shisir Baral is Project Manager and Diagnostics & Telemetry owner, and reviews overall architecture, purchases, scope, and release decisions. Abhinav Dhakal is Chief Scientist and Sensor Payload & Data Acquisition owner. Ankit owns Flight Platform, Power & Control; Pritam owns Ground Control & Communications; Aalok owns Data Processing & Change Detection; Saugat owns Reporting, Database & Alerts. Faculty advisor: Jingdao Chen.


## 03 · Pavement inspection problem

The Los Angeles Controller's 2021 audit reports more than 1,700 sidewalk injury claims and over $35 million in settlements over five fiscal years. This is a city-specific example of the consequences of deteriorating sidewalks. PaveWatch targets campus facilities and municipal maintenance teams that need organized condition records and location-linked evidence. Reviewers retain responsibility for follow-up inspection and maintenance decisions.

[1] [Los Angeles Controller · Sidewalk audit (2021)](https://controller.lacity.gov/audits/sidewalks)
[2] [FHWA · 2D and 3D pavement imaging](https://infotechnology.fhwa.dot.gov/2d-and-3d-imaging-technology/)

## 04 · Inspection approaches

The design integrates direct range measurements with visual evidence in a common survey frame. A current survey supports broad surface geometry and visible-distress assessment. A previous survey can add change context. This comparison describes the intended information supplied by each approach; comparative field performance will be evaluated during development.

| Approach | Primary information | PaveWatch design contribution |
| --- | --- | --- |
| Manual inspection | Direct observation and inspector judgment | Location-linked records for follow-up inspection |
| RGB imaging | Visible distress, texture, and context | Pair images with laser-derived surface measurements |
| Photogrammetry | Image-derived surface reconstruction | Use direct range profiles as a geometry input |
| PaveWatch | Laser profiles + images + aircraft pose | A referenced survey package and maintenance review interface |

[2] [FHWA · 2D and 3D pavement imaging](https://infotechnology.fhwa.dot.gov/2d-and-3d-imaging-technology/)

## 05 · Design features

The baseline assesses a single survey. Repeat-survey comparison is an extension. Quantitative measurement relies on valid timing, pose, and mounting relationships. The prototype targets broad pavement geometry and visible concerns; structural and subsurface diagnosis require other methods.


## 06 · Survey workflow

The operator plans a mission, the aircraft records laser profiles and RGB images with pose, and the survey package is transferred after landing. Processing reconstructs and evaluates the surface, then supplies findings to the review interface and report. The supplied illustration also shows previous-survey comparison; that stage is optional. Current-survey surface assessment is the baseline. The imagery illustrates the planned workflow.


## 07 · Subsystem architecture

The six subsystems separate mission control, flight, acquisition, processing, reporting, and diagnostics. LiDAR connects to the recorder over Ethernet; the selected camera uses USB. Position, orientation, and flight state are logged with time references. Bulk sensor data is stored onboard and transferred after landing. The ground radio carries mission commands and health information. Photogrammetry and repeat-survey change detection in the illustration are extension paths. The ownership strip identifies the team member responsible for each subsystem.


## 08 · System requirements: flight and geometry

Use predefined evaluation regions and matching rules. A missed feature reduces S2 recall. S3 is evaluated on detected targets and requires both height and location bounds to pass together. Separate calibration controls from evaluation targets. Record measured and reference gradients; a numerical gradient-error acceptance limit remains to be agreed.

| Feature / ID | Acceptance target | Evaluation |
| --- | --- | --- |
| F1 / S1 | ≥10 min flight with acquisition active; ≥20% calibrated usable energy remaining at landing | Three loaded flights |
| F2 / S2 | 100–150 mm geometry in regions ≥0.5 × 0.5 m; recall ≥90%, precision ≥80%; report gradients | ≥10 feature cases and ≥10 negative regions |
| F2 / S3 | ≥90% of detected targets jointly meet height error ≤60 mm and centroid error ≤0.5 m | Independent height and location references; height uncertainty ≤10 mm |


## 09 · System requirements: data and imagery

The imagery task identifies visible classes at the stated prototype scale. Evaluate the actual lens, height, speed, image mode, and lighting together. Preserve original sensor and flight timestamps, then map them into a documented common time reference. Record frame origin, axes, units, orientation convention, and sensor-to-body transforms. Unsupported observations must be flagged.

| Feature / ID | Acceptance target | Evaluation |
| --- | --- | --- |
| F3 / S4 | Record range and images for ≥10 min; identify stream gaps >1 s | Concurrent recording and controlled gap injection |
| F2–F3 / S5 | Per-class precision and recall ≥80%; crack-like targets ≥20 mm × 0.2 m; depressions ≥0.5 × 0.5 m | ≥10 positives per class and ≥10 nuisance-only regions |
| F4 / S6 | Record 3D position and orientation for ≥10 min; reference each quantitative observation | Clock/frame/mount checks and missing-reference tests |


## 10 · Operating and integration constraints

The 650 g and 800 g payload values are engineering allocations including the sensor, recorder, camera, storage, supplies, harness, mount, and margin. The sensor-body mass is specified as 220 g, excluding its system plug. Confirm delivered accessories and installation dimensions. The flight regulatory row summarizes the planned operating case; applicable airspace, pilot, weather, and aircraft conditions are addressed in the operation plan. The $700 boundary applies to the aircraft configuration and excludes recording payload; separate total project funding must be reconciled.

| Area | Planning bound | Design response |
| --- | --- | --- |
| Survey operation | 5–8 m above pavement; 1–2 m/s; dry daylight | Plan route spacing, exposure, and scan coverage together |
| Flight/site | Part 107 operating case; VLOS; <55 lb; ≤400 ft AGL; campus request ≥3 weeks ahead | Schedule site authorization before field trials |
| Aircraft budget | Under $700 for aircraft, flight battery, RC, and navigation; recording payload excluded | Compare complete aircraft configurations and delivered quotes |
| Payload installation | 650 g target; 800 g upper planning case; picoScan supply 9–30 V DC | Allocate mass, mounting space, and separate payload power branches |

[13] [SICK · picoScan150 operating instructions](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf)
[14] [14 CFR Part 107 · Small unmanned aircraft](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107)
[15] [Mississippi State · UAS policy 79.11](https://www.policies.msstate.edu/sites/www.policies.msstate.edu/files/policies/7911.pdf)

## 11 · Applicable standards

Ethernet supplies the physical/data-link interface used for sensor transport. Capture software separately checks packet continuity. GeoJSON coordinates use longitude then latitude in WGS 84; local metric geometry is stored with an explicit frame and units rather than being presented as geographic coordinates. TLS 1.3 applies when network upload or remote report access is used; application authorization is handled by the reporting service.

| Standard | Application | Verification |
| --- | --- | --- |
| IEEE 802.3-2022 | Ethernet connection from LiDAR to recorder | Verify link configuration and ≥10 min capture; inspect packet gaps |
| IETF RFC 7946 | Geographic finding exports in GeoJSON | Parse ≥10 findings; verify WGS 84 longitude/latitude ordering |
| IETF RFC 8446 | TLS 1.3 for network upload and report access | Verify negotiated version and certificate handling |

[16] [IEEE 802.3-2022 · Ethernet](https://standards.ieee.org/ieee/802.3/10422/)
[17] [IETF RFC 7946 · GeoJSON](https://www.rfc-editor.org/rfc/rfc7946)
[18] [IETF RFC 8446 · TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)

## 12 · Flight-system options

Selection metrics are an aircraft cost below $700, payload mounting, control and pose interfaces, and a ten-minute loaded survey with energy reserve. The original F450 DIY concept is retained as one of three options. Its $405 estimate covers the frame/propulsion, controller stack, F9P rover, flight battery, and FlySky radio. The X500 and S500 subtotals include the navigation and ground telemetry arrangements detailed in the hardware plan. Cost scopes differ and are labeled accordingly. X500 is the planning choice for its external rails and configurable electronics. Purchase configuration and delivered quote are reviewed by the Project Manager.

| Configuration | Planned cost | Selection attributes |
| --- | --- | --- |
| F450 DIY + SpeedyBee F405 V4 | $405 estimate | Custom assembly; F9P rover navigation concept; FlySky RC; 3S/4S battery selection |
| X500 v2 ARF + Kakute H7 Mini v1.5 | $657.17 subtotal | 250 mm payload rails; matched propulsion; M10 GNSS/compass; SiK telemetry; 4S 5 Ah |
| S500 v2 kit + Pixhawk 6C | $669.20 subtotal | Integrated flight electronics; M10 navigation; SiK telemetry; matched propulsion and 4S 5 Ah |

[3] [Holybro · X500 v2 ARF / frame specifications](https://holybro.com/products/x500-v2-kits)
[4] [Holybro · S500 v2 development kit](https://holybro.com/products/s500-v2-development-kit)
[5] [ArduPilot · SpeedyBee F405 V3/V4](https://ardupilot.org/copter/docs/common-speedybeef4-v3.html)
[6] [Holybro · Kakute H7 Mini](https://holybro.com/products/kakute-h7-mini)
[24] [Holybro · H-RTK F9P GNSS series](https://holybro.com/products/h-rtk-f9p-gnss-series)

## 13 · Recorder options

Metrics are Ethernet, camera and SSD connectivity, installed mass and cost, timestamp access, and simultaneous recording for at least ten minutes. Board/hub allowances exclude camera, SSD, power, and enclosure. Orange Pi is the low-cost starting configuration; Pi 4 supplies a USB 3 path if required by the measured data rate. Record native camera compression when available. Benchmark sustained capture, dropped packets/frames, CPU load, storage queues, and temperature using actual sensor modes. A USB-C SSD connects to the board's host port through a suitable data cable.

| Configuration | Interfaces / allowance | Selection attributes |
| --- | --- | --- |
| Orange Pi Zero 3 + expansion board | Gigabit Ethernet; USB 2.0; approximately $50 for board + expansion | Compact recorder for LiDAR, USB camera, and external SSD |
| Raspberry Pi 4 · 2 GB | Gigabit Ethernet; USB 3.0; CSI; approximately $60 board allowance | Native USB ports and storage interface; CSI camera option |
| Pi Zero 2 W + Ethernet/USB hub | CSI; USB host with Ethernet adapter; approximately $35 board + hub | Compact modular recorder with shared USB connection |

[7] [Orange Pi · Zero 3](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero-3.html)
[8] [Raspberry Pi · Pi 4 Model B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
[9] [Raspberry Pi · Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)

## 14 · Camera options

Selection metrics are usable target detail at 5–8 m, motion performance at 1–2 m/s, color evidence, timing controls, interface compatibility, and installed cost/mass. The low-cost InnoMaker product page gives inconsistent 720p/1080p wording; confirm the exact SKU and negotiated UVC modes. The OV9281 model is 1280 by 800 and monochrome, so choosing it changes the RGB acquisition plan. Global shutter exposes the image together but does not prevent exposure-related motion blur. The Arducam B0495 datasheet specifies full 1920 by 1200 operation on USB 3 and reduced 960 by 600 at 10 fps on USB 2. Verify ground pixel scale and target visibility; megapixel count alone does not establish S5. Listed prices exclude delivery fees. Arducam pricing requires an exact quote.

| Camera | Image / interface | Selection attributes |
| --- | --- | --- |
| InnoMaker U20CAM-1080P | Color; USB 2.0 UVC; $18.69 listed | Budget color recording; verify negotiated 1080p mode and lens coverage |
| InnoMaker U20CAM-9281M | 1280 × 800 monochrome; global shutter; $32.99 listed | External trigger; manual exposure; grayscale analysis path |
| Arducam B0495 / AR0234 | 1920 × 1200 color; global shutter; USB 3.0 | Color with global exposure; pair with a USB 3 recorder for full mode |

[10] [InnoMaker · U20CAM-1080P](https://www.inno-maker.com/product/u20cam-1080p/)
[11] [InnoMaker · U20CAM-9281M](https://www.inno-maker.com/product/u20cam-9281m/)
[12] [Arducam · B0495 / AR0234 datasheet](https://www.arducam.com/downloads/datasheet/B0495_AR0234_Global_Shutter_USB3.0_Camera_Module_Datasheet.pdf)

## 15 · Payload installation and power

Payload target allocations: sensor body 220 g; plug and harness 90 g; recorder/cooling/protection 90 g; camera/cable 20 g; SSD/cable 30 g; supply/filter/fuses 40 g; mounting/retention 100 g; margin 60 g. Total 650 g, with an 800 g upper planning case. Proposed sensor envelope is 120 by 100 by 130 mm; recorder envelope 120 by 90 by 60 mm. These are packaging allocations. Install the camera rigidly relative to the LiDAR and record the transform. A 4S pack is 14.8 V nominal and 16.8 V full. Feed the LiDAR through a fused branch consistent with the received unit's instructions; supply the computer/camera/SSD from a dedicated regulated 5 V branch. The two existing 2S packs remain available equipment. Confirm 4S charging, connector arrangements, measured payload mass, center of gravity, and ground clearance during assembly.

[3] [Holybro · X500 v2 ARF / frame specifications](https://holybro.com/products/x500-v2-kits)
[13] [SICK · picoScan150 operating instructions](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf)
[23] [RCBattery · 4S 5 Ah battery](https://rcbattery.com/liperior-5000mah-4s-35c-14-8v-lipo-battery-with-xt90-plug.html)

## 16 · Aircraft budget

The X500 DIY aircraft subtotal is $657.17 before shipping and tax: ARF $329; Kakute H7 Mini v1.5 $82; Micro M10 IST8310 $27.99; SiK 915 MHz pair $58.99; PM02 V3 $18.99; RC, flight battery, adapter, and transmitter cells $110.20; custom wiring/mounting consumables $30. The resulting allowance below $700 is $42.83. The recording payload is separately budgeted. Orange Pi and expansion allocation $50 plus color camera $18.69 equals $68.69 before SSD, regulator, cooling, storage card, LiDAR connectors, and payload mount. A 4S charger must be available within the delivered aircraft plan. The comparison uses ordinary M10 GNSS for X500 and S500; an RTK addition has a separate cost and corrections plan. Verify the full procurement total against available project funding.

[3] [Holybro · X500 v2 ARF / frame specifications](https://holybro.com/products/x500-v2-kits)
[6] [Holybro · Kakute H7 Mini](https://holybro.com/products/kakute-h7-mini)
[19] [Holybro · Micro M10 GNSS / compass](https://holybro.com/products/micro-m10-gps)
[20] [Holybro · SiK telemetry radio](https://holybro.com/products/sik-telemetry-radio-v3)
[21] [Holybro · PM02 V3 power module](https://holybro.com/products/pm02-v3-12s-power-module)
[22] [RadioLink · T8FB specifications](https://www.radiolink.com/t8fb_specification)
[23] [RCBattery · 4S 5 Ah battery](https://rcbattery.com/liperior-5000mah-4s-35c-14-8v-lipo-battery-with-xt90-plug.html)

## 17 · Project development

Upcoming work moves from interface definition to commissioning, bench evaluation, and integrated field evaluation. The competition supplies the picoScan sensor. The team has two 2S batteries and chargers. Acceptance values on the requirement slides define the planned evaluation.


## 18 · Capstone I schedule

The Capstone I plan assigns dated tasks to all six subsystems. Freeze the aircraft and payload interfaces, place compatible orders, commission the sensor and recorder, then integrate diagnostics, processing, and reporting. The November 30 demonstration focuses on acquisition, diagnostics, and processing. Flight and ground-control work supports those workstreams. Field activity depends on delivery, assembly, and site authorization. Course milestones: October 30 approach draft, November 13 approach final, November 20 demo rubric, November 30 demo, December 4 final document.


## 19 · Capstone II schedule

The January through April dates are proposed planning dates. Complete platform and mount integration, calibrate clocks and sensor geometry, evaluate controlled movement, then conduct loaded flights and independent surface checks. Final evaluation includes held-out geometry/image cases, field errors, health logs, and the reviewer interface. Optional repeat-survey analysis follows current-survey validation.


## 20 · Capstone I demonstration deliverables

SA2 timing uses independent events at the start, middle, and end of recording. SA3 tests 5, 6.5, and 8 m with at least ten observations under each declared condition. DT2 injects five gaps longer than one second per stream; DT3 removes the sensor and pose inputs. PC1 uses three known sensor positions, at least ten independent check points, at least 90% within 1 m X/Y and 0.2 m Z, and ten invalid-reference tests. PC2 follows S2, S3, and S5 sample counts. PC3 completes three exports of at least 1 GB each within thirty minutes with integrity checks. Bench, replay, and flight records are labeled by acquisition method. The flight, ground-control, and reporting owners provide platform/pose inputs, operator links, and result display to the three demo workstreams.

| Subsystem / owner | Performance criteria | Method and delivered artifact |
| --- | --- | --- |
| Sensor Acquisition; Abhinav Dhakal | ≥10 min range + images; gaps >1 s flagged; residual timing ≤20 ms; ≥90% range errors ≤60 mm | Bench recording at 5, 6.5, 8 m; ≥10 observations/condition; independent timing events. Data package + plots. |
| Diagnostics & Telemetry; Shisir Baral | ≥90% health updates ≤4 s for ≥10 min; sensor/pose loss warnings | ≥300 updates; inject 5 gaps per stream; disconnect pose/sensor. Status view + latency/fault logs. |
| Data Processing; Aalok Uprety | ≥90% frame checks: ≤1 m X/Y, ≤0.2 m Z; S2/S3/S5 metrics; 3 exports ≥1 GB, each ≤30 min | Three known poses + ≥10 check points; held-out geometry/image cases; integrity checks. Analysis + findings + exports. |


## 21 · Verification plan

The agreed FP4 attitude bound is ≤5° for at least 90% of samples, aligning the test with the requirement. FP1 requires three loaded flights of at least ten minutes with at least 20% usable energy reserve. FP2 requires five passes with at least 90% within 2 m horizontally and ±1 m vertically in the survey envelope. FP3 takeover is ≤1 s in ten of ten trials. Record recall as true positives divided by true positives plus false negatives and precision as true positives divided by true positives plus false positives. Attitude acceptance is a subsystem check; independent final surface accuracy is still evaluated under S3.


## 22 · Integration decisions

The X500 and S500 configurations use ordinary M10 GNSS. Final measurement quality is evaluated against independent surface references with the documented pose and registration workflow. The F450 concept includes an F9P rover and therefore needs a corresponding correction source and delivery plan. GC3's current requirement specifies sixty seconds of buffering and backlog before current stream data; define the bounded data stream so current control and safety information retain their own appropriate path. Gradient reporting needs a numerical error criterion for acceptance.

| Decision | Planned definition | Lead |
| --- | --- | --- |
| Mechanical and power | Freeze installed mass, sensor clearance, mount geometry, 4S charging, and the final delivered quote | Ankit + Abhinav |
| Navigation and timing | Document GNSS/IMU pose, clocks, mounting transforms, and independent reference points | Ankit + Aalok |
| Ground communication | Define GC3's 60 s buffered stream, data rate, reconnect ordering, and operator health fields | Pritam + Shisir |
| Evaluation and reporting | Agree gradient-error criterion, evidence fields, geographic export, and reviewer warnings | Aalok + Saugat |


## 23 · Future work and broader impact

The project supports human maintenance review with organized images and geometry. Better condition records may support maintenance prioritization and accessibility-focused inspection. Field evaluation will establish the usable operating envelope and practical effort. Repeat-survey comparison is an extension after current-survey performance has been established.


## 24 · References: inspection and aircraft

Manufacturer specifications, technical standards, and public-agency references used for the design. Hardware prices and configurations are planning inputs; final quotes include the selected variants and delivery costs.

[1] [Los Angeles Controller · Sidewalk audit (2021)](https://controller.lacity.gov/audits/sidewalks)
[2] [FHWA · 2D and 3D pavement imaging](https://infotechnology.fhwa.dot.gov/2d-and-3d-imaging-technology/)
[3] [Holybro · X500 v2 ARF / frame specifications](https://holybro.com/products/x500-v2-kits)
[4] [Holybro · S500 v2 development kit](https://holybro.com/products/s500-v2-development-kit)
[5] [ArduPilot · SpeedyBee F405 V3/V4](https://ardupilot.org/copter/docs/common-speedybeef4-v3.html)
[6] [Holybro · Kakute H7 Mini](https://holybro.com/products/kakute-h7-mini)
[24] [Holybro · H-RTK F9P GNSS series](https://holybro.com/products/h-rtk-f9p-gnss-series)

## 25 · References: acquisition hardware

Manufacturer specifications, technical standards, and public-agency references used for the design. Hardware prices and configurations are planning inputs; final quotes include the selected variants and delivery costs.

[7] [Orange Pi · Zero 3](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero-3.html)
[8] [Raspberry Pi · Pi 4 Model B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
[9] [Raspberry Pi · Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
[10] [InnoMaker · U20CAM-1080P](https://www.inno-maker.com/product/u20cam-1080p/)
[11] [InnoMaker · U20CAM-9281M](https://www.inno-maker.com/product/u20cam-9281m/)
[12] [Arducam · B0495 / AR0234 datasheet](https://www.arducam.com/downloads/datasheet/B0495_AR0234_Global_Shutter_USB3.0_Camera_Module_Datasheet.pdf)
[13] [SICK · picoScan150 operating instructions](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf)

## 26 · References: interfaces and operation

Manufacturer specifications, technical standards, and public-agency references used for the design. Hardware prices and configurations are planning inputs; final quotes include the selected variants and delivery costs.

[14] [14 CFR Part 107 · Small unmanned aircraft](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107)
[15] [Mississippi State · UAS policy 79.11](https://www.policies.msstate.edu/sites/www.policies.msstate.edu/files/policies/7911.pdf)
[16] [IEEE 802.3-2022 · Ethernet](https://standards.ieee.org/ieee/802.3/10422/)
[17] [IETF RFC 7946 · GeoJSON](https://www.rfc-editor.org/rfc/rfc7946)
[18] [IETF RFC 8446 · TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)

## 27 · References: aircraft electronics

Manufacturer specifications, technical standards, and public-agency references used for the design. Hardware prices and configurations are planning inputs; final quotes include the selected variants and delivery costs.

[19] [Holybro · Micro M10 GNSS / compass](https://holybro.com/products/micro-m10-gps)
[20] [Holybro · SiK telemetry radio](https://holybro.com/products/sik-telemetry-radio-v3)
[21] [Holybro · PM02 V3 power module](https://holybro.com/products/pm02-v3-12s-power-module)
[22] [RadioLink · T8FB specifications](https://www.radiolink.com/t8fb_specification)
[23] [RCBattery · 4S 5 Ah battery](https://rcbattery.com/liperior-5000mah-4s-35c-14-8v-lipo-battery-with-xt90-plug.html)
