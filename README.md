# PaveWatch hardware design workspace

Prepared **October 24, 2026** from existing project material. This is the working home for whole-project hardware design, component selection, integration, and procurement planning. No new external research, hardware selection, purchases, or tests were performed to create it.

Start with [the next-agent task](NEXT_AGENT_TASK.md), [project state](system/project-state.md), [requirements](system/requirements.md), and [open decisions](decisions/open-questions.md). Folder-level [agent instructions](AGENTS.md) explain evidence and update conventions.

## Where work belongs

| Folder | Contents |
| --- | --- |
| [system](system/architecture.md) | Scope, known state, requirements, functional architecture |
| [subsystems](subsystems/README.md) | The six charter subsystems, responsibilities, existing ideas, and research handoffs |
| [integration](integration/README.md) | Shared interfaces, power, mass, mechanical fit, timing, frames, and assembly planning |
| [procurement](procurement/README.md) | Unselected BOM skeleton, compatibility checks, and budget accounting |
| [decisions](decisions/decision-log.md) | Confirmed inputs, dated decisions, conflicts, and unresolved choices |
| [verification](verification/plan.md) | Acceptance targets and the evidence needed to evaluate the chosen design |
| [references](references/README.md) | Portable snapshots, document extracts, provenance manifest, and space for future evidence |
| [templates](templates/research-note.md) | Research and decision templates |

The CSVs are editable planning worksheets. Blank numerical cells mean **unknown**, never zero. Seeded descriptions identify functions to provision; they are not a shopping cart. Candidate prices in references are dated planning inputs. No subsystem has an approved, complete purchasing BOM here.

## Intended workflow

1. Read current constraints and source conflicts before selecting parts.
2. Investigate subsystem options against their defined functions; retain exact evidence and alternatives.
3. Resolve coupled choices together: aircraft/controller/firmware; camera/recorder/storage; pose/timing/reference method; and installed power/mechanics.
4. Update shared interfaces and budgets as candidates become specific. Record decisions and their consequences.
5. Produce one coherent installed design, itemized BOM, wiring/pin map, mechanical layout, assembly instructions, and verification plan. Track bench demonstration equipment and recurring costs too.
6. Give the team a reviewable package with unresolved items and delivered totals. Ordering is a separate action when requested.

This folder is usable on its own: the reference manifest includes snapshots or readable extracts of the key source files. The rest of the repository remains intact. Snapshots preserve their original wording, including outdated claims; consult the source guide and current-state files before using them as requirements.
