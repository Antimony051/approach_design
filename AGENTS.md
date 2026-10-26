# Working in hardware_design

This is a design workspace, not a completed design. Read README.md, NEXT_AGENT_TASK.md, system/project-state.md, system/requirements.md, and decisions/open-questions.md first. Follow the repository's UV rule for Python; never edit canvas_archive/.

- Preserve the six charter subsystem boundaries. Shared power, mounting, timing, and interface choices belong in integration/ so they have one maintained definition.
- The user requested this folder's creation without new research. Its seeded content only consolidates existing material. Future design/research tasks may use external research when authorized; do not describe this consolidation as fresh manufacturer verification.
- Separate user-confirmed constraints, document requirements, historical proposals, engineering allocations/calculations, manufacturer statements, and project measurements. A recommendation or slide label is not purchase authorization or test evidence.
- Keep references/snapshot/ and references/extracted/ as the initial record. Put later research in references/new-evidence/ with date, exact variant, direct source, relevant section, and limitations. Do not overwrite old source evidence.
- Working summaries take the October 23 context and user corrections into account. The original final requirements still contain the FP4 1° test inconsistency; the user resolved it to ≤5°. Log unresolved contradictions instead of silently changing requirements.
- Aircraft ceiling is strictly under $700 including flight battery, RC, and navigation, excluding supplied LiDAR and recording payload. Keep whole-project acquisition, ground equipment, shipping/tax, and recurring costs visible separately; their current available allocation is unresolved.
- Existing packs are TWO 2S 5,200 mAh 50C, 7.4 V nominal. Connectors and charger cell support are unknown. Do not treat these as 6S, assume series use, or substitute a connector change for voltage compatibility.
- X500/Orange Pi/InnoMaker are the latest presentation's planning direction, not a frozen or procured build. Preserve the original F450 route as a candidate requiring exact compatible parts and evidence. Do not combine mutually exclusive builds into one BOM.
- For DIY parts verify exact revisions, propulsion at the chosen voltage/prop, firmware target, port allocation, signal levels, connectors/pinouts, current limits, timing access, and installed clearances. Record documentation checks separately from physical tests.
- Use stable IDs in requirements, interfaces, decisions, and BOM rows. Each purchased or fabricated item must have one owning row; cross-reference kit contents instead of charging for them twice. Unknown numerical values stay blank with a reason/status.
- After a design change update the subsystem brief, decision log, affected interfaces, budgets, compatibility checks, and verification implications. Do useful independent work while questions remain open.
- Deliver concrete planning artifacts. Do not order, publish, contact others, or claim passed tests as a consequence of a research task alone.
