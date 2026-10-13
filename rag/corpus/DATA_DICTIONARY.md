# Data dictionary and aggregation contract

## Common fields

| Field | Definition | Aggregation |
|---|---|---|
| source_month | YYYY-MM from the source filename | Provenance/group key |
| raw_records | Parquet footer/source rows before cleaning | Additive over disjoint files |
| compressed_bytes | Download size in bytes | Additive; not memory footprint |
| trips | Operational source-month-matched pickups, duration >0 and <=180 min | Additive across disjoint groups |
| distance_n | Operational records with distance 0–100 miles inclusive | Additive |
| fare_n | Operational records with nonnegative fare/charge; payment nonmissing and not 4/6 (0 Flex Fare and 5 Unknown retained) | Additive |
| median_duration_min / p90_duration_min | Exact interpolated pooled duration percentiles | Never sum or average group percentiles |
| median_distance_mi | Exact pooled median over eligible distance fields | Never average medians |
| distance_sum_mi | Sum over distance_n | Divide by distance_n for mean |
| fare_sum_usd | Sum of fare_amount over fare_n | Divide by fare_n for mean |
| charge_sum_usd | Sum of total_amount over fare_n | Divide by fare_n for mean |
| median_fare_usd / median_charge_usd | Separate exact medians over fare_n | Difference is not median surcharge |
| pickup_share | Group trips / all operational trips, including unknown zones | Reported for the full 2025 denominator |
| calendar_days | Distinct observed pickup dates within weekday | All dates are present in this snapshot |
| trips_per_day | Weekday trip count divided by calendar days | Do not average without day weights |
| yoy_pct | 100 × (current matching-month records / prior matching-month records − 1) | Jan–Aug only |

## Result table grains

| Table | Grain and scope |
|---|---|
| historical_month | One row per published monthly file; 212 files, 2009-01–2026-08 |
| historical_year | One row per calendar year; 2026 partial |
| historical_comparable | One row per year; January–August only |
| monthly_2025 | One row per 2025 pickup/source month |
| annual_2025 | One pooled full-year row, computed directly from trips |
| weekday_hour_2025 | Weekday × pickup hour; full 2025 |
| weekday_2025 | Weekday; counts normalized by observed calendar days |
| hour_2025 / fare_hour_2025 | Pickup hour; full 2025 |
| zone_2025 | Pickup location ID; full 2025, unknown values retained |
| borough_2025 | Pickup borough; full 2025 |
| zone_month_2025 | Source month × pickup location ID |
| routes_2025 | Known pickup ID × known drop-off ID; n >=100, full year |
| route_top20_2025 | Twenty highest-volume qualifying routes; display subset |
| zone_top15_2025 | Fifteen highest-volume known pickup zones; display subset |
| airport_2025 | Mutually exclusive airport group including other routes |
| airport_only_2025 | Airport groups excluding other routes; display subset |
| airport_hour_2025 | Airport group × pickup hour |
| fare_band_2025 | Reported distance band; eligibility applied per metric |
| rate_2025 | Final rate code; null remains null, not zero |
| payment_2025 | Payment type; recorded credit-card tips are separate |
| quality_month | Source month × independent overlapping flags |
| quality_long | One row per selected full-year quality flag |
| sensitivity_2025 | One row comparing duration rules and positive distance |
| validation_summary | Raw, accepted, excluded operational totals |

## Airport and quality rules

Airport precedence: PU132 → JFK pickup; PU138 → LGA pickup; DO132 → JFK drop-off; DO138 → LGA drop-off; PU/DO1 → Newark zone; otherwise other routes. Rate2/3 are reported cross-checks. A trip between airports is assigned to its pickup airport first.

Location IDs 1–263 are known for route eligibility; 264/265/null/out-of-range records remain in global activity and geography tables. Known-ID status does not prove every reported location is correct.

Quality flags overlap and are counted over all raw records, unless a field explicitly says fare_sample or distance_sample. Negative money, zero distance, disputed payment and invalid timestamps are different flags. None is a duplicate indicator. No repeated rows are silently removed.

Column schemas by source month are preserved in source_manifest.json. Earlier fields differ in names, types and geography; historical summaries intentionally use the common record-count metric only. Missing surcharges are not imputed as observed zeros.


The Interactive explorer filters pickup date, borough and taxi zone across its seven views. Daily averages include all selected dates; monetary means use eligible sums/counts. Annual reference dashboards remain fixed to 2025. Payment code 0 is Flex Fare under the March 2025 TLC dictionary. See QUALITY_INVESTIGATION.md for disjoint cleaning rules, negative-money investigation and JFK within-zone caveat. Extension SQL/results are saved; nineteen business/reconciliation queries have been executed locally.


## Extension table grains

| Table | Grain and aggregation |
|---|---|
| cleaning_funnel | Three sequential record populations; do not sum stages |
| cleaning_waterfall | Disjoint priority reasons within each transition |
| payment_diagnostics | Payment code; raw/operational/fare counts remain separate |
| negative_money_patterns | Source month x payment code x operational status; money flags overlap |
| flex_negative_fare_values | Top 20 negative Flex Fare values with nonnegative charge |
| negative_counterpart_check | Existence test; matching positive rows are not one-to-one pairings |
| zone_pickup_dropoff_2025 | Zone ID; pickup and drop-off endpoint counts from the same operational population |
| zone_balance_top20 | Ten positive and ten negative NYC net balances; net = drop-offs minus pickups |
| jfk_within_zone_diagnostics | PU132/DO132 operational subset and fare-eligible subset |
| interactive_daily_2025 | Every 2025 calendar date x each of 262 observed pickup IDs, including zero-activity rows |

Explorer date and zone filters use pickup endpoints. Selected daily average is SUM(trips)/COUNTD(pickup_date); mean fare and charge use SUM(money)/SUM(fare_n). Null mean when no eligible records. Unknown/EWR records remain in global totals; only NYC zones are plotted on the map. Filtered medians are not calculated from aggregated snapshots.
