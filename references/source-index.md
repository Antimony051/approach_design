# Source index

Stable source IDs used throughout the workspace. Paths in the table refer to portable artifacts in this folder; original paths and SHA-256 hashes are in [the manifest](source-manifest.csv). Classification describes authority/use, not verified technical correctness.

| ID | Portable artifact | Use / limitation |
| --- | --- | --- |
| SRC-001 | [AGENTS.md](snapshot/project-context.txt) | context: Latest project context and user corrections |
| SRC-002 | [final_docs/PaveWatch_DesignRequirementSpecifications_Final.docx](snapshot/final_docs/PaveWatch_DesignRequirementSpecifications_Final.docx) | requirements: Current final requirement source; contains FP4 stale test text |
| SRC-003 | [final_docs/msdr.pptx](extracted/final-msdr-slide-text.txt) | presentation: Final saved presentation; 25 slides; latest planning labels |
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

Readable extracts: [final requirements](extracted/final-requirements.txt), [signed charter](extracted/signed-charter.txt), [problem statement](extracted/problem-statement.txt), [final saved MSDR](extracted/final-msdr-slide-text.txt), and [working MSDR](extracted/working-msdr-slide-text.txt).
