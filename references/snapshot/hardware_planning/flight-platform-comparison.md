# PaveWatch flight-platform comparison

Research checked **October 23, 2026**. Budget clarified by the user: **under $700 for the complete aircraft, flight battery, RC, and navigation**, excluding the supplied LiDAR and recording payload. This is a design comparison; no aircraft has been purchased, weighed, or tested.

## Recommendation

**My first choice for payload mounting is an X500 v2 ARF kit with a Kakute H7 Mini v1.5 and the matched electronics specified below.** For the strictest budget, especially if a new charger is needed, choose the equivalent S500 DIY build. Choose the S500 development kit when minimizing wiring work matters most.

The resulting shortlist has **three build choices across two airframes**. The original F450 is evaluated separately because its generic propulsion list cannot establish compatibility or payload capability; it is not an ordering recommendation.

| Purchase choice | Parts subtotal | Headroom below $700 | Main tradeoff |
| --- | ---: | ---: | --- |
| **X500 v2 ARF + Kakute H7 Mini v1.5** | **$657.17** | **$42.83** | Best documented payload mounting; custom wiring; existing/borrowed 4S charger needed unless the remaining allowance covers one and fees. |
| **S500 v2 ARF + Kakute H7 Mini v1.5** | **$587.17** | **$112.83** | Best cost margin, including room to source a charger; custom mounting and wiring. |
| **S500 v2 development kit / Pixhawk 6C** | **$669.20** | **$30.80** | Least flight-electronics integration work; existing/borrowed 4S charger needed unless the remaining allowance covers one and fees. |

Subtotals include a new flight battery, matched transmitter/receiver, GNSS/compass, ground telemetry pair, battery monitoring, and aircraft consumables. The DIY totals allow $30 for custom wiring/mounting instead of the kit's $10 allowance. Delivery charges and tax must fit the remaining headroom. Owned chargers' 4S capability remains unknown. Payload mounting and loaded endurance remain to be demonstrated for every choice.

## Project basis

Reviewed:

- [Hardware concept](rough_setup.txt), [compute alternatives](compute.md), and [camera alternatives](camera.md).
- [MSDR slide 11 and associated notes](../MSDR/PaveWatch_MSDR_Rough_Draft_Notes.md), [team review](../MSDR/TEAM-REVIEW.md), and [project status](../AGENTS.md).
- [Current final requirements](../final_docs/PaveWatch_DesignRequirementSpecifications_Final.docx), including S1/FP1 and the survey envelope. This file is an OpenDocument archive despite its extension; document comments are not acceptance requirements.
- Earlier [flight-platform investigation](../sick-application/investigations/01-flight-platform-power-mechanical/findings.md), [LiDAR investigation](../sick-application/investigations/02-picoscan150-sensing-acquisition/findings.md), and [hardware acquisition plan](../sick-application/development-plan/02-hardware-and-acquisition.md).

The aircraft must carry an active acquisition system for **at least 10 minutes**, landing with **at least 20% calibrated usable energy remaining**. The proposed operating envelope is **5–8 m above pavement at 1–2 m/s**. The two owned packs are **2S, 5,200 mAh, 7.4 V**, not 6S. Their connectors and the chargers' supported cell counts remain unknown.

The recorder alternatives in hardware_planning and MSDR differ. Use an installed mass allowance until the computer, camera, storage, cooling, and harness are frozen. A lighter Orange Pi configuration may reduce mass; its recording performance still needs a simultaneous-capture benchmark.

## Payload we actually need to carry

SICK specifies **220 g without the system plug** and a **60 × 60 × 82 mm** sensor body, approximately **0.295 L** as a rectangular bounding box. Those numbers exclude connectors, cables, and the mount. The exact incoming variant and accessories remain unconfirmed. The current large manual could not be opened in full by the browsing tool; its indexed mechanics values agree with the project's earlier extraction. [SICK operating instructions, mechanics/electronics table](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf).

Use this **650 g design target**, with an **800 g upper planning case**. Only the sensor body's mass below is a manufacturer value; the other rows are engineering allowances, not measurements.

| Installed survey item | Target mass |
| --- | ---: |
| picoScan150 body | 220 g |
| System plug, short Ethernet and power harness | 90 g |
| Recorder, cooling, and light protection | 90 g |
| Camera and cable | 20 g |
| SSD and its short cable | 30 g |
| Payload regulator, fuses, filtering | 40 g |
| Rigid plate, brackets, fasteners, retention | 100 g |
| Unallocated mass margin | 60 g |
| **Survey payload target, excluding flight battery and navigation** | **650 g** |

Long industrial cables, a large SSD enclosure, or a heavy printed box can consume the margin quickly. Weigh the received cable assembly before selecting a final aircraft.

For physical fit, provision two **proposed packaging envelopes**:

| Assembly | Proposed outside dimensions | Bounding-box volume |
| --- | --- | ---: |
| LiDAR, camera, connector exits, and bracket | 120 × 100 × 130 mm | 1.560 L |
| Recorder, SSD, regulator, cooling, and cable exits | 120 × 90 × 60 mm | 0.648 L |
| **Sum of separate envelopes** | Distributed installation | **2.208 L** |

These are layout targets, not manufacturer payload capacities or a completed CAD design. The envelopes may need enlargement after checking the supplied M12 plugs and cable bend radii. Mount the recorder separately from the downward sensor assembly where practical, keeping the camera and LiDAR rigid relative to each other.

## Three-airframe comparison: mass and space

| Platform | Evidence for payload mass | Physical payload space | Decision at $700 |
| --- | --- | --- | --- |
| **F450 DIY** | Original DJI F450 documentation lists **800–1,600 g total takeoff weight**, including battery and payload. It does not give a 1.5 kg survey-payload allowance. A generic clone has no established rating from that document. | No verified payload bay or standard rail dimensions for the unspecified candidate frame. A custom plate and tall landing gear are needed for the proposed sensor envelope. Usable volume is **unestablished**. | Existing $405 is a partial, unverified estimate. **Hold** pending an exact BOM and mass/thrust evidence. |
| **Holybro S500 v2** | Manufacturer wording is **1,500 g payload without battery at 70% throttle**. Conservatively count the battery against that allowance: approximately **993 g** remains with the 507 g battery/adapter below. Development-kit dry mass is approximately **915 g**. | Listed overall dimensions **383 × 385 × 240 mm** and **480 mm wheelbase**; adjustable battery mounting, integrated PDB, and landing gear. No dimensioned, unobstructed payload bay or rated volume is published in the reviewed material. Battery and sensor mounting must be resolved together. | **Preferred candidate**, subject to delivered price, charger availability, fit, and endurance. |
| **Holybro X500 v2** | Same published **1,500 g without-battery / 70%-throttle** wording; conservatively approximately **993 g** remains with this battery/adapter. Complete dry aircraft mass must be measured; the listing's **610 g** appears under the frame/ARF specifications and is not a verified development-kit dry mass. | **144 × 144 mm** body plates, **28 mm** plate spacing, **250 mm** dual rails, and **215 mm** landing gear. External sensor mounting is necessary. Usable payload volume is **unestablished**, but the rail interface is better documented. | **DIY configuration: $657.17 before fees.** Full development-kit configuration: $729.20 before fees, over budget. |

Sources: [DJI original Flame Wheel specifications](https://www-v1.dji.com/fr/flame-wheel-arf/spec.html), [S500 development kit](https://holybro.com/products/s500-v2-development-kit), [S500 ARF details](https://holybro.com/products/s500-v2-kit), [X500 development kit](https://holybro.com/products/px4-development-kit-x500-v2), [X500 ARF details](https://holybro.com/products/x500-v2-kits).

**Mass interpretation:** the approximately 993 g values are conservative planning calculations, not battery-inclusive ratings confirmed by Holybro. Ask the supplier to confirm the meaning of its payload wording. Allowances for any additions to the standard aircraft also come out of this margin; a DIY build's electronics mass difference must be reconciled against the rated configuration. At a 650 g survey payload, nominal remaining margin is **343 g**; at 800 g, **193 g**. This is lifting headroom on paper, not proof of endurance or acceptable handling.

The S500 development-kit planning takeoff mass is approximately **915 + 507 + 650 = 2,072 g**, or **2,222 g** with the 800 g payload. These calculations use the published dry figure and allowances; they are not project measurements.

### What volume research can establish

None of these open frames has a published payload capacity in liters. Fit depends on the shape, mounting interface, battery location, optical clearance, and center of gravity.

- **F450:** the exact frame and landing gear are missing, so a numerical usable volume would be invented. With an illustrative dry aircraft allowance of 750–950 g and a 507 g battery/adapter, the original DJI 1.6 kg takeoff envelope leaves only **143–343 g** for payload. This illustrates the risk; it neither rates a clone nor proves that every F450-based redesign fails.
- **S500:** the approximately 240 mm overall height is not a verified rail-to-ground clearance. Use the [assembly manual](https://cdn.shopify.com/s/files/1/0604/5905/7341/files/S500_V2_Kit_AssemblyManual.pdf?v=1646987800) to plan the battery/mount arrangement, then confirm dimensions on the actual frame. Its older Pixhawk 4 / KV880 electronics descriptions do not override the current kit's Pixhawk 6C / KV920 contents.
- **X500:** the gross space between 144 mm square plates separated by 28 mm is **0.581 L**, already occupied in part by structure and electronics. An 82 mm sensor body cannot fit in that gap. The [assembly guide](https://cdn.shopifycdn.net/s/files/1/0604/5905/7341/files/X500_V2_Assembly_Guide_en.pdf?v=1720853913) supports using the external mounting provisions. The 215 mm leg specification alone does not prove clearance for a 130 mm module below the rails.

For either Holybro frame, check the two proposed envelopes with the battery installed. Record the actual mount-to-ground height, clear width between legs, fastener access, cable bends, propeller clearance, and unobstructed downward scan sector. A dimensioned supplier drawing or a physical fit check is needed before calling the payload installation compatible.

## S500 development-kit budget

Prices are USD listings checked during this research, excluding delivery charges and tax unless stated. The radio price is the retailer's price including US tariffs. Stock indicators are not reserved inventory.

| Aircraft item | Selection | Cost |
| --- | --- | ---: |
| Matched frame/propulsion/control/navigation/telemetry | S500 v2 development kit, Pixhawk 6C / M10 / 915 MHz, SKU 30185 | $549.00 |
| Independent manual-control link | RadioLink T8FB(BT) with R8EF receiver | $60.72 |
| Flight battery | Liperior LP50004S35, 4S 5 Ah 35C, XT90 | $37.99 |
| Battery connector adapter | XT90 male to XT60 female, RCB-XT90M-XT60F | $3.49 |
| Transmitter batteries | Allowance; confirm required battery set | $8.00 |
| Small aircraft wiring/retention consumables | Allowance | $10.00 |
| **Aircraft parts subtotal** | | **$669.20** |
| **Amount left within $700** | Must cover delivery charges and tax | **$30.80** |

Sources: [S500 kit](https://holybro.com/products/s500-v2-development-kit), [T8FB/R8EF retailer listing](https://www.robotshop.com/products/radiolink-t8fbbt-24ghz-8ch-transmitter-w-r8ef-8ch-receiver), [battery](https://rcbattery.com/liperior-5000mah-4s-35c-14-8v-lipo-battery-with-xt90-plug.html), [adapter](https://rcbattery.com/xt90-male-to-xt60-female-2pcs-bag.html).

The battery is listed as **495 g, 140 × 43 × 39 mm**; the adapter adds **12 g**. It is a normal 4S LiPo, **14.8 V nominal / 16.8 V full**. Its XT90 connector requires the specified adapter for the kit's XT60 input. It falls within the kit's 4S, 3–5 Ah, 20C+ electrical recommendation. Battery-board dimensions, straps, and installed CG still require checking.

**Budget boundaries:** LiDAR, computer, camera, SSD, payload regulator, and payload mount remain in the separately excluded payload budget. No new charger, RTK equipment, or replacement flight battery is included. If the owned charger cannot balance-charge a 4S LiPo, include a compatible purchased or borrowed charger before claiming a complete usable system below $700. The reserve for fees is small; a delivered quote is essential.

## Parts compatibility

### Development kits

The current S500 kit supplies **four Holybro 2216 KV920 motors, four 20 A BLHeli_S ESCs, 1045 propellers, Pixhawk 6C, PM02 V3, M10 GPS, and SiK telemetry**. Retain this matched motor/propeller/ESC/4S combination. Use the supplied flight-controller power module and signal harnesses; no additional four-in-one ESC is needed. The X500 kit uses the corresponding matched 4S propulsion arrangement. [S500 contents](https://holybro.com/products/s500-v2-development-kit), [X500 contents](https://holybro.com/products/px4-development-kit-x500-v2).

The T8FB and R8EF form a matched radio pair. Use **SBUS** for the flight-controller input, following the received controller's pinout; the receiver is specified for **4.6–10 V**, compatible with a regulated 5 V receiver supply. The radio's Bluetooth configuration feature is not the aircraft-to-laptop telemetry link. [RadioLink specifications](https://www.radiolink.com/t8fb_specification), [manufacturer product information](https://www.radiolink.com/en/t8fb_bt).

### DIY alternative with explicitly selected electronics

These two builds share a compatible electrical architecture using current listed parts; they are not assembled or fit-validated aircraft:

| Item | S500 DIY | X500 DIY |
| --- | ---: | ---: |
| ARF frame with matched propulsion | $259.00 | $329.00 |
| Kakute H7 Mini **v1.5**, SKU 11082 | $82.00 | $82.00 |
| Holybro Micro M10 **IST8310, without case**, SKU 12043 | $27.99 | $27.99 |
| Holybro SiK V3, 100 mW, 915 MHz pair, SKU 17013 | $58.99 | $58.99 |
| PM02 V3 analog current/power module, SKU 15010 | $18.99 | $18.99 |
| Same RC, battery, adapter, and transmitter cells | $110.20 | $110.20 |
| Custom breakout wiring, insulating adapter, retention | $30.00 allowance | $30.00 allowance |
| **Subtotal before delivery charges/tax** | **$587.17** | **$657.17** |

Electronics sources: [Kakute H7 Mini](https://holybro.com/products/kakute-h7-mini), [Micro M10](https://holybro.com/products/micro-m10-gps), [SiK pair](https://holybro.com/products/sik-telemetry-radio-v3), [PM02 V3](https://holybro.com/products/pm02-v3-12s-power-module). The cheaper H7 Mini v1.3 and cased IST8310 Micro M10 showed unavailable; their lower/default prices must not be substituted for the selected available variants.

If the owned chargers cannot handle 4S, an **ISDT 608AC** is a compatible charging candidate: the manufacturer supports **1–6S LiPo balance charging with AC input**, and Buddy RC lists it at **$59.99**. Adding it to the S500 DIY subtotal gives **$647.16**, leaving **$52.84** for any required charging lead, delivery charges, and tax. Verify stock, the supplied AC cord, and the XT60/JST-XH connections in the final quote. This charger does not add airborne mass. [ISDT specifications](https://www.isdt.co/608ac.html?lang=en), [charger listing](https://www.buddyrc.com/products/isdt-608ac-ac-battgo-smart-battery-charger).

Use **ArduCopter 4.6.0 or later supporting KakuteH7Mini v1.5**, rather than the v1.3 `KakuteH7Mini-Nand` target. Manufacturer firmware instructions explicitly distinguish those versions. [Supported firmware](https://docs.holybro.com/autopilot/kakute-h7-v1-v2-mini/kakute-h7-mini/supported-firmware).

| Connection | Compatible implementation |
| --- | --- |
| Battery → ESCs | Battery/adapter → PM02 → ARF PDB → four supplied ESCs. Keep all propulsion grounds common. |
| Motor control | H7 Mini M1–M4 signals and ground → individual ESC signal inputs using a custom breakout. Use a supported PWM mode and verify motor order with propellers removed. A connector advertised for a four-in-one ESC does not require using one. |
| GNSS and compass | Micro M10 powered from regulated **5 V**; GNSS TX/RX cross to H7 UART3; compass SDA/SCL to I2C. The Micro M10 requires **4.7–5.2 V**, so use the 5 V rail. |
| RC | R8EF **SBUS** output → H7 R6; regulated 5 V and ground. ArduPilot documents `SERIAL6_PROTOCOL=23` and `SERIAL6_OPTIONS=3` for SBUS. PPM is not supported on this board's ArduPilot input. |
| Ground telemetry | SiK air unit → UART2 TX/RX, 5 V, ground; USB unit → laptop. Carry MAVLink commands/health, not raw LiDAR or images. |
| Recorder pose link | UART4 TX/RX/ground → recorder's compatible 3.3 V UART. Configure MAVLink; do not connect battery voltage to the computer. |
| Battery monitoring | H7 built-in voltage measurement plus PM02 analog current output → CURRENT input. Use the module's calibration, not a four-in-one ESC's scale. Verify ADC limits and measure calibration before installation. |

Sources: [ArduPilot H7 Mini connections and mapping](https://ardupilot.org/copter/docs/common-holybro-kakuteh7mini.html), [Holybro connector pinout](https://docs.holybro.com/autopilot/kakute-h7-v1-v2-mini/kakute-h7-mini/pinout), [Micro M10 electrical specifications](https://holybro.com/products/micro-m10-gps).

The H7 uses its own battery-input BEC in this wiring plan; the PM02's regulated output is not connected in parallel with it. A custom current-signal breakout is required. Holybro rates the PM02 PCB at 60 A continuous, but its supplied connector/wire assembly at **30 A continuous**, so that assembly limits sustained current unless appropriately replaced. The S500 PDB is listed at **60 A continuous / 100 A burst**. A 20 A rating on each of four ESCs does not make the shared wiring an 80 A continuous path. [PM02 specification](https://holybro.com/products/pm02-v3-12s-power-module), [S500 PDB specification](https://holybro.com/products/s500-v2-kit).

Use an insulating adapter plate and the H7's **20 × 20 mm mounting pattern**; an ARF kit's Pixhawk mounting provisions are not automatically a direct fit. The GPS JST-GH cable also requires a verified breakout to the H7's pads. These small adapters and harnesses are part of the fabrication work; their actual cost must fit the $30 allowance or be added to the quote. The survey sensor's rigid mount remains in the separately excluded payload budget.

### Why the existing F450 list is not a compatible released BOM

- “2212” is a motor size, not an exact motor/KV/voltage/propeller specification. The frame/propulsion bundle needs an actual supplier SKU and thrust/current data at the selected voltage.
- Select **four individual ESCs or one four-in-one ESC**. The rough list contains a propulsion combo with ESCs and a controller stack with another ESC set. The electrical topology and price must be reconciled.
- The F405 V4 supports a documented ArduPilot target, but the manufacturer's V4 stack page currently says **discontinued**. Replacing it with a V5 changes wiring and firmware; its stack page also says discontinued. Source the exact board before treating the old price as available. [V4 listing](https://www.speedybee.com/speedybee-f405-v4-bls-55a-30x30-fc-esc-stack/), [ArduPilot V4 documentation](https://ardupilot.org/copter/docs/common-speedybeef4-v3.html), [V5 listing](https://www.speedybee.com/speedybee-f405-v5-55a-stack/).
- The proposed F9P rover provides a compass in the documented model, but needs compatible corrections for RTK operation. Its GNSS performance does not establish surface height accuracy. [F9P rover specifications](https://holybro.com/products/h-rtk-f9p-gnss-series).
- The owned **2S** packs do not satisfy the proposed SpeedyBee **3S–6S** input or the Holybro kits' 4S propulsion recommendation. A connector change does not change voltage. A single 2S pack is also below the picoScan's documented **9–30 V** input range. No pack-combining modification is proposed here.

## Shared payload power and data integration

For a 4S aircraft, provision a separately fused LiDAR branch within the received sensor's electrical instructions and a dedicated regulated supply for the recorder/camera/SSD. The sensor's documented 9–30 V range includes a normal 4S pack's voltage; verify startup, cable drop, and transients on the actual unit. Do not power the computer from a telemetry port or assume the flight controller's peripheral BEC can support it. [SICK manual](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf).

LiDAR connects by Ethernet to the recorder; camera and storage also terminate there. A Pi 4 uses the standard 15-pin camera cable; a Pi 5 needs the appropriate 22-to-15-pin cable for Camera Module 3. A USB camera uses a USB connection instead. [Raspberry Pi camera connections](https://www.raspberrypi.com/documentation/accessories/camera.html).

The budget baseline uses ordinary **M10 GNSS**, not RTK. Final survey accuracy still requires independent validation against the project's S3 bounds, using the documented pose/registration workflow. Adding an F9P and correction infrastructure requires a revised cost and mass budget; an RTK receiver is not mandated by name in the current requirements.

## Endurance is the remaining selection risk

Holybro's approximately **18-minute hover** statement is for **no additional payload**. It cannot establish the project's loaded ten-minute flight with reserve. [S500 listing](https://holybro.com/products/s500-v2-development-kit), [X500 listing](https://holybro.com/products/px4-development-kit-x500-v2).

For the selected 4S 5 Ah battery, nominal energy is **74 Wh**. If calibrated usable energy equaled nominal energy, retaining 20% after ten minutes would allow only **355 W average total electrical power**, approximately **24 A at 14.8 V**, including the acquisition payload. Actual usable energy can be lower. This is an energy-budget limit, not a prediction of either aircraft's consumption.

Before final platform acceptance:

1. Weigh the complete payload and aircraft; replace every mass allowance.
2. Complete a dimensioned installation drawing using the received connectors, battery, and actual landing-gear clearances.
3. Confirm the delivered aircraft quote and 4S charging arrangement within the ceiling.
4. Check simultaneous recorder operation, stable power, battery-current calibration, and RC/telemetry/pose links.
5. Conduct the required **three authorized loaded flights** with acquisition active, establishing at least ten minutes and at least 20% calibrated usable energy remaining.

If the S500 fails the endurance requirement, rework payload mass or the propulsion/energy design with new supporting data. The X500's shared propulsion specification does not, by itself, demonstrate an endurance solution.

## Suggested MSDR disposition

Replace the provisional preference for the generic F450 build with: **“Three purchase choices are X500 v2 ARF/Kakute H7 Mini for payload mounting, S500 v2 ARF/Kakute H7 Mini for cost margin, and the S500 v2/Pixhawk 6C development kit for simpler integration. Final selection depends on delivered cost, 4S charging, installed fit, and loaded endurance. F450 remains an unqualified DIY concept pending exact propulsion and mass evidence.”**

The existing presentation and source planning files have not been modified by this research.
