# PostgreSQL and Neon migration

The cloud project is `nyc-taxi-evidence`, PostgreSQL 18, database `nyc_taxi`. It is separate from all Aiven/ecommerce services.

Active query files in `sql/` now use PostgreSQL syntax. `sql/postgresql/01_schema.sql` defines the retained typed result tables and evidence storage; the other files in that folder are business and reconciliation queries. Median and p90 calculations use `percentile_cont` ordered-set aggregates. Integer divisions explicitly cast to floating point. Source CSV readers are replaced with typed `results` tables. Raw input staging uses a `raw_trip_source` table because PostgreSQL does not read local Parquet files directly.

The original calculations were executed in DuckDB and MariaDB. Those historical scripts and outputs are retained under `../work/legacy-sql` and `../work/legacy-mysql-artifacts` for audit; conversion does not retroactively change their execution engine. New PostgreSQL executions have their own results and validation ledger. Parser validation alone is not execution verification.

`load_postgresql.py` imports the original result CSVs and RAG sources into the new cloud project. It refuses to replace a populated evidence snapshot. Supply the owner connection privately through `NEON_ADMIN_URL`. No credentials belong in GitHub or downloadable archives. Streamlit uses a separate SELECT-only role and a pooled connection with certificate/hostname verification.

Full trip records remain local in `../work/analysis.duckdb`. The cloud retains derived tables, not 48 million individual trip rows. Detailed aggregate tables preserve sums and eligible denominators so combined means can be computed as `SUM(fare_sum_usd)/SUM(fare_n)`. Never average stored medians, p90 values, ratios or per-group means to obtain a larger population's metric.

Detailed grains are daily/hour/pickup-zone, monthly pickup/drop-off route, monthly pickup-zone/hour/payment, daily drop-off zone and daily/hour/payment. These are independent tables: they cannot establish an exact daily/hour/route/payment intersection. Exact percentiles apply only to their stored group; larger-group percentiles require the raw records. Missing location/payment IDs remain explicit NULL groups rather than being discarded.

New detailed exports are in `postgres_import_data/*.csv.gz`, with row counts, sizes and population checks in `detailed_evidence_ledger.json`. They are database-import artifacts, not an extra claim of new raw coverage. All detailed operational/fare findings still cover 2025; historical published totals use their original separate population.
