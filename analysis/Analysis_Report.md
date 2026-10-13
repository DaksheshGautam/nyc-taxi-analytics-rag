# NYC Yellow Taxi Operations

## 01 / Business question and key findings

NYC Yellow Taxi Operations | Source snapshot checked 12 October 2026 | Report revised 13 October 2026

Question: What do the published records show about hourly pickup activity, recorded fares, NYC endpoint patterns and record eligibility? Detailed analysis covers January-December 2025; historical comparisons use published source-file counts.

Activity: 48,157,684 operational trips. Median duration 13.6 minutes; p90 32.8 minutes. These exact pooled statistics use timestamp-eligible trips.

Hourly finding: pickup counts peak at 18:00-18:59 with 3,431,144 trips (9,400 per calendar day). Recorded meter-fare totals peak at 17:00. This compares operational pickup counts with sums from the smaller fare-eligible population.

Historical finding: January-August 2026 has 29,703,355 published records versus 31,556,438 in the matching 2025 period: -5.9%. Neither period is annualized.

Spatial finding: East Harlem South has the largest positive NYC endpoint balance (+194,202); JFK Airport has the largest negative balance (-1,594,167). Balance is drop-offs minus pickups, not an estimate of unmet demand.

Fare population: 44,727,165 eligible records. Their recorded meter-fare sum is USD 901.3 million. This sum does not measure collected revenue, driver earnings or profit.

Reading order: scope (2), definitions (3), cleaning (4), history (5), hourly activity (6), geography (7), airports and fares (8), quality and limitations (9), evidence appendix (10). Findings are descriptive; no causal explanation, forecast or projected benefit is presented.

Evidence: annual_2025.csv; hourly_dashboard_2025.csv; historical_comparable.csv; zone_pickup_dropoff_2025.csv.

## 02 / Sources and scope

Official source: NYC Taxi and Limousine Commission yellow taxi monthly Parquet files, taxi zone lookup CSV, and taxi_zones.zip boundaries. The source manifest records each URL, exact compressed bytes, footer row count, schema and verification status.

All 212 monthly file footers were verified. Earlier years use these exact record counts without downloading their trip records. Detailed January-December 2025 analysis uses all twelve files: 829,973,299 compressed bytes (829.97 MB decimal; approximately 791.52 MiB). This is a compressed file size, not a database or memory footprint.

The historical common metric is the number of published source-file records. It is assigned to the source month, not to a validated pickup date. Comparing historical raw counts with cleaned 2025 activity would mix definitions; the dashboard keeps them separate.

Representative schemas were inspected through the footer manifest for every month. The 2009 schema includes string Trip_Pickup_DateTime/Trip_Dropoff_DateTime, Start_Lon/Start_Lat, and Fare_Amt. Later files use typed tpep timestamps, zone IDs and fare_amount. Some older surcharge fields are null or absent. These changing fields are not needed for the common historical count metric and are not filled with observed zeros.

2025 processing stages compact trip fields into a local DuckDB database and executes memory-bounded SQL (1.5 GB limit, two threads). SQL results are exported to CSV. Those compact tables are also loaded into an isolated project-only local MariaDB 10.4.32 instance from XAMPP; nineteen business/reconciliation queries are executed and saved with their results.

The 11-dashboard Tableau workbook is a portable summary snapshot. It supports filtering on the Interactive explorer page. Refreshing the embedded CSV snapshots does not rerun the TLC download or SQL.

Evidence: source_manifest.json; validation.json; mysql_calculation_ledger.json.

| Population | Coverage | Definition |
| --- | --- | --- |
| Historical | 2009-01 to 2026-08 | Published monthly records |
| 2025 detail | 2025-01 to 2025-12 | All raw records retained |
| Operational | 2025 source-matched pickups | Duration >0 and <=180 min |
| Fare metrics | Operational subset | Nonnegative fare/charge; no dispute/void |

## 03 / Metric definitions

Operational trip: pickup timestamp belongs to the same calendar month as its source file; drop-off timestamp exists; elapsed timestamp duration is greater than zero and at most 180 minutes. The 180-minute threshold is an analyst rule for operational comparability, not a statement that every longer journey is impossible. Valid trips crossing midnight or into the next month remain eligible when their pickup belongs to the source month.

Time: NYC local meter timestamps as recorded. No timezone or daylight-saving conversion is imposed. Duration is timestamp difference in seconds divided by 60. The median and p90 use exact SQL quantile_cont interpolation over the relevant pooled trip population; monthly medians are never averaged into an annual figure.

Distance: reported meter miles. Distance summaries use non-null values between 0 and 100 miles inclusive. Zero-distance records remain in operational activity counts and distance summaries. Negative, missing or greater-than-100-mile distance fields are excluded only from distance metrics.

Meter fare: fare_amount. Passenger charge: total_amount as recorded, including recorded charges rather than a reconstructed component sum. Eligible fare records are operational trips with nonnegative fare_amount and total_amount and payment_type not equal to 4 (dispute) or 6 (void). Missing payment/money values are ineligible. Nonnegative zero fares remain eligible. Negative-money records are tracked separately; their meaning is not established; they are not removed from activity solely for being negative.

Known zones: IDs 1-263 for route comparisons. Pickup zone 264/265 and absent/unmapped values are retained in global activity totals and labeled unknown/outside mapped zones as appropriate. Route summaries require both zones in 1-263 and at least 100 operational trips. Displayed route tables show the most frequent qualifying routes; the complete qualifying route table is retained.

Airport groups use a mutually exclusive precedence: JFK pickup (PU 132), LGA pickup (PU 138), JFK drop-off (DO 132), LGA drop-off (DO 138), Newark zone (PU or DO 1), then other routes. A trip between airports belongs to the pickup airport group. Rate code 2 means JFK and 3 means Newark; these are cross-check counts, not a substitute for observed airport locations. airport_fee applies to pickups and is not used to infer every airport trip.

No deduplication is performed: repeated records are not automatically evidence of erroneous duplicates. No vehicle/employee identities are assumed. Cash tips are not captured. Observed trips cannot establish idle time, fleet utilization, unmet demand, shift earnings, operating profit, or optimal vehicle allocation.

Evidence: sql/01_stage_2025.sql; sql/annual_2025.sql; sql/airport_2025.sql.

## 04 / Cleaning funnel

The disjoint cleaning funnel is 48,722,602 published records -> 48,157,684 operational trips -> 44,727,165 fare-eligible records. Operational exclusions are 214 pickups outside the source month, 546,304 nonpositive durations and 18,400 durations over 180 minutes, evaluated in that priority order: 564,918 total.

The further 3,430,519 fare exclusions comprise 2,853,180 operational records with negative fare or total charge, followed by 577,339 disputed-payment records with nonnegative monetary fields. Missing timestamp, money or payment fields contribute no exclusions in this snapshot. Zero fares, zero distance and unknown zones remain under their documented rules.

Zero-distance and unknown-zone trips remain in operational activity. No deduplication is performed. Raw quality flags overlap and must not be summed into an exclusion total. The disjoint priority rules above reconcile the two transitions.

Evidence: cleaning_funnel.csv / cleaning_funnel.sql; cleaning_waterfall.csv / cleaning_waterfall.sql.

## 05 / Historical matching-period comparison

The verified full-year published record total is 48,722,602 for 2025 versus 41,169,720 for 2024 (+18.3%). These are source-file counts before cleaning.

Partial 2026 contains 29,703,355 records across January-August. Matching months in 2025 contain 31,556,438; the matching-month change is -5.9%. This comparison is preferable to comparing eight months against an entire prior year.

The chart compares the same eight source-file months each year, before operational cleaning. Historical counts are assigned to the source month rather than validated pickup date. The observed difference does not identify its cause.

Evidence: historical_year.csv / historical_year.sql; historical_comparable.csv / historical_comparable.sql.

## 06 / Hourly activity and recorded fares

Hourly charts divide annual trips in each pickup-hour bucket by all 365 calendar days. This measures average daily observed trips at that hour. It is different from the average fare per trip, which divides eligible fare sums by eligible record counts. Days with no eligible activity remain in the daily denominator.

The busiest pickup-hour bucket is 18:00-18:59: 3,431,144 annual operational trips, or 9,400 average daily pickups in that hour. It accounts for 7.1% of the annual activity. Overall activity averages 131,939 trips per calendar day.

The weekday/hour heatmap uses the actual number of each weekday in 2025: Wednesday occurs 53 times and other weekdays 52 times. Thursday at 18:00 has the strongest cell, averaging 10,703 observed trips. The weekday/weekend hourly lines divide by 261 weekdays and 104 weekend days respectively. Both peak at 18:00, averaging 9,820 weekday and 8,348 weekend trips in that bucket.

Recorded meter-fare totals peak at 17:00, while pickup volume peaks at 18:00. Each series is divided by 365 calendar days; fare sums use eligible monetary records and pickup counts use all operational trips. This difference does not establish a causal effect of pickup hour.

Evidence: hourly_dashboard_2025.csv / hourly_dashboard_2025.sql; weekday_heatmap_2025.csv / weekday_heatmap_2025.sql.

## 07 / NYC pickup and drop-off patterns

Both endpoint counts use the same 48,157,684 operational records. Every record contributes one pickup and one drop-off. Net zone balance is drop-offs minus pickups; a positive value means more recorded arrivals and a negative value means more recorded departures.

East Harlem South has the strongest positive NYC balance: 550,093 drop-offs versus 355,891 pickups, or +194,202. JFK Airport has the strongest negative balance: 453,087 drop-offs versus 2,047,254 pickups, or -1,594,167. These are descriptive annual differences, not evidence of unmet demand or a taxi-rebalancing requirement.

The dashboard compares the ten strongest positive and ten strongest negative NYC zone balances in a signed bar chart. NYC subtotals need not balance because some journeys cross the displayed boundary or have unknown endpoints. All endpoint totals reconcile before restricting the display.

Evidence: zone_pickup_dropoff_2025.csv / zone_pickup_dropoff_2025.sql; zone_balance_top20.csv / zone_balance_top20.sql.

## 08 / Airport durations and fare distributions

Airport groups are mutually exclusive: JFK pickup, LGA pickup, JFK drop-off, LGA drop-off, Newark zone, then other routes. A journey between airports belongs to its pickup group. Geographic endpoints, rather than rate code, define these groups.

JFK pickups: n=2,047,254, median 41.3 minutes, p90 70.4. LGA pickups: n=1,275,310, median 28.3, p90 49.4 minutes. These pooled percentiles are not guaranteed travel times or recommended buffers.

Across eligible fare records, the median meter fare is USD 14.49 and median passenger charge is USD 22.13. The mean meter fare is USD 20.15, compared with mean passenger charge USD 28.95. These are distinct distributions; subtracting their medians does not produce the median surcharge.

Within-JFK caveat: PU132/DO132 has 107,448 operational records; 43,026 (40.0%) have zero distance. Median duration is 0.3 minutes and p90 is 12.2. Shared zone IDs do not mean identical GPS positions; the cause is not established.

Evidence: airport_only_2025.csv (airport_2025.sql); annual_2025.csv; jfk_within_zone_diagnostics.csv / jfk_within_zone_diagnostics.sql.

## 09 / Payment investigation and interpretation limits

The March 2025 TLC dictionary defines payment code 0 as Flex Fare, not unspecified payment. Flex Fare represents 11,609,242 operational records (24.1%) and 9,562,369 fare-eligible records. Unknown payment code 5 contains only two operational records.

Flex Fare accounts for 2,047,090 raw negative-money records (71.7% of that category). Of those, 1,879,872 have negative fare but nonnegative total charge. The most frequent such fare is -4.75, appearing in 1,048,380 raw records. The dictionary does not establish why this pattern occurs; treating all negative values as refunds would be unsupported.

Among 968,516 operational records with both fare and total charge negative, 712,945 have at least one positive counterpart matching timestamps, zones, distance and exactly opposite monetary amounts. This is an existence test, not a one-to-one transaction match; no transaction identifier establishes a refund or duplicate.

Completed-trip records do not measure failed requests, passenger queues, vehicle availability or operating costs. This report makes no estimate of unmet demand, fleet utilization, optimal allocation, earnings, profit or savings. Cash tips are absent from the recorded-tip field in the official dictionary.

Source rows can contain reporting anomalies and later revisions. Eligibility under the declared rules does not certify a record as accurate. No causal interpretation is made for negative money or short within-zone records.

The native NYC map uses representative points inside official taxi-zone polygons, weighted by pickups. Its 259 NYC zone points show approximate zone activity, not individual trip GPS locations. Unknown/off-city endpoints remain in overall totals.

Evidence: payment_diagnostics.csv; negative_money_patterns.csv; flex_negative_fare_values.csv; negative_counterpart_check.csv; corresponding SQL; TLC dictionary; tableau_validation.json.

## 10 / Evidence and reproducibility appendix

All figures are regenerated from the retained summaries used by the Tableau analysis. Evidence paths identify files in the project package: CSV outputs are under data/, calculations under sql/, and manifests/ledgers at the package root. The calculation ledgers connect queries to their actual result files.

MariaDB query 09_annual_reconciliation returned all_match=1. Query 18_explorer_reconciliation returned 48,157,684 operational trips, 44,727,165 fare records and 365 dates. Nineteen executed business/reconciliation outputs are saved.

Tableau filter testing covered all-data defaults, Manhattan, January Manhattan and January Midtown Center. All five KPI cards matched independently calculated sums and weighted means. Every possible filter combination was not tested. Explorer averages include all selected calendar dates; monetary means divide selected sums by selected eligible counts. Filtered medians are not reconstructed from group medians.

Rebuild order: analyze.py > analyze_hourly.py > analyze_extensions.py > load_mysql.py > build_tableau.py > write_report.py. Raw trip files remain outside the public package.

Official sources: <link href="https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page" color="#3B82B8">NYC TLC Trip Record Data</link>; <link href="https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf" color="#3B82B8">Yellow taxi dictionary (18 March 2025)</link>. Official zone lookup and boundary links are retained in README.md. Definitions are cited separately from observed findings.

Evidence: saved SQL outputs and provenance ledgers.

| Area | Evidence | Retained file |
| --- | --- | --- |
| Sources | Source files and footer/schema checks | source_manifest.json; validation.json |
| Definitions | Staging and annual pooled metrics | sql/01_stage_2025.sql; annual_2025.csv |
| Cleaning | Disjoint population transitions | cleaning_waterfall.csv; cleaning_funnel.csv |
| Time | Hourly/weekday normalization | hourly_calculation_ledger.json |
| Geography | Same-population endpoints | zone_pickup_dropoff_2025.csv |
| Quality | Payment and counterpart checks | extension_calculation_ledger.json |
| Local SQL | 19 executed query outputs | mysql_results/; mysql_calculation_ledger.json |
| Filters | 4 native selections verified | interactive_filter_validation.json |
| Report | Assertions and input hashes | report_evidence_validation.json |
