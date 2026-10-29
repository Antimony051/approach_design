# Ground-control workflow documentation check

Checked October 28, 2026. Published software documentation only; no physical or simulated tests. No exact project hardware is selected, so none of these checks establish installed compatibility. These are live documentation pages; behavior must be rechecked against the eventual installed firmware and GCS versions.

| ID | Source / version / section | Supported statement | Limitation |
| --- | --- | --- | --- |
| E1 | [QGroundControl Stable V5.1, Plan View](https://docs.qgroundcontrol.com/Stable_V5.1/en/qgc-user-guide/plan_view/plan_view.html), Planning a Mission and Planned Home Position | Map-based waypoint editing/upload exists; planned home is an estimate and differs from actual vehicle home. | Does not establish map accuracy, project stack selection, or site safety. |
| E2 | [ArduPilot Copter, Optical Flow Sensor Testing and Setup](https://ardupilot.org/copter/docs/common-optical-flow-sensor-setup.html), Testing the sensor / Rangefinder / calibration and flight setup | Optical-flow use requires sensor/rangefinder checks, calibration, and estimator configuration. | Live/unversioned guide; no support or accuracy claim for our recorder camera or picoScan installation. |
| E3 | [ExpressLRS, MAVLink](https://www.expresslrs.org/software/mavlink/), Hardware Requirements, Flight Controller Setup, Connecting to the Ground Control Station | A supported RC/MAVLink shared-link architecture and laptop access methods exist; hardware/firmware/configuration prerequisites apply. | No specific transmitter/receiver selected; no project latency, range, load, or independent-failure test. |
| E4 | [MAVLink, Mission (Plan) Protocol](https://mavlink.io/en/services/mission.html), Upload a Mission / Download a Mission / Timeouts and Retries | Mission transfer has explicit acceptance/error/retry semantics and download operations. | Protocol specification is not evidence of exact autopilot implementation. An upload acknowledgement alone is not project-specific route readback verification. |

The draft review's proposed workflow and risk analysis are engineering judgments informed by these sources and existing project requirements. A single known coordinate, local-frame labels, and post-flight processing are not evidence of live navigation accuracy.
