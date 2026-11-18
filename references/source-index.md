# Source index

Stable source IDs used throughout the workspace. Paths in the table refer to portable artifacts in this folder; original paths and SHA-256 hashes are in [the manifest](source-manifest.csv). Classification describes authority/use, not verified technical correctness.

| ID | Portable artifact | Use / limitation |
| --- | --- | --- |
| SRC-001 | [AGENTS.md](snapshot/project-context.txt) | context: October 22–23 context and user corrections; sensor status later updated by SRC-034 |
| SRC-002 | [final_docs/PaveWatch_DesignRequirementSpecifications_Final.docx](snapshot/final_docs/PaveWatch_DesignRequirementSpecifications_Final.docx) | requirements: Current final requirement source; contains FP4 stale test text |
| SRC-003 | [final_docs/msdr.pptx](extracted/final-msdr-slide-text.txt) | presentation: Final saved MSDR; 25 slides; hardware preference superseded by SRC-034 |
| SRC-004 | [MSDR/PaveWatch_MSDR_Notes.md](snapshot/MSDR/PaveWatch_MSDR_Notes.md) | planning: Editable 27-section MSDR notes; differs from final saved deck |
| SRC-005 | [MSDR/TEAM-ASSIGNMENTS.md](snapshot/MSDR/TEAM-ASSIGNMENTS.md) | planning: Technical handoffs and review responsibilities |
| SRC-006 | [Demonstration-Rubric-Draft/PaveWatch_Demonstration_Rubric.md](snapshot/Demonstration-Rubric-Draft/PaveWatch_Demonstration_Rubric.md) | demo-proposal: Proposed ground-demo rubric |
| SRC-007 | [Demonstration-Rubric-Draft/GROUND-DEMO-PLAN.md](snapshot/Demonstration-Rubric-Draft/GROUND-DEMO-PLAN.md) | demo-proposal: Ground-demo execution details and boundaries |
| SRC-008 | [hardware_planning/flight-platform-comparison.md](snapshot/hardware_planning/flight-platform-comparison.md) | prior-research: October 23 prior aircraft research; prices not refreshed |
| SRC-009 | [final_docs/Proposal_TeamCharter_PaveWatch.pdf](snapshot/final_docs/Proposal_TeamCharter_PaveWatch.pdf) | charter: Signed charter; subsystem ownership/support/governance |
| SRC-010 | [hardware_planning/rough_setup.txt](snapshot/hardware_planning/rough_setup.txt) | raw-concept: Original F450 candidate partial list; optimistic claims unvalidated |
| SRC-011 | [hardware_planning/compute.md](snapshot/hardware_planning/compute.md) | raw-concept: Raw recorder alternatives with inconsistent price summaries |
| SRC-012 | [hardware_planning/camera.md](snapshot/hardware_planning/camera.md) | raw-concept: Raw camera alternatives with unvalidated motion/blur claims |
| SRC-013 | [hardware_planning/post_processing_for_location.md](snapshot/hardware_planning/post_processing_for_location.md) | raw-concept: User location idea and unverified AI accuracy/variant claims |
| SRC-014 | [final_docs/PaveWatch_ProblemStatement.pdf](snapshot/final_docs/PaveWatch_ProblemStatement.pdf) | scope: Final problem statement |
| SRC-015 | [MSDR/PaveWatch_MSDR.pdf](snapshot/MSDR/PaveWatch_MSDR.pdf) | presentation: Rendered 27-slide MSDR working edition; not same as final deck |
| SRC-016 | [MSDR/TEAM-REVIEW.md](snapshot/MSDR/TEAM-REVIEW.md) | review-history: Historical MSDR audit and unresolved points; some since resolved |
| SRC-017 | [MSDR/PaveWatch_MSDR_Schedule.csv](snapshot/MSDR/PaveWatch_MSDR_Schedule.csv) | schedule-proposal: Saved planning task schedule |
| SRC-018 | [system-diagram/MSDR/PaveWatch_MSDR_Diagrams.pdf](snapshot/system-diagram/MSDR/PaveWatch_MSDR_Diagrams.pdf) | diagram-proposal: Existing design/option diagrams; not as-built wiring |
| SRC-019 | [system_diagram_infographic.png](snapshot/system_diagram_infographic.png) | diagram-proposal: User-supplied overall workflow illustration |
| SRC-020 | [sick-application/investigations/01-flight-platform-power-mechanical/findings.md](snapshot/sick-application/investigations/01-flight-platform-power-mechanical/findings.md) | historical-research: September flight/power research; older recommendations |
| SRC-021 | [sick-application/investigations/02-picoscan150-sensing-acquisition/findings.md](snapshot/sick-application/investigations/02-picoscan150-sensing-acquisition/findings.md) | historical-research: September sensor evidence, commissioning, interfaces |
| SRC-022 | [sick-application/investigations/03-rgb-positioning-synchronization/findings.md](snapshot/sick-application/investigations/03-rgb-positioning-synchronization/findings.md) | historical-research: September camera/pose/timing options; old envelope |
| SRC-023 | [sick-application/investigations/04-onboard-computing-storage-telemetry/findings.md](snapshot/sick-application/investigations/04-onboard-computing-storage-telemetry/findings.md) | historical-research: September recorder/storage/power research; Pi 5 direction |
| SRC-024 | [sick-application/investigations/05-mission-planning-ground-control/findings.md](snapshot/sick-application/investigations/05-mission-planning-ground-control/findings.md) | historical-research: September mission/GCS/communications research |
| SRC-025 | [sick-application/investigations/06-processing-sensor-fusion-change-detection/findings.md](snapshot/sick-application/investigations/06-processing-sensor-fusion-change-detection/findings.md) | historical-research: September processing options and data contracts |
| SRC-026 | [sick-application/investigations/07-datasets-pipeline-demonstration/findings.md](snapshot/sick-application/investigations/07-datasets-pipeline-demonstration/findings.md) | historical-research: September dataset/test/software leads; no measured results |
| SRC-027 | [sick-application/investigations/08-reporting-data-management-user-interface/findings.md](snapshot/sick-application/investigations/08-reporting-data-management-user-interface/findings.md) | historical-research: September reporting/local data design and schemas |
| SRC-028 | [sick-application/development-plan/02-hardware-and-acquisition.md](snapshot/sick-application/development-plan/02-hardware-and-acquisition.md) | historical-proposal: Older integrated hardware plan; no procurement evidence |
| SRC-029 | [sick-application/development-plan/03-processing-and-cloud.md](snapshot/sick-application/development-plan/03-processing-and-cloud.md) | historical-proposal: Older cloud integration proposal |
| SRC-030 | [sick-application/development-plan/01-project-and-architecture.md](snapshot/sick-application/development-plan/01-project-and-architecture.md) | historical-proposal: Older scope/architecture; historical comparison emphasis |
| SRC-031 | [sick-application/development-plan/04-verification-and-delivery.md](snapshot/sick-application/development-plan/04-verification-and-delivery.md) | historical-proposal: Older test proposals; not current acceptance criteria |
| SRC-032 | [sick-application/development-plan/05-budget-and-references.md](snapshot/sick-application/development-plan/05-budget-and-references.md) | historical-proposal: Older $999 estimate with excluded operating environment |
| SRC-033 | [sick-application/development-plan/README.md](snapshot/sick-application/development-plan/README.md) | historical-proposal: Older integrated choices; Purchased wording conflicts with current inventory |
| SRC-034 | [final_docs/PaveWatch_Approach_Final.docx](new-evidence/2026-11-16-final-approach/PaveWatch_Approach_Final.docx) | final-approach: Current design selections and reported Pro receipt/Ethernet activity; estimates and acceptance unverified |
| SRC-035 | [Final approach text](new-evidence/2026-11-16-final-approach/approach-text.txt) | extract: OOXML paragraphs/tables; figures and rendered layout remain in SRC-034 |
| SRC-036 | [Camera/LiDAR Timing DOCX](new-evidence/2026-11-16-camera-lidar-timing/PaveWatch_Camera_and_LiDAR_Timing.docx) | timing-design: Supplied November16 row/beam/PTP method, bench profile and proposed goals; installed behavior/results unverified |
| SRC-037 | [Camera/LiDAR Timing text](new-evidence/2026-11-16-camera-lidar-timing/timing-text.txt) | extract: Equations/line breaks/table text/hyperlink targets retained; rendered layout in SRC-036 |
| SRC-038 | [Timing Figure 1](new-evidence/2026-11-16-camera-lidar-timing/rolling-shutter.png) | embedded-image: Unmodified source illustration of row exposure windows/midpoints; not measurement evidence |
| SRC-039 | [Pi member connection guide](new-evidence/2026-11-16-raspberry-pi-access/FRIEND_ACCESS.md) | connection-record: Original member SSH account/key workflow; superseded by user instruction and SRC-043; endpoint/trust evidence retained |
| SRC-040 | [Pi administrator access record](new-evidence/2026-11-16-raspberry-pi-access/TAILSCALE.md) | connection-record: Recorded November16 installation/registration/SSH, sharing and original-laptop wired fallback; not retested |
| SRC-041 | [November12 Pi boot/SSH excerpts](new-evidence/2026-11-16-raspberry-pi-access/2026-11-12-raspberrypi-excerpts.txt) | connection-record-excerpt: Selected exact lines including Pi4/Bullseye, boot, fingerprint, SSH correction and unrepaired-filesystem decision |
| SRC-042 | [November11 laptop-to-sensor log](new-evidence/2026-11-16-raspberry-pi-access/2026-11-11_connection.md) | connection-record: Laptop Ethernet/HTTP success; not Pi capture or PTP evidence |
| SRC-043 | [Shared-key Pi member guide](new-evidence/2026-11-16-raspberry-pi-access/shared-key/FRIEND_ACCESS.md) | user-update: Earlier supplied-key/antimony instructions; username superseded by SRC-045; snapshot preserved |
| SRC-044 | [Shared-key Pi administrator guide](new-evidence/2026-11-16-raspberry-pi-access/shared-key/TAILSCALE.md) | user-update: Earlier shared-key admin revision; current pavewatch instructions in SRC-046 |
| SRC-045 | [Current pavewatch member guide](new-evidence/2026-11-16-raspberry-pi-access/pavewatch-login/FRIEND_ACCESS.md) | user-update: Supplied private key, pavewatch SSH login, home instructions and onboard LiDAR workspace/session paths |
| SRC-046 | [Current pavewatch administrator guide](new-evidence/2026-11-16-raspberry-pi-access/pavewatch-login/TAILSCALE.md) | user-update: Current login/workspace instructions; older successful-login observation retained as history |
| SRC-047 | [Sidewalk standards DOCX](new-evidence/2026-11-17-sidewalk-standards/Sidewalk_Standards_Federal_and_Mississippi_2026.docx) | supplied-reference: Federal, Mississippi and MDOT sidewalk measurements and scope |
| SRC-048 | [Sidewalk standards text](new-evidence/2026-11-17-sidewalk-standards/sidewalk-standards-text.txt) | extract: Body paragraphs, tables and hyperlink targets from SRC-047 |

For the engineering interpretation and source checks, see the [sidewalk measurement reference](new-evidence/2026-11-17-sidewalk-standards.md).

Readable extracts: [sidewalk standards](new-evidence/2026-11-17-sidewalk-standards/sidewalk-standards-text.txt), [camera/LiDAR timing](new-evidence/2026-11-16-camera-lidar-timing/timing-text.txt), [final approach](new-evidence/2026-11-16-final-approach/approach-text.txt), [final requirements](extracted/final-requirements.txt), [signed charter](extracted/signed-charter.txt), [problem statement](extracted/problem-statement.txt), [final saved MSDR](extracted/final-msdr-slide-text.txt), and [working MSDR](extracted/working-msdr-slide-text.txt).
