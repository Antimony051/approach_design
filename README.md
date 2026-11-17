# PaveWatch hardware design workspace

Updated **November 16, 2026** to match [the final approach (SRC-034)](references/new-evidence/2026-11-16-final-approach/PaveWatch_Approach_Final.docx). This workspace covers whole-project hardware design, integration, and procurement planning. Its October 24 source snapshots remain intact. This update incorporates document selections and reported status; it adds no purchases, external verification, or hardware tests.

The current configuration, **PW-APPROACH-01**, uses a custom 500 mm hybrid carbon-fiber/PA6-CF frame, MicoAir H743v2-AIO-35A with PX4 1.16.0, four SunnySky X2216 880 KV motors, Master Airscrew MR 10 × 4.5-inch props, and a 4S 5,200 mAh battery. The payload uses the supplied picoScan150 Pro, Raspberry Pi 4 Model B, Camera Module 3, and SanDisk Extreme 128 GB microSD in a USB 3 reader separate from boot media. RadioMaster Pocket ELRS/RP1 V2 handles pilot control and intended critical alerts; a separate MAVLink link serves the laptop. Post-flight processing feeds a hosted reporting portal with PostgreSQL/PostGIS and cloud evidence storage; processing deployment is still undecided.

The [source reconciliation](references/new-evidence/2026-11-16-final-approach.md) distinguishes selections, estimates, reported sensor receipt/streaming, and pending checks. The user confirmed approximately **0.25–1 m/s** planned survey speed (D-019); older FP2 test wording still needs alignment. Remaining feasibility issues include the ~8.5-minute endurance estimate versus the ≥10-minute target and the unreconciled $1,000 whole-design limit alongside the under-$700 aircraft ceiling.

[Camera/LiDAR timing notes](integration/camera-lidar-timing.md) from the supplied November 16 document (SRC-036) add per-row exposure times, per-beam acquisition times, Pi/PTP clock mapping, calibration and proposed ≤3 ms P95 bench goals. Its 3 m/binned 10–15 fps/SSD test profile is recorded separately from the current flight plan; timing remains unmeasured and SA2's ≤20 ms requirement is unchanged.

For recorder login and development, use [the Raspberry Pi connection guide](integration/raspberry-pi-access.md): November16 records show Tailscale/OpenSSH access to `picoscan-pi` at `100.72.89.22`. It uses the private key supplied by Shisir and the shared `pavewatch` login, plus Tailscale invitations, the trusted host fingerprint, original-laptop wired maintenance fallback, and the distinction from sensor Ethernet/PTP. On the Pi, start with `~/README.md` and `~/AGENTS.md`; use `/home/pavewatch/03-sensor-payload-acquisition` for scripts/docs and `~/data/sessions/` for recordings. Existing Pi4/Bullseye/32GB boot media are recorded as bench hardware; capture/timing readiness still needs qualification.

Start with [the next-agent task](NEXT_AGENT_TASK.md), [project state](system/project-state.md), [requirements](system/requirements.md), and [open decisions](decisions/open-questions.md). Folder-level [agent instructions](AGENTS.md) explain evidence and update conventions.

## Where work belongs

| Folder | Contents |
| --- | --- |
| [system](system/architecture.md) | Scope, known state, requirements, functional architecture |
| [subsystems](subsystems/README.md) | The six charter subsystems, responsibilities, existing ideas, and research handoffs |
| [integration](integration/README.md) | Shared interfaces, power, mass, mechanical fit, timing, frames, and assembly planning |
| [procurement](procurement/README.md) | Document-selected BOM with unresolved accessories, compatibility checks, and budget accounting |
| [decisions](decisions/decision-log.md) | Confirmed inputs, dated decisions, conflicts, and unresolved choices |
| [verification](verification/plan.md) | Acceptance targets and the evidence needed to evaluate the chosen design |
| [references](references/README.md) | Portable snapshots, document extracts, provenance manifest, and space for future evidence |
| [templates](templates/research-note.md) | Research and decision templates |

The CSVs are editable planning worksheets for PW-APPROACH-01. Blank numerical cells mean **unknown**, never zero. Source selections and price estimates are identified, but accessories, pinouts, installed values, and delivered costs remain unresolved. No subsystem has an approved, complete purchasing BOM here.

## Intended workflow

1. Read current constraints and source conflicts before selecting parts.
2. Investigate subsystem options against their defined functions; retain exact evidence and alternatives.
3. Resolve coupled choices together: aircraft/controller/firmware; camera/recorder/storage; pose/timing/reference method; and installed power/mechanics.
4. Update shared interfaces and budgets as candidates become specific. Record decisions and their consequences.
5. Produce one coherent installed design, itemized BOM, wiring/pin map, mechanical layout, assembly instructions, and verification plan. Track bench demonstration equipment and recurring costs too.
6. Give the team a reviewable package with unresolved items and delivered totals. Ordering is a separate action when requested.

This folder is usable on its own: the reference manifest includes snapshots or readable extracts of the key source files. The rest of the repository remains intact. Snapshots preserve their original wording, including outdated claims; consult the source guide and current-state files before using them as requirements.
