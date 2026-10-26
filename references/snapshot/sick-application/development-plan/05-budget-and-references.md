### 16. Initial prototype acquisition budget

The planned incremental hardware allocation is **$999**, including a $55 integration and procurement reserve. This is an engineering estimate subject to final supplier quotations. The picoScan150 and its challenge accessories are treated as the competition-provided sensing resource. [1]

| Item | Planned USD | Basis |
|---|---:|---|
| X500 v2 development kit: Pixhawk 6C, M10 GNSS, 915 MHz telemetry | 579 | Manufacturer configuration reference [3] |
| 4S 5 Ah battery | 80 | Procurement allowance |
| Raspberry Pi 5, 2 GB | 65 | Board allowance based on research record [4] |
| Camera Module 3, standard color | 25 | Manufacturer starting price [5] |
| 256 GB USB SSD and boot storage | 45 | Procurement allowance |
| Active cooling | 10 | Procurement allowance |
| Payload regulator, filters and fuses | 45 | Integration allowance |
| Payload plate, printed protection and retention hardware | 40 | Fabrication allowance |
| CSI/serial interfaces and supporting cables | 20 | Integration allowance |
| Spare propellers, wiring and connectors | 20 | Consumable allowance |
| Calibration markers and test materials | 15 | Consumable allowance |
| Integration, shipping and tax reserve | 55 | Reserve; reconcile with final quotations |
| **Total planned acquisition** | **999** | **Estimate, not a supplier quote** |

The operating environment includes a ground-control workstation, compatible manual RC system, charging equipment, reference-measurement tools, and cloud services. These are separate from this incremental payload/aircraft acquisition table; the figure is not the replacement cost of the complete operating environment. The exact challenge accessory package and all purchase quotations will be confirmed before procurement. Any additional sensor cable, equipment, or shipping requirement must be reconciled within the approved allocation.

Cloud operating expenditure will be tracked separately through measured storage, compute and transfer use, with a spending limit established before deployment. The architecture uses post-flight batch jobs and private storage so resource consumption can be measured per survey. No recurring-cost or commercial unit-price claim is made at this stage.

### 17. References

Manufacturer specifications are design inputs, not team measurements. The supporting investigations were researched on September 19, 2026. Product pages [1, 3–6, 10] were revisited during integration on that date; the remaining references are retained from the investigation source record. Specifications, configurations and purchase prices will be rechecked at commissioning/procurement.

1. SICK, [SICK$10K Challenge, 2026–2027](https://s.sick.com/us-en-SICK10KChallenge-2026). Challenge scope and supplied sensor/accessories.
2. SICK, [picoScan150 Operating Instructions](https://www.sick.com/media/docs/1/91/691/operating_instructions_picoscan150_2d_lidar_sensors_en_im0106691.pdf), document 8028323. Variant-dependent sensing, interfaces, electrical and mechanical integration. Detailed source review is recorded in investigation 02.
3. Holybro, [PX4 Development Kit — X500 v2](https://holybro.com/products/px4-development-kit-x500-v2). Select the Pixhawk 6C/M10/915 MHz configuration; frame-only and other controller options are different products.
4. Raspberry Pi, [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) and [power documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html). Acquisition interfaces and supply requirements; board price allowance retained from investigation 04.
5. Raspberry Pi, [Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/). Imaging specifications, control interfaces and starting price.
6. PX4, [Missions](https://docs.px4.io/main/en/flying/missions). Mission workflow; a specific stable firmware/GCS configuration will be frozen for testing.
7. OpenCV, [Camera calibration and 3D reconstruction](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html). Camera models and calibrated projection.
8. Open3D, [ICP registration](https://www.open3d.org/docs/latest/tutorial/t_pipelines/t_icp_registration.html). Proposed geometric registration implementation.
9. Yan and Zhang, [UAV-PDD2023 dataset](https://doi.org/10.5281/zenodo.8429208). Aerial RGB demonstration source; dataset provenance and limitations assessed in investigation 07.
10. Fan, [Stereo Pothole Datasets](https://github.com/ruirangerfan/stereo_pothole_datasets). Paired imagery/stereo geometry for software fusion evaluation.
