# Design decision log

Record the decision, date, source/reviewer, rationale, alternatives, affected BOM/IF/requirement IDs, and pending verification. A planning preference can be changed with evidence; user-confirmed constraints should not be silently changed.

| ID | Date / evidence | State | Decision or input | Consequence |
| --- | --- | --- | --- | --- |
| D-001 | October 23 context / user budget clarification, SRC-001/SRC-008 | Confirmed constraint | Complete aircraft under $700; recording payload excluded | Track complete delivered aircraft and separate project scopes |
| D-002 | October 22–23, SRC-001 | Confirmed inventory correction | Two owned packs are 2S, not 6S | Voltage/charger compatibility remains open |
| D-003 | October 23, SRC-001/SRC-004 | Confirmed requirement correction | FP4 uses ≤5°, including test | Retain original document discrepancy in provenance |
| D-004 | Current requirements and latest MSDR, SRC-002/SRC-003 | Scope baseline | Single-survey assessment; previous survey optional | Historical comparison must not block baseline function |
| D-005 | October 23 demo package, SRC-006/SRC-007 | Proposed demo scope | Real sensors, stand/carriage, local record/replay, measured or post-processed poses; no flight required | Plan bench equipment separately; no airborne validation claim |
| D-006 | Final saved MSDR slides 13–15, SRC-003 | Planning preference | X500 ARF/H7 Mini v1.5, Orange Pi Zero 3, InnoMaker color USB | Exact installed BOM and interfaces not frozen |
| D-007 | October 23 context / latest MSDR | Candidate retained | Keep F450/SpeedyBee DIY concept as an option | Generic list needs exact compatible parts and payload evidence |

No new implementation decisions were made during consolidation. Use [the decision template](../templates/decision-record.md) for substantive future selections. Current design blockers/dependencies are in [open questions](open-questions.md).
