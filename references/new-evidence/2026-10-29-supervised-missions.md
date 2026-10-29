# Supervised mission / stabilization documentation

Reviewed October 29, 2026. Published ArduPilot Copter live documentation; no release pinned and no project hardware selected. No bench, simulation, or flight tests were performed. Recheck the eventual firmware build, enabled features, sensors, and mode configuration before adopting any behavior.

| ID | Direct source / relevant section | Published behavior and design implication | Limitation |
| --- | --- | --- | --- |
| O1 | [Auto Mode](https://ardupilot.org/copter/docs/auto-mode.html), Overview / Starting a Mission | Waypoint transitions can curve; explicit mode changes permit takeover and return to AUTO. | Earlier discussion checked this page; actual defaults/version/configuration need verification. A waypoint line is not a clearance guarantee. |
| O2 | [Mission Rewind on Resume](https://ardupilot.org/copter/docs/common-mission-rewind.html), introduction / Configuration / Limitations | Ordinary resumption can go directly to the last active waypoint; optional rewind returns to earlier track. | Rejoin safety, coverage, command execution, and exact firmware behavior remain project checks. |
| O3 | [Simple Object Avoidance](https://ardupilot.org/copter/docs/common-simple-object-avoidance.html), Algorithms / Stop Avoidance / Advanced Configuration | Avoidance differs by mode; AUTO/GUIDED uses separately documented methods. Stopping depends on tuning and motion. | Does not prove an automatic stop-and-hold policy for the proposed aircraft. Sensor field of view and object detectability are untested. |
| O4 | [Stabilize Mode](https://ardupilot.org/copter/docs/stabilize-mode.html), Overview | Self-levels roll/pitch; pilot must correct drift and manage throttle. | Supports the distinction between attitude stabilization and position holding; not an endorsement of a project fallback mode. |
| O5 | [Altitude Hold Mode](https://ardupilot.org/copter/docs/altholdmode.html), Overview | Adds throttle/altitude control; barometer is a primary altitude source, with supported rangefinder use. | Altitude control does not establish horizontal holding or IMU-only hover. |
| O6 | [Brake Mode](https://ardupilot.org/copter/docs/brake-mode.html), Overview / Controls | Requires a valid position estimate and ignores pilot inputs until switched out of the mode. | Cannot be assumed to provide pilot maneuverability or a safe response to invalid positioning. |

IMU integration drift and the need to separate attitude, velocity, position, and altitude control are engineering explanations. Desired proximity interruption, manual detours, skipped coverage, early ending, and deliberate resumption come from the user discussion; they are operating requirements/preferences, not demonstrated autopilot capabilities.
