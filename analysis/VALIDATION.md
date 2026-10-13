# Validation evidence



## Data and SQL



- Verified all 212 official monthly Parquet footers (January 2009â€“August 2026); status, row count, size and schema retained in source_manifest.json.

- Downloaded only the twelve 2025 trip files. Every downloaded byte length and footer row count matches the manifest.

- Raw 2025 total: **48,722,602** records; compressed bytes: **829,973,299**.

- Operational trips: **48,157,684**; operational exclusions: **564,918**.

- Monthly, weekday/hour, weekday, hour, zone, borough, zone/month, airport, distance-band, payment, fare/hour and rate-code population totals reconcile to the same annual activity total.

- Local MariaDB query 09_annual_reconciliation returned **all_match=1**; annual, monthly, weekday/hour and zone totals all equal 48,157,684.

- Exact pooled median/p90 duration checks satisfy p90 >= median. Fare sample counts are no larger than activity populations.

- Data reconciliation evidence is retained in validation.json and hourly_validation.json; Tableau artifact checks are recorded separately in tableau_validation.json.

- Overlapping quality flags remain separate. No duplicate removal or hidden zero-distance exclusion is performed.

- 120-, 180- and 240-minute threshold sensitivity results are retained.



## Native Tableau verification



The installed Tableau Desktop 2026.2.3 opened the native workbook, populated its charts, and saved the packaged workbook. The original nine dashboard designs and new executive/explorer/cleaning pages were inspected on screen. Final hourly KPI values match the executed SQL: 48,157,684 annual trips, 131,939 average daily trips (rounded), busiest hour 18 and peak-hour share 7.1% (rounded). Fare medians are $14.49 and $22.13; eligible fare means are $20.15 and $28.95. The historical timeline is a continuous 2009-2026 date axis and 2026 is marked partial.



The native map plots weighted spatial points inside official zones, focuses automatically on NYC and excludes Newark/unknown coordinates. The final mapped snapshot has 259 distinct NYC zone IDs. The weighted density uses Tableau's native Orange-Gold palette on its dark basemap; other visuals use the requested palette. The weekday/hour heatmap has 168 color cells with values available on hover, avoiding a dense numeric table. Weekday ordering is Monday-Sunday.



The workbook contains eleven dashboards and 50 editable worksheets. Fixed dashboard canvases are 1360 × 740, and dashboard tiles are checked against their canvas bounds. CSV snapshots are embedded; this is a portable snapshot with no configured live SQL refresh. `tableau_validation.json` records structural, reconciliation and archive checks. Native inspection does not claim every possible selection was tested. Tableau basemap tiles require internet access.



The analysis PDF has ten pages. Its changed Tableau-related pages were rendered and visually inspected, along with the previously checked report layout.



## Reproduction boundary



Cached DuckDB result reuse assumes unchanged raw source files. If the source snapshot is updated, rebuild in a new work directory. Stored source sizes/row counts provide provenance but are not cryptographic content hashes. Full-table exact quantiles are computed directly, not reconstructed from monthly summaries.



## Extension verification

All 36 final structural, archive and data checks passed. The disjoint funnel reconciles published 48,722,602 -> operational 48,157,684 -> fare-eligible 44,727,165. Each endpoint total is 48,157,684. The interactive calendar has 95,630 unique date-zone rows (365 dates x 262 pickup IDs). Nineteen MariaDB query results are saved.

Tableau Desktop tests covered all-data defaults, Manhattan, January Manhattan, and January Midtown Center. All five displayed KPI values match independently calculated sums and weighted means, with chart selections updating consistently. Exact observations are in interactive_filter_validation.json. Every possible combination was not tested. Native NYC map, signed zone balance, airport sample labels, executive insights and cleaning funnel were inspected. The 10-page final PDF was rendered and visually reviewed.

Payment 0 is Flex Fare. No causal conclusion is drawn from negative monetary values or the positive-counterpart existence check. See QUALITY_INVESTIGATION.md.


The restructured 10-page report has five figures generated from retained SQL summaries, evidence paths beside findings, and a reproducibility appendix. Proposed pilots and untested recommendations were removed. Ten report-specific reconciliation assertions passed; final pages were rendered and visually reviewed. See report_evidence_validation.json for input hashes and checks.
