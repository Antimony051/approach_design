# FP — Flight Platform, Power & Control

Lead: **Ankit Dhakal**. Charter support: **Aalok Uprety**. Requirements: **S1, S6, FP1–FP4**.

Updated November 16, 2026. **Status: PW-APPROACH-01 selected in SRC-034 §§3.3.1/3.4; installed design and performance unverified.**

## Required function

Carry the acquisition payload, fly supervised survey legs, permit pilot takeover, provide timestamped pose, and distribute aircraft/payload power. Power remains within FP, not a seventh subsystem.

## Selected approach and alternatives

Use a custom 500 mm hybrid X frame: CNC carbon-fiber center plates and tube arms form the primary load path; PA6-CF clamps, landing fittings, sensor carrier, and electronics mounts complete the structure. Holybro X500 v2 CAD supplies a dimensional reference, not a purchased frame or a transferable payload rating.

A MicoAir H743v2-AIO-35A combines flight control and four 35 A ESC channels. The document selects **PX4 1.16.0 / MicoAir743v2**, with QGroundControl and M10G GNSS/compass. Confirm the exact target/build and revision before flashing. Propulsion is **4 × SunnySky X2216 880 KV**, **Master Airscrew MR 10 × 4.5-inch props**, and **4S 14.8 V nominal 5,200 mAh LiPo**. Avoid separate duplicate ESC purchase lines. Pocket ELRS/RP1 V2 and separate MAVLink laptop telemetry are shared with GC/DT.

The final approach compares X500 ARF/Kakute H7 Mini v1.5 ($657.17) and S500/Pixhawk 6C ($669.20) with the chosen custom frame ($447.09 aircraft hardware), all before fees and unverified. The original F450/SpeedyBee route remains a historical alternative; it is not combined with the active configuration.

## Energy, mass, and installation

Provide separate protected/regulation-matched LiDAR and recorder branches, independent of flight-control power. Source supply guidance for the sensor is 9–30 V; regulator parts, pinouts, transients, grounds, and current limits remain open. The source's **2.25 kg all-up target**, **440–550 g sensing-payload estimate**, and **650 g payload target** need a complete mass ledger and installed CG/clearance checks.

The [energy screen](../../integration/flight-energy-screen.md) reproduces the source's **~8.5 min** estimate using assumed usable energy and APC 10 × 4.7 proxy data. It falls below the unchanged **≥10 min / ≥20% usable reserve** requirement. No matched Master Airscrew thrust/current or loaded endurance result exists here. Existing **2S** packs are not the selected 4S supply; charger capability and connectors remain unknown.

## Remaining implementation work

- Release fabrication drawings, fasteners/load paths, landing/prop/optics clearance, whole-plate vibration isolation if needed, cable routing, battery placement, and actual mass/CG.
- Verify PX4 board support, motor outputs/order, integrated ESC limits, full FC UART/I2C/RC/power allocation, and current/voltage calibration.
- Reconcile **0.25–1 m/s** survey planning with **FP2 1–2 m/s**, preserving 5–8 m height (Q-17).
- Reconcile delivered aircraft under $700 and the $1,000 whole-design limit; identify a usable 4S charger and leads (Q-09/10).
- Map takeover, return, estimator/link failsafes, and prior proximity interruption intent onto PX4 with GC/DT. Additional proximity hardware remains unselected.

Historical leads: SRC-008/010/020/028. Their ArduPilot/H7 wiring and propulsion assumptions are not the selected PX4/AIO installation.

## Shared design records

Maintain one owning row per component in [the BOM](../../procurement/bom.csv), exact connections in [interfaces](../../integration/interfaces.csv), and affected [power](../../integration/power-budget.csv), [mass/fit](../../integration/mass-and-fit.csv), [compatibility](../../procurement/compatibility.csv), [verification](../../verification/plan.md), and [decisions](../../decisions/decision-log.md). Design selection is not purchase authorization or test evidence. Blank installed/price values remain unknown.

Current source: [SRC-034 final approach](../../references/new-evidence/2026-11-16-final-approach/PaveWatch_Approach_Final.docx), [readable text SRC-035](../../references/new-evidence/2026-11-16-final-approach/approach-text.txt), and [reconciliation](../../references/new-evidence/2026-11-16-final-approach.md). Earlier source IDs resolve through [the source index](../../references/source-index.md).
