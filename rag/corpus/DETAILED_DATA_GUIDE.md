# Detailed PostgreSQL data guide

Detailed records cover 2025 operational trips (48,157,684) and their fare-eligible subset (44,727,165). Each of the five aggregate tables independently reconciles to both totals. Do not add these totals across tables: each table summarizes the same trips at a different grain.

## Available grains

- `detail.daily_hour_pickup_zone`: 1,429,444 groups. Every observed group is retained, including null location/payment keys.
- `detail.monthly_route`: 467,678 groups. Every observed group is retained, including null location/payment keys.
- `detail.monthly_zone_hour_payment`: 221,643 groups. Every observed group is retained, including null location/payment keys.
- `detail.daily_dropoff_zone`: 92,171 groups. Every observed group is retained, including null location/payment keys.
- `detail.daily_hour_payment`: 43,750 groups. Every observed group is retained, including null location/payment keys.

`daily_hour_pickup_zone`: pickup calendar date, pickup hour 0–23, pickup taxi zone.
`monthly_route`: source month, pickup zone and drop-off zone.
`monthly_zone_hour_payment`: source month, pickup zone, pickup hour and payment code.
`daily_dropoff_zone`: pickup calendar date and drop-off zone. This date is the pickup date, not the drop-off date.
`daily_hour_payment`: pickup calendar date, pickup hour and payment code.

## Measures and correct aggregation

`trips` is the operational count. `fare_n` counts operational and fare-eligible records; `distance_n` counts operational records with distance between 0 and 100 miles inclusive. `duration_sum_min` covers all operational trips. Fare and charge sums use only fare-eligible records. `distance_sum_mi` uses valid-distance records. Card-tip sums/counts apply to fare-eligible card records with a recorded tip; these do not measure cash tips. CBD-fee sums/counts cover fare-eligible records with a recorded CBD fee. Negative fees are not silently dropped when the trip otherwise passes fare eligibility.

Combined means must divide combined sums by combined denominators: fare sum/fare_n; charge sum/fare_n; duration sum/trips; distance sum/distance_n; card tip sum/card_tip_n; CBD fee sum/cbd_fee_n. Missing eligible values remain null; empty denominators produce no mean. Stored median_duration_min, p90_duration_min and median_fare_usd are exact only for their stored group. Never average them to calculate a larger group's percentile.

## Boundaries

The table grains cannot answer arbitrary cross-dimensional intersections. Exact date+hour+pickup-zone queries are supported. Exact month+pickup-zone+drop-off-zone queries are supported. Exact date+hour+route+payment combinations and individual trip lookups require raw data, which is local. No absence of an observed group proves unmet demand. Period averages use calendar days in the requested period, including days with zero observed activity. Historical published volume is a separate population and must not be mixed with these operational counts.

SQL definitions: sql/detail_*.sql. Source and reconciliation proof: detailed_evidence_ledger.json. Taxi-zone names and boroughs join through taxi_analysis.zones. Dataset snapshot: 12 October 2026.
