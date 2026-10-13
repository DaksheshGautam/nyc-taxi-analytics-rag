# NYC Yellow Taxi Operations: agreed scope



Two historical pages use monthly source-file record counts for January 2009 through August 2026. Counts were computed from all 212 verified Parquet footers, without downloading the historical trip archive. These represent published records before cleaning, not timestamp-filtered operational trips. The historical pages avoid fare comparisons, route statistics and claims about fleet utilization.



Four operational pages use January–December 2025 records only. All twelve raw monthly files are retained locally under work/raw, excluded from Git and deliverable packages. The full 2025 file total is 48,722,602 records and 829,973,299 compressed bytes. Detailed data is processed with memory-bounded SQL; compact result tables power the report.



2026 is partial (January–August). Annual totals are explicitly labeled, and comparable trends use January–August for every year. No annualization is used.



SQL, calculation tables, provenance, quality checks, editable Tableau workbook, and a computed analysis report are the deliverables. The active cloud project uses Neon PostgreSQL 18 with isolated results, detail and evidence schemas. Original raw calculations were executed locally in DuckDB; historical MariaDB artifacts are archived for audit.



GitHub upload is a later step after the user has reviewed the completed artifacts. No cloud database, paid service, forecasting model, or LLM app is included.



The Interactive explorer filters pickup date, borough and taxi zone across its seven views. Daily averages include all selected dates; monetary means use eligible sums/counts. Annual reference dashboards remain fixed to 2025. Payment code 0 is Flex Fare under the March 2025 TLC dictionary. See QUALITY_INVESTIGATION.md for disjoint cleaning rules, negative-money investigation and JFK within-zone caveat. Extension SQL/results are saved; nineteen business/reconciliation queries have been executed locally.
