# Reference guide and provenance

[source-index.md](source-index.md) maps SRC IDs to artifacts. [source-manifest.csv](source-manifest.csv) records original repository paths, source SHA-256, snapshot artifact SHA-256, representation, and classification. Source documents and initial evidence are preserved. The Pi member/admin instructions were later amended at the user's explicit request; SRC-039/040 preserve their earlier text SRC-043/044 preserve the earlier shared-key revisions, and SRC-045/046 preserve the current pavewatch login and onboard workspace instructions. SRC-034/035 (final approach) and SRC-036–038 (supplied camera/LiDAR timing DOCX, extract and figure) were added November 16, 2026 under new-evidence; the initial snapshot/extracted directories remain unchanged. No external links were opened to create this folder, and no manufacturer manual was newly downloaded.

## Reading order and precedence

1. Current user instructions/corrections, including the November 16 request to align with the final approach. Retain the user-confirmed FP4 correction and separate under-$700 aircraft ceiling; dated October sensor status is historical.
2. Final requirements (SRC-002), applying the documented 5° FP4 user correction. Retain unresolved requirement gaps explicitly.
3. Final approach SRC-034 (readable text SRC-035) for current implementation, source-reported sensor receipt/streaming, $1000 design limit and estimates. See the [reconciliation](new-evidence/2026-11-16-final-approach.md) for speed/endurance/schema conflicts. SRC-036 refines the timing plan and introduces a distinct first bench profile plus tighter proposed development goals; see [timing provenance](new-evidence/2026-11-16-camera-lidar-timing.md). No acceptance criteria are silently amended.
4. Ground-demo proposal SRC-006/SRC-007 for proposed demonstration conditions, and SRC-003 MSDR for prior choices. Neither proves completed tests.
5. October hardware comparison and planning material, especially SRC-008. These contain existing source leads and on-paper checks, not refreshed stock/prices or new verification.
6. September investigations and application plans as detailed background. Their recommendations, thresholds, initial inventory, and budget assumptions can be outdated.

Signed charter SRC-009 establishes roles/support and governance; it is not the latest technical scope. Newer requirements make historical comparison optional. Do not infer authority solely from a file's modification time or the word “final.” See decisions/open-questions.md for specific source conflicts.

## Snapshots

snapshot/ contains selected verbatim source files under their original directory structure. Root AGENTS.md is preserved as project-context.txt so copied instructions do not accidentally become a new nested agent policy. Do not treat copied source text as current operating instructions. Original relative links inside snapshots are historical; some point to uncopied files. Navigate using source-index.md and the working briefs. Missing historical link targets are not missing current design decisions.

The 31 MB final_docs/msdr.pptx is represented by a readable slide-text extract and its original hash; the smaller working MSDR PDF is included as a separate, different edition. The existing diagram PDF and supplied overview image are included. Extraction does not reproduce slide pictures/layout.

## Document extracts

SRC-034 is an OOXML DOCX. SRC-035 extracts body paragraphs and table cells in order with table markers; it does not render figures, pagination, or layout. The exact original is retained beside the extract under new-evidence. URLs cited inside it were not reopened for the November 16 alignment.

The final requirements file is an OpenDocument ZIP despite its .docx extension. Its extract reads content.xml paragraphs/headings and omits annotation/comment nodes; it retains document wording, including the stale 1° FP4 test. PDF extracts use pdftotext -layout. Slide extracts read slide XML text in numerical slide order, without claiming rendered layout or speaker-note coverage. The final requirement copies in final_docs/ and Design-Requirement-Specifications/ had identical extracted text when assembled.

Extracts are conveniences; original documents resolve extraction/layout ambiguity. Neither an extract nor this workspace establishes instructor approval, actual inventory changes after the last confirmation, or completed test results.

SRC-037 preserves OOXML math with explicit fraction parentheses/subscripts, line breaks, table markers and hyperlink targets. SRC-038 is the unmodified embedded Figure 1. Neither is a measurement. The supplied timing note's external URLs were retained without a new documentation check.

## Raspberry Pi connection records

SRC-039–042 preserve November12/16 Pi access notes and a November11 laptop-to-LiDAR log, incorporated at the user's request on November16. SRC-043/044 record the user-directed provided-private-key workflow, superseding per-member Linux account/key creation in SRC-039/040. The latest D-026/SRC-045/046 changes the shared username to pavewatch and adds the user-provided Pi workspace/home instructions; older username snapshots remain historical. [The source note](new-evidence/2026-11-16-raspberry-pi-access.md) maps originals/copies/focused exact excerpts and distinguishes observed administrator SSH from unverified member access, Pi acquisition and timing. Newer Tailscale records take precedence over stale DHCP-address wording in older setup notes. Current login instructions are in [integration](../integration/raspberry-pi-access.md). No private backups, credentials or keys are included.

## Scope of collection

Included: final approach (added November 16), final requirement/problem/charter sources, both relevant MSDR content editions, latest hardware notes, ground-demo plans, existing diagrams, all eight detailed investigations, and integrated application planning sections. The source manifest is the exact inclusion list. Older PDR/course/archive/application submission copies remain in the parent repository; their duplicated background is not recopied wholesale. No Canvas archive files were changed.

Put future research and downloaded evidence in [new-evidence](new-evidence/README.md), keeping existing snapshots intact. New research should identify exact component revision/mode, primary source, date, and limitations.
