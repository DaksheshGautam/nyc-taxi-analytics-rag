# Data quality investigation and spatial observations

## Record-processing funnel

48,722,602 published records → 48,157,684 operational records → 44,727,165 fare-eligible records.

Operational exclusions: 564,918 (1.16% of published records). Disjoint priority order: missing timestamps; pickup outside source month; nonpositive duration; duration over 180 minutes. In this snapshot there are no missing timestamps. The remaining disjoint counts are 214 outside source month, 546,304 nonpositive duration and 18,400 over 180 minutes. The raw flag for >180 minutes has 18,401 records, because one also falls outside its source month. Overlapping flag counts must not be summed.

Fare-only exclusions: 3,430,519 (7.12% of operational records). Apply missing monetary/payment fields first, then negative fare or total charge, then disputed/voided payment. In this snapshot missing money/payment fields and voided payments are zero. Negative monetary fields remove 2,853,180 operational records; a further 577,339 nonnegative-money disputes are removed. Negative disputed records are already in the negative-money group.

Both fare_amount and total_amount must be nonmissing and nonnegative; payment_type must be nonmissing and not 4/6. Code 0 (Flex Fare), code 3 (No charge) and code 5 (Unknown) are retained if their amounts meet the rule. Zero fares/charges remain eligible. These choices produce a recorded-fare sample, not a cash-flow statement. Other financial populations could be defensible and must be defined separately.

Distance eligibility is a separate rule: observed mileage 0–100 inclusive. Missing, negative and >100-mile distances affect distance statistics rather than removing operational trips. Zero-distance records and unknown zones remain in operational totals. Unknown endpoints cannot be plotted or assigned to NYC zones; they are retained in global endpoint counts. There is no imputation, automatic deduplication or claim that remaining records are error-free.

## Correct payment-code interpretation

The current [official TLC yellow taxi dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf), dated 18 March 2025, defines 0 as **Flex Fare**. The previous dashboard's “Unspecified (0)” label was incorrect and has been replaced. This is not missing payment data. There are 11,609,242 operational Flex Fare records (24.11% of operational activity); 9,562,369 pass the fare rules. Actual code 5 (Unknown) contains only two operational records.

## Negative-money patterns: observations, not a refund classification

The raw negative-money flag covers 2,853,594 records, of which 2,853,180 are operational. Flex Fare accounts for 2,047,090 raw negative-money records (71.74% of the flag). Of those, 1,879,872 have a negative fare_amount but nonnegative total_amount. The most frequent such recorded fare is −$4.75 (1,048,380 raw records; 1,048,322 operational), with median total charge $4.14. Values vary; this pattern is not safely described as a simple refund or missing payment. The official dictionary consulted does not establish the cause of these negative monetary patterns.

Among operational records with **both** fare and total charge negative, 968,516 records exist. Of them, 712,945 (73.61%) have at least one positive record matching pickup/drop-off timestamps, both zone IDs, recorded distance and exactly opposite fare/charge values. This is an existence check, not one-to-one pairing; multiple records can share a counterpart. Vendor IDs and transaction IDs are absent from the analysis stage. The result is compatible with reversal/adjustment patterns but does not prove a refund, duplicate or vendor-specific explanation. No rows are deduplicated or reclassified on this evidence.

All counts and distributions are retained in payment_diagnostics.csv, negative_money_patterns.csv, flex_negative_fare_values.csv and negative_counterpart_check.csv, with the original executed SQL and archived local MariaDB result copies. Converted PostgreSQL queries and server execution checks have separate provenance.

## Pickup versus drop-off geography

Use the same 48,157,684 operational records for both endpoint counts. Each record contributes one pickup and one drop-off. For each zone, net_dropoffs = dropoffs − pickups. A positive value means more recorded arrivals; a negative value means more recorded departures. It is not unmet demand, available taxis, vehicle rebalancing needs or proof of causation.

The displayed comparison selects ten NYC zones with the largest positive differences and ten with the largest negative differences. Whole-population pickup and drop-off sums each reconcile to 48,157,684, including unknown/off-city endpoints. A NYC-only subtotal need not balance because trips can cross its boundary. The daily explorer's geography filters refer to the **pickup** endpoint; the annual net-balance comparison is explicitly a separate full-year view.

East Harlem South has 550,093 drop-offs versus 355,891 pickups (+194,202), the largest positive NYC difference. JFK Airport has 453,087 drop-offs versus 2,047,254 pickups (−1,594,167), the largest negative difference. These describe recorded spatial patterns without explaining their causes.

The map remains an approximate weighted representation of points inside official taxi-zone polygons. It cannot show street-level pickup positions. This limitation is now prominent beside the map, instead of relying on a small footer.

## JFK-to-JFK records

There are 107,448 operational records whose pickup and drop-off both have zone ID 132. Their median recorded duration is 0.3 minutes, p90 12.2 minutes, median eligible distance 0.03 miles, and 43,026 (40.04%) have zero distance. Fare eligibility retains 74,450; their median fare is $28.20. These endpoints represent the same broad airport zone, not identical GPS points. The very short/zero-distance pattern is a quality caveat. The dataset alone cannot distinguish within-zone travel, corrections, test/meter events or other causes. These records are retained under the declared rules rather than being silently removed.

## Interactive aggregation contract

The explorer uses a calendar-complete 365-date × 262-observed-pickup-ID snapshot (95,630 rows). Missing date/zone combinations contain zero additive activity; this prevents sparse zones from losing zero-trip days. Date, pickup borough and zone filters apply to all explorer charts and cards. Counts and sums are additive. Mean fare = SUM(eligible fare_amount)/SUM(fare_n); mean total charge uses the same fare_n. Average daily trips = SUM(trips)/COUNTD(selected pickup_date). No average of zone means or group medians is used. Annual/historical dashboards remain explicitly fixed summaries, and the explorer contains no filtered median because exact medians cannot be reconstructed from its compact daily aggregates.
