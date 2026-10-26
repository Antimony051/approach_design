# Application attachment working sources

These numbered Markdown sections form one PaveWatch Technical Development and Validation Plan. They are maintained separately for review and assembled in numerical order for submission. This README is editorial material and is not part of the attachment.

The polished application-facing edition is now [PaveWatch Application Attachment](../application/PaveWatch_Application_Attachment.pdf), with editable [HTML source](../application/PaveWatch_Application_Attachment.html). Use that PDF for submission; these sections remain the more detailed working engineering record.

## Assembly order

1. `01-project-and-architecture.md`
2. `02-hardware-and-acquisition.md`
3. `03-processing-and-cloud.md`
4. `04-verification-and-delivery.md`
5. `05-budget-and-references.md`

## Integration decisions

- Purchased X500 v2 development kit; printed parts used for payload integration.
- Cloud processing after landing, with onboard recording and repeatable local replay.
- Camera Module 3 baseline; global-shutter upgrade requires a revised purchase budget and validation. This reconciles investigation 01 with investigations 03–04 rather than treating their camera configurations as interchangeable.
- PX4 and QGroundControl; Raspberry Pi 5 2 GB; 256 GB USB SSD.
- Conservative initial survey envelope: 5–8 m above pavement, 1–2 m/s, 15 Hz / 0.33° subject to delivered sensor configuration and site testing.
- Initial acquisition budget is an estimate, not a quote. It excludes operating infrastructure and assumes the challenge sensor accessories cover its system plug and interface cables. Final quotes must fit the allocation before purchase.
- Equipment-loan arrangements and student cloud-credit mechanisms are intentionally omitted from attachment text at the team's request.

## Release checks

Confirm final delivered sensor configuration, actual component quotes and shipping, cloud provider and operating allowance, project calendar, and team workstream assignments. Render diagrams and paginate the assembled document before submission. All experiments described here are planned; no hardware or experimental results are claimed.

The eight investigations are the detailed research record. These sections supersede the earlier `drafts/` package for this attachment but do not alter those research files.
