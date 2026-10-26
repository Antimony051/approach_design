# Procurement planning

[bom.csv](bom.csv) contains functional placeholders. No component has been selected for purchase by this workspace. The challenge sensor and owned 2S packs are inventory rows, not new purchase lines. Blank quantity/price cells are unknown; zero must mean an actually supplied/owned/no-charge item with evidence. The placeholder rows do not promise completeness: expand them for the chosen design's exact parts and accessories.

Use one active configuration ID for the buy list. Keep alternative configurations in dated research notes or separate BOM exports. A kit parent row should list its included parts; child rows for included items should not add cost a second time. Shared laptop, storage, regulator, or diagnostics hardware gets one cost owner. Split bundled placeholders into actual purchasable/fabricated lines.

Complete [compatibility.csv](compatibility.csv) with exact revisions and evidence. A historical paper check can seed a check but cannot become a physical pass. Use status values such as unresolved, documented, selected-pending-test, measured-pass, measured-fail, or not-applicable-with-reason.

[cost-summary.csv](cost-summary.csv) separates aircraft, payload, ground/demo, fabrication/spares, and recurring costs. For each scope count kit inclusions, supplied/owned items, shipping, tax, contingency, and unpriced lines. The aircraft must be **strictly under $700** including flight battery, RC, and navigation; recording payload is excluded. Keep telemetry and any needed charger/leads visible in the delivered aircraft plan. Resolve ownership of shared integration parts instead of moving costs to hide an overrun.

Historical component leads and costs are in SRC-008, latest MSDR SRC-003/SRC-004, compute/camera notes SRC-011/SRC-012, and older investigations/application plans. Prices were not refreshed during workspace creation. Do not reuse old stock/availability statements as current evidence.

Final purchasing package should include exact manufacturer SKU/revision/options, vendor/product URL, quantities/spares, kit inclusions, unit/extended and delivered costs, lead time/availability/check date, interface/fit evidence, and missing dependencies. Account separately for operational/site equipment and recurring correction/cloud services if selected. No orders are authorized by merely populating a research BOM.
