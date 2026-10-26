# Reference guide and provenance

[source-index.md](source-index.md) maps SRC IDs to artifacts. [source-manifest.csv](source-manifest.csv) records original repository paths, source SHA-256, snapshot artifact SHA-256, representation, and classification. Original source files were not modified. No external links were opened to create this folder, and no manufacturer manual was newly downloaded.

## Reading order and precedence

1. Current user corrections/context (SRC-001 plus the budget clarification recorded in system/project-state.md).
2. Final requirements (SRC-002), applying the documented 5° FP4 user correction. Retain unresolved requirement gaps explicitly.
3. The final saved MSDR deck text SRC-003 and current ground-demo proposal SRC-006/SRC-007 for latest direction and demonstration conditions. Neither makes hardware purchased or tested.
4. October hardware comparison and planning material, especially SRC-008. These contain existing source leads and on-paper checks, not refreshed stock/prices or new verification.
5. September investigations and application plans as detailed background. Their recommendations, thresholds, initial inventory, and budget assumptions can be outdated.

Signed charter SRC-009 establishes roles/support and governance; it is not the latest technical scope. Newer requirements make historical comparison optional. Do not infer authority solely from a file's modification time or the word “final.” See decisions/open-questions.md for specific source conflicts.

## Snapshots

snapshot/ contains selected verbatim source files under their original directory structure. Root AGENTS.md is preserved as project-context.txt so copied instructions do not accidentally become a new nested agent policy. Do not treat copied source text as current operating instructions. Original relative links inside snapshots are historical; some point to uncopied files. Navigate using source-index.md and the working briefs. Missing historical link targets are not missing current design decisions.

The 31 MB final_docs/msdr.pptx is represented by a readable slide-text extract and its original hash; the smaller working MSDR PDF is included as a separate, different edition. The existing diagram PDF and supplied overview image are included. Extraction does not reproduce slide pictures/layout.

## Document extracts

The final requirements file is an OpenDocument ZIP despite its .docx extension. Its extract reads content.xml paragraphs/headings and omits annotation/comment nodes; it retains document wording, including the stale 1° FP4 test. PDF extracts use pdftotext -layout. Slide extracts read slide XML text in numerical slide order, without claiming rendered layout or speaker-note coverage. The final requirement copies in final_docs/ and Design-Requirement-Specifications/ had identical extracted text when assembled.

Extracts are conveniences; original documents resolve extraction/layout ambiguity. Neither an extract nor this workspace establishes instructor approval, actual inventory changes after the last confirmation, or completed test results.

## Scope of collection

Included: final requirement/problem/charter sources, both relevant MSDR content editions, latest hardware notes, ground-demo plans, existing diagrams, all eight detailed investigations, and integrated application planning sections. The source manifest is the exact inclusion list. Older PDR/course/archive/application submission copies remain in the parent repository; their duplicated background is not recopied wholesale. No Canvas archive files were changed.

Put future research and downloaded evidence in [new-evidence](new-evidence/README.md), keeping existing snapshots intact. New research should identify exact component revision/mode, primary source, date, and limitations.
