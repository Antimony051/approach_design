# MSDR rough draft — team review

The review is **October 23, 2026, 11:00–11:55 a.m. Central**. Post the reviewed
presentation to the project website by **10:00 a.m. Central**. The October 20
Canvas snapshots list **11:59 p.m. Central** for both MSDR submission entries.
Confirm that the scheduled slot is recorded in Signup Genius. All members should
attend and bring a feedback notebook.

## Draft files

- `PaveWatch_MSDR_Rough_Draft.pptx`: 28 editable slides, editable diagram and Gantt
  charts, and embedded speaker notes.
- `PaveWatch_MSDR_Rough_Draft.pdf`: rendered reading copy.
- `PaveWatch_MSDR_Rough_Draft_Notes.md`: slide text, full speaker notes, source
  links, and exact task dates.
- `PaveWatch_MSDR_Schedule.csv`: editable dated task list for both semesters.
- `build_draft.py`: content and layout source. Regenerating overwrites the PPTX,
  Markdown notes, and CSV; preserve manual PowerPoint edits before rebuilding.

## Confirmed during drafting

- Selected for the SICK$10K Challenge; picoScan is on its way.
- No project hardware ordered.
- Two existing **2S**, 5,200 mAh, 50C, 7.4 V, 38.48 Wh batteries and chargers.
  The initial 6S description was corrected by the user. Connector and charger
  compatibility with a new flight pack are still unconfirmed.
- Team roles unchanged; presentation slot confirmed by the user.

## Input that would finish the draft

1. **Six real member photos.** The team slide has explicit placeholders; the
   lecture rubric grades photographs. Existing website avatar SVGs are not
   treated as photographs.
2. **Exact part numbers and supplier quotes.** The F450 / 2212 / ESC / propeller
   bundle is not a uniquely specified product. `parts_to_buy.txt` remains
   unchanged and is cited as the user's candidate design. The custom build is
   the draft's provisional selection for engineering review, not a proven
   aircraft or an approved order.
3. **Firmware, ports, and correction access.** The SpeedyBee option uses an
   ArduCopter board target; the older Pixhawk/PX4 assumption is conditional on a
   kit alternative. Confirm GNSS, RC, companion and telemetry connections, an
   external compass as required, and the RTK base/NTRIP correction source.
4. **Any existing test evidence.** No measured results were supplied. Add logs,
   plots, dates, test conditions, and observed failures if available. Proposed
   tests are not shown as completed.
5. **Acceptance and semester scope.** Resolve the requirements issues below;
   confirm which physical tests can actually be delivered on November 30.

## Requirements issues carried forward explicitly

The authoritative project source for this draft is
`final_docs/PaveWatch_DesignRequirementSpecifications_Final.docx`, including the
October 19 edits. Despite its extension, this is an OpenDocument archive. The
draft extracted body content and excluded document comments. The older Markdown
requirements source omits some later edits and was not used to override them.

| Issue | Source text / consequence | Treatment in the MSDR draft |
| --- | --- | --- |
| FP3 takeover | Updated to ≤1 s, 10/10 trials | Uses the updated limit, rather than the older ≤2 s draft |
| FP4 attitude | Requirement says ≤5° for ≥90%; test procedure says ≤1° for ≥90% | Explicit team decision; no silent resolution |
| PC1 versus S3 | PC1 permits 1 m X/Y and 0.2 m Z errors for ≥90%; S3 requires joint ≤0.5 m centroid and ≤60 mm height errors for ≥90% of detected targets | Present PC1 as a subsystem frame check; evaluate S3 separately |
| GC3 buffering | Edited to buffer up to 60 s, then transmit backlog before current data | Clarify which stream, rates, buffer capacity, ordering, and endpoint; no assumption of full sensor streaming over a low-rate telemetry link |
| PC3 export | Edited to export ≥1 GB onboard survey package to laptop within 30 min | Retains three timed exports and integrity checks |
| Gradients | Rise/run reporting required, but no numerical error acceptance bound | Report measured errors; agree a bound before claiming gradient accuracy |
| Prior survey | Current assessment does not require historical data | Historical comparison remains optional future/contextual input |

## Parts-list review

The user's five estimates sum to **$405**. Added September planning allowances
for the recorder, camera, storage, cooling, payload supply, mount, cables, spares,
and targets total **$285**, for a preliminary **$690**. Adding the older $55
reserve makes **$745**. These figures are planning arithmetic, not complete
quotes. They omit unresolved telemetry hardware, RTK correction access,
additional sensor accessories, and shipping/fees. Avoid duplicate ESC purchases
if both the propulsion combo and flight-controller stack include ESCs.

The archived ordering policy allocates $700 for Capstone I and $300 for Capstone
II and has a Wednesday-noon cutoff for Friday orders. Verify current policy and
remaining funds. It does not establish a new discretionary $1,000 Fall budget.

The existing packs are **2S**. One pack's nominal 7.4 V differs from the proposed
SpeedyBee input (documented 3S–6S) and picoScan's source-manual 9–30 V requirement.
Changing to XT60 does not resolve voltage compatibility. Select the flight pack
from exact motor/prop/ESC data and design the payload rails separately. This
draft does not propose combining or modifying battery packs.

The RTK rover needs compatible corrections and validated fix quality. It does
not establish centimeter-level surface accuracy, attitude accuracy, payload
capacity, or ten-minute endurance. Those claims in the informal parts list
remain unvalidated. Holybro's documentation identifies the Rover Lite as a
rover-only model.

## Schedule and evidence limitations

- Fall tasks are a proposed plan beginning October 22, rather than claims of
  completed work. Hardware tasks depend on actual arrival and procurement.
- January–April 2027 task dates are planning assumptions pending the official
  Capstone II calendar.
- The two Capstone I deliverable slides include all six owners. Sensors,
  diagnostics, and processing are the main technical workstreams; control and
  reporting provide supporting deliverables.
- Simulated or replayed inputs demonstrate their stated software behavior.
  Real range/timing, loaded endurance, route tracking, and airborne accuracy
  require physical measurements. Agree any changed demo scope with instructors.
- The large SICK manual could not be re-fetched during drafting; its electrical
  and interface values are carried from the existing requirements/development
  plan. Verify against the received sensor's label/manual.

## Rubric coverage

| Lecture requirement | Slides |
| --- | --- |
| Team name, introduction, pictures/names/roles | 1–2; photographs still missing |
| Problem significance and citations | 3–4 |
| Segmented, labeled system diagram | 6 |
| Features / constraints / requirements / standards | 5, 7–10 |
| Three components; metrics, ≥3 options, comparison and choice | 11–13 |
| Color-coded Gantt, tasks, subsystems, start times, both semesters | 17–18 plus CSV |
| At most two slides of Capstone I deliverables and tests | 19–20 |
| Future work and broader impact | 23 |
| Submission and scheduling logistics | 24 |
| References and provenance | 25–28; per-slide sources and notes |

AI acknowledgement is included in slide 24's speaker notes: OpenAI
ChatGPT/Codex assisted with assembly, source checks, drafting, comparisons,
scheduling, notes, and layout. The team retains responsibility for technical
review and course acknowledgement requirements.

No website publication, Canvas submission, scheduling edit, parts order, or
message to another person was performed.
