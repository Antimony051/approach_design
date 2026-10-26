# Subsystem map

The six charter subsystems remain the work boundaries. Numbering follows the signed charter; shared integration is maintained outside these folders.

| Code | Brief | Lead |
| --- | --- | --- |
| FP | [Flight Platform, Power & Control](01-flight-platform-power-control/README.md) | Ankit Dhakal |
| DT | [Diagnostics & Telemetry](02-diagnostics-telemetry/README.md) | Shisir Baral |
| SA | [Sensor Payload & Data Acquisition](03-sensor-payload-acquisition/README.md) | Abhinav Dhakal |
| GC | [Ground Control & Communications](04-ground-control-communications/README.md) | Pritam Adhikari |
| PC | [Data Processing & Change Detection](05-data-processing-change-detection/README.md) | Aalok Uprety |
| RD | [Reporting, Database & Alerts](06-reporting-database-alerts/README.md) | Saugat Karki |

Subsystem hardware can be shared: for example, acquisition and diagnostics may use one recorder. A shared implementation must have one BOM owner and explicit interfaces, not two copies in the budget.
