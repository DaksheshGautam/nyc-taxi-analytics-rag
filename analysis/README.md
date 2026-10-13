# NYC Yellow Taxi Operations



A SQL and Tableau portfolio project covering historical published taxi activity (2009â€“August 2026) and detailed Januaryâ€“December 2025 operations.



## Start here



- `NYC Taxi Operations.twbx`: portable Tableau workbook with packaged CSV snapshots. Open in installed Tableau Desktop and use Presentation Mode for the full canvas.

- `tableau/NYC Taxi Operations.twb`: editable native workbook source; keep its `Data/` folder beside it.

- `Analysis_Report.pdf`: updated computed business analysis.

- `Analysis_Report.md`: editable text version.

- `data/`: compact calculation tables with explicit grains and sample sizes.

- `sql/`: PostgreSQL trip-level and derived queries; `sql/postgresql/`: PostgreSQL schema and result-table business queries.

- `postgresql_results/`: results verified on the Neon PostgreSQL server after import.

- `calculation_ledger.json`: original computation provenance; PostgreSQL has separate migration/import/execution ledgers.

- `source_manifest.json`: all 212 verified source file footers, URLs, schemas and sizes.

- `validation.json`, `tableau_validation.json` and `VALIDATION.md`: reconciliation and verification evidence.

- `DATA_DICTIONARY.md`: fields, populations and aggregation rules.

- `Zone_Pickup_Map.svg`: official-boundary vector map of full-year 2025 pickups; zone tooltips show counts when opened in a browser. This is a supplemental boundary snapshot alongside the native Tableau density map.



## Data strategy



Earlier years need only monthly record counts from verified Parquet metadata. Their trip files are not downloaded. Twelve 2025 files (48,722,602 records; 829,973,299 compressed bytes) are retained outside the deliverable package under `../work/raw/`.



Historical counts are source-file records before cleaning. Operational 2025 counts require a source-month-matched pickup, an observed drop-off and duration greater than zero and at most 180 minutes. These definitions must not be mixed. 2026 contains Januaryâ€“August only. Comparable historical growth uses those same eight months in every year.



Exact pooled quantiles are computed with DuckDB SQL. Group medians and p90s are displayed at their saved grain using MIN; annual cards use separately computed pooled statistics. Fare means use eligible fare sums divided by eligible counts. Hourly daily averages divide by all calendar days: 365 overall, 261 weekdays and 104 weekend days. Heatmap cells use 52 occurrences of each weekday except Wednesday (53).



The workbook contains eleven dashboards and 50 editable worksheets. Historical counts, 2025 operations, hourly activity, fares, airports, routes and quality remain separate sources. CSV snapshots are included; Tableau Refresh reads those snapshots and does not download TLC files or rerun the SQL. The map uses spatial points inside the largest part of each official zone, weighted by completed pickups. It does not depict individual GPS locations. Only the five NYC boroughs are plotted; Newark and unknown zones remain in overall totals. The density map uses Tableau's native Orange-Gold scale; the remaining dashboard colors use the requested hex palette. Hover over heatmap cells for exact values.



## Rebuild



Install Python dependencies from `requirements.txt` in your preferred local environment. Then run, in order:



```

python analyze.py

python analyze_hourly.py

python load_postgresql.py  # requires private NEON_ADMIN_URL

python build_tableau.py

python write_report.py

python create_zone_map.py

```



For raw files, use the official 2025 URLs recorded in `source_manifest.json`, save them as `../work/raw/2025-MM.parquet`, and verify file bytes and footer row counts. The project download/preflight scripts are in `reproduction/`; they download only 2025 trip files. They require `psutil` for capacity inspection.



The analysis stage is kept in `../work/analysis.duckdb`; 1.5 GB working memory and two SQL threads keep processing bounded. The stage is reused after checking its total row count. If source files change, build into a new work directory or remove only your project-owned stage deliberately before rebuilding; cached result reuse assumes unchanged source files.



## Neon PostgreSQL database

The active cloud database is `nyc_taxi` in the separate `nyc-taxi-evidence` Neon project, PostgreSQL 18. Typed original results live in `results`, detailed aggregates in `detail`, and the report/search corpus in `evidence`. Streamlit uses a dedicated read-only connection. Aiven and ecommerce services are not used.

See `POSTGRESQL_MIGRATION.md` for scope, schema, import, verified execution and the distinction between original local calculations and converted PostgreSQL queries. Original DuckDB/MariaDB artifacts are preserved under `../work/` for audit. The PDF records the evidence available when it was written; migration does not retroactively change the original computation engine.

Full raw trips stay local. The five additional detail tables contain 2,254,686 date/hour/zone/route/payment groups with reconciliation checks and correct eligible denominators. Do not infer unavailable dimension intersections or average stored percentiles. See `DETAILED_DATA_GUIDE.md`.


## Source references



- [NYC TLC trip records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

- [Yellow trip dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf)

- [Historical user guide](https://www.nyc.gov/assets/tlc/downloads/pdf/trip_record_user_guide.pdf)

- [Zone lookup](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv)

- [Zone boundaries](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip)

- [Tableau density maps](https://help.tableau.com/current/pro/desktop/en-us/maps_howto_heatmap.htm)



## Interpretation and sharing



This is a fixed, portable source snapshot. The evidence app is published at https://nyc-taxi-evidence.streamlit.app/ and uses a read-only Neon PostgreSQL connection. No scheduled dataset refresh is configured. Public trips describe completed activity; they do not measure unmet demand, utilization, idle time, operating profit or driver shift earnings. Charges are nominal USD and exclude cash tips.



The deliverable package is ready for later GitHub review/upload. Raw records, database files, local application caches and secrets are excluded. The ZIP package should not be committed alongside its unpacked contents. The revised report PDF is published on main at DaksheshGautam/DaksheshGautam.github.io/public/projects/nyc-taxi-analysis.pdf. The complete project source, SQL, report and Tableau workbook are published at https://github.com/DaksheshGautam/nyc-taxi-analytics-rag.



The Interactive explorer filters pickup date, borough and taxi zone across its seven views. Daily averages include all selected dates; monetary means use eligible sums/counts. Annual reference dashboards remain fixed to 2025. Payment code 0 is Flex Fare under the March 2025 TLC dictionary. See QUALITY_INVESTIGATION.md for disjoint cleaning rules, negative-money investigation and JFK within-zone caveat. Extension SQL/results are saved; nineteen business/reconciliation queries have been executed locally.


The final report has 10 ordered sections/pages, five figures regenerated from retained SQL outputs, evidence references beside findings and a reproducibility appendix. Causal explanations, forecasts, benefit estimates and proposed pilots are excluded. Report checks and input hashes are retained in report_evidence_validation.json.


## Local RAG evidence assistant

The `nyc-taxi-rag` folder includes a local/Streamlit evidence search and Groq adapter. It indexes the analysis PDF, selected SQL result tables, and generated metric, FAQ and evidence-boundary documents. Run `python nyc-taxi-rag/server.py` and open http://127.0.0.1:8765. Offline verification passed 18 tests. Live LLM verification is pending the new Groq Cloud key. See `nyc-taxi-rag/README.md` for setup and grounding limits. A separate portable archive is `NYC_Taxi_RAG_Assistant.zip`.


## Published cloud evidence

Neon stores five detailed tables containing 2,254,686 groups, plus typed original results and verified report evidence. Table and index storage is 416,833,536 bytes. See `neon_database_validation.json`, `postgresql_execution_validation.json` and `detailed_query_validation.json`. All nineteen result queries reconcile to retained originals, with documented tolerance for original four-decimal division outputs. Raw records remain local; converted raw-trip queries were semantically planned, not reexecuted in Neon.

The Streamlit explorer supports available filtered dimensions and attaches selected query results to the next question. It does not execute unrestricted natural-language SQL. Groq live testing is pending the new API key. Credentials remain private. `load_detailed_postgresql.py` imports detailed aggregates after `load_postgresql.py`; the separately packaged `NYC_Taxi_PostgreSQL_Data.zip` contains the compressed data.
