# Working in hardware_design

This is a design workspace, not a completed design. Read README.md, NEXT_AGENT_TASK.md, system/project-state.md, system/requirements.md, and decisions/open-questions.md first. Follow the repository's UV rule for Python; never edit canvas_archive/.

- Preserve the six charter subsystem boundaries. Shared power, mounting, timing, and interface choices belong in integration/ so they have one maintained definition.
- The user requested this folder's creation without new research. Its seeded content only consolidates existing material. Future design/research tasks may use external research when authorized; do not describe this consolidation as fresh manufacturer verification.
- Separate user-confirmed constraints, document requirements, historical proposals, engineering allocations/calculations, manufacturer statements, and project measurements. A recommendation or slide label is not purchase authorization or test evidence.
- Keep references/snapshot/ and references/extracted/ as the initial record. Put later research in references/new-evidence/ with date, exact variant, direct source, relevant section, and limitations. Do not overwrite old source evidence.
- Working summaries take the October 23 context and user corrections into account. The original final requirements still contain the FP4 1° test inconsistency; the user resolved it to ≤5°. Log unresolved contradictions instead of silently changing requirements.
- Aircraft ceiling is strictly under $700 including flight battery, RC, and navigation, excluding supplied LiDAR and recording payload. Keep whole-project acquisition, ground equipment, shipping/tax, and recurring costs visible separately; their current available allocation is unresolved.
- Existing packs are TWO 2S 5,200 mAh 50C, 7.4 V nominal. Connectors and charger cell support are unknown. Do not treat these as 6S, assume series use, or substitute a connector change for voltage compatibility.
- Current baseline is SRC-034, final_docs/PaveWatch_Approach_Final.docx, incorporated November 16, 2026: custom 500 mm hybrid frame, MicoAir H743v2-AIO-35A/PX4 1.16.0, Raspberry Pi 4, Camera Module 3, and SanDisk Extreme 128 GB survey card in a USB 3 reader. X500/H7/Orange Pi/InnoMaker and the original F450 route are alternatives/history. Do not combine mutually exclusive builds or treat design selection as procurement.
- SRC-034 reports receipt of a picoScan150 Pro and Ethernet streaming. Attribute these statements to the document; accessory inventory, exact configuration, raw test evidence, and acceptance results remain open. Older unreceived/no-tests context is dated history.
- The user confirmed approximately 0.25–1 m/s planned survey speed on November 16 (D-019), consistent with SRC-034. The operating-range choice is settled; Q-17 concerns alignment of older FP2 1–2 m/s test wording. SRC-034 retains 5–8 m height and a $1,000 whole-design limit. Retain the separate under-$700 aircraft ceiling and reconcile costs/funding. The source's ~8.5-minute energy screen does not meet the unchanged ≥10-minute loaded-flight target.
- SRC-036, PaveWatch_Camera_and_LiDAR_Timing.docx, supplies the working timing plan: mode-dependent row times, Compact beam times, Pi software PTP/CLOCK_REALTIME with native boot/FC clock maps and validity segments. Verify timestamp event/clock semantics optically. Its 3 m/binned 10–15 fps/SSD settings and ≤3 ms P95, ±1 ms median, ≤1 ms/10 min drift are proposed bench configuration/goals; do not replace flight planning or SA2 ≤20 ms, infer installed PTP licenses, or claim tests passed.
- SRC-039–042 preserve picoscan150_hardware access records: existing Pi4/Bullseye/roughly32GB boot card, November16 Tailscale picoscan-pi at 100.72.89.22 and regular OpenSSH22. Keep prior Wi-Fi addresses and original-laptop aliases/profiles labeled historical/specific; no remote login, access provisioning, sensor/PTP pass or filesystem repair is implied by a documentation task. Per the user's follow-up (D-025), the current team instructions SRC-043/044 use the provided shared private key and Linux user antimony; do not require new per-member Linux accounts/key pairs. Tailscale accounts/invitations remain individual. Do not copy private backups, credentials or keys; preserve the user's decision to leave recorded filesystem errors unchanged.
- For DIY parts verify exact revisions, propulsion at the chosen voltage/prop, firmware target, port allocation, signal levels, connectors/pinouts, current limits, timing access, and installed clearances. Record documentation checks separately from physical tests.
- Use stable IDs in requirements, interfaces, decisions, and BOM rows. Each purchased or fabricated item must have one owning row; cross-reference kit contents instead of charging for them twice. Unknown numerical values stay blank with a reason/status.
- After a design change update the subsystem brief, decision log, affected interfaces, budgets, compatibility checks, and verification implications. Do useful independent work while questions remain open.
- Deliver concrete planning artifacts. Do not order, publish, contact others, or claim passed tests as a consequence of a research task alone.

## Azure workstation guides for subsystem leads

When helping a subsystem lead work from a laptop on the Azure GPU workstation,
read the relevant connection guide:

- **Data Processing & Change Detection (PC):** [Data processing lead instructions](data_processing_lead_instructions.md).
- **Reporting, Database & Alerts (RD):** [Findings presentation lead instructions](findings_presentation_lead_instructions.md).

These guides cover the dev_admin SSH login, saving and checking the current
server IP on the laptop, the correct remote working directory, and explicitly
reading the server's AGENTS.md before starting work. Follow the remote links to
detailed backup instructions when a backup or restore is requested.
