# Flight energy and thrust screening — PW-APPROACH-01

November 16, 2026. Source: SRC-034 §3.3.1, reproduced as a planning calculation. These are assumptions and proxy published values quoted by the approach, not fresh manufacturer checks or measured project performance. S1/FP1 remains **≥10 min loaded with ≥20% calibrated usable energy remaining**, demonstrated in three authorized flights.

| Input / calculation | Value | Status |
| --- | --- | --- |
| Selected battery | 4S, 14.8 V nominal, 5.2 Ah | Exact pack/condition/charging unresolved |
| Nominal energy | 14.8 × 5.2 = **76.96 Wh** | Nameplate calculation, not usable-energy measurement |
| Assumed usable energy | 76.96 × 0.80 = **61.568 Wh** | 80% factor is an assumption requiring calibration |
| Reserved usable energy | 61.568 × 0.20 = **12.3136 Wh** | 20% reserve applied to assumed usable energy |
| Energy allowed for flight | 61.568 × 0.80 = **49.2544 Wh** | Includes every airborne load/loss |
| All-up design target | **2.25 kg** | Not weighed or a verified maximum takeoff mass |
| Hover thrust per motor | 2.25 × 9.81 / 4 = **5.52 N ≈563 gf** | Ideal symmetric hover; no maneuver margin |
| 2:1 static thrust screen | **1,125 gf per motor** | Design screening ratio, not a new acceptance requirement |
| Proxy propulsion power | **~326 W total**, roughly 82 W/motor | Source APC 10 × 4.7 curve at 14.8 V |
| Illustrative avionics/payload | **20 W total** | Includes all non-propulsion loads for this screen; no individual load measurement |
| Illustrative total power | 326 + 20 = **346 W** | Conversion/harness treatment not fully itemized |
| Flight time | 49.2544 / 346 × 60 = **8.54 min** | Below the ≥10 min requirement |
| Maximum average power for 10 min at assumed energy/reserve | 49.2544 / (10/60) = **295.53 W** | Derived limit under these assumptions only |

The source quotes ~1,200 gf at 17.4 A / 257.5 W per motor at 14.8 V for the **APC 10 × 4.7**. The selected propeller is **Master Airscrew MR 10 × 4.5**. Neither its thrust nor its current follows from the proxy curve. Do not equate the 35 A channel label with verified installed continuous capability or assume voltage sag/heat/wiring are covered.

For branch loads the source proposes `E = V × (I_active × d + I_idle × (1 − d)) × t / efficiency`, with time in hours. Use real active/idle/startup states, converter losses, flight phases and all loads once in the completed budget. [power-budget.csv](power-budget.csv) keeps per-load unknowns blank; do not add the 20 W screen to individually budgeted avionics/payload again.

Q-18 remains open: obtain matched motor/prop/voltage data, complete actual mass/CG and current/thermal budgets, measure usable battery energy, and evaluate a revised feasible configuration. Larger batteries can increase mass and hover demand; do not scale flight time by capacity alone. Two existing 2S packs are owned inventory, not an approved series-connected 4S substitute. No alternative battery/propulsion change is selected by this screen.
