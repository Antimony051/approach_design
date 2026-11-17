# Later evidence and source updates

Add dated manufacturer manuals/datasheets, exact supplier quotes, connector drawings, CAD, experiment records, and concise source notes as design work proceeds. Link them from the relevant research note, BOM, interface, or decision. Preserve URL, checked date, document/revision/section, exact hardware variant, and whether a claim is published, calculated, assumed, or measured. Do not save credentials or private access tokens.

- [October 28 ground-control documentation check](2026-10-28-ground-control.md): GCS planning, optical-flow setup, shared RC/MAVLink links, and mission transfer semantics. Published documentation only; no project hardware compatibility or test claims.
- [October 29 supervised mission documentation](2026-10-29-supervised-missions.md): mission resumption, mode-specific proximity protection, stabilization versus position holding, and Brake limitations. Published documentation only; no selected fallback or passed test.
- [November 3 RGB/depth fusion assessment](2026-11-03-rgb-depth-fusion.md): manufacturer scan geometry, RGB-D segmentation/depth-completion precedents, paired pavement data, and continued 3D processing. Documentation/papers and labeled sampling calculations; no training or project measurements.

- [November 16 final approach alignment](2026-11-16-final-approach.md): supplied project DOCX (SRC-034) and readable text (SRC-035), adopted design choices, reported sensor activity, estimates, and conflicts; no new web research or executed tests.

- [November 16 camera/LiDAR timing incorporation](2026-11-16-camera-lidar-timing.md): supplied DOCX/extract/figure (SRC-036–038), per-row/per-beam timing, Pi software PTP/clock mapping, bench profile, and proposed 3 ms goals; external links preserved without new verification; no executed tests.

- [November16 Raspberry Pi access consolidation](2026-11-16-raspberry-pi-access.md): member/admin Tailscale/OpenSSH records, focused Pi boot/SSH excerpts and laptop-to-LiDAR log (SRC-039–042); existing Pi inventory, historical addresses and maintenance/acquisition boundaries; no new login or configuration.

The Pi access entry also preserves SRC-043/044: updated member/admin instructions using the user-provided private key and shared antimony login (D-025). Earlier per-member Linux-account/key instructions remain historical snapshots.

Latest Pi access update: D-026 / SRC-045–046 use **pavewatch** with the supplied key and document the Pi home README.md/AGENTS.md, /home/pavewatch/03-sensor-payload-acquisition (tools/docs), and ~/data/sessions recordings. Earlier usernames remain historical.
