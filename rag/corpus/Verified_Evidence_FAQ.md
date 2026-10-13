# Verified evidence FAQ
Generated from the retained October 2026 snapshot. Detailed trip findings cover 2025. Each entry identifies supporting originals.

## What is the busiest pickup hour? Peak hourly trips and demand
For 2025 operational trips, the busiest pickup hour is 18:00-18:59. It contains 3,431,144 annual pickups, 9,400 average daily pickups and 7.12% of operational trips. These are completed-record counts, not unmet demand.
Evidence: data/hourly_dashboard_2025.csv

## When do recorded meter fare totals peak?
Recorded meter-fare totals peak at 17:00 in 2025. Operational pickup counts peak at 18:00. The fare series uses fare-eligible records; the pickup series uses all operational records. No causal explanation for the difference is established.
Evidence: data/hourly_dashboard_2025.csv

## How many total operational trips and average daily trips are there?
The 2025 operational population is 48,157,684 trips. Average daily operational activity is 131,939 trips, using all 365 calendar dates. The total is not the raw published count.
Evidence: data/annual_2025.csv

## Why were 564,918 records excluded? What is the cleaning funnel?
Published 2025 records: 48,722,602. Operational trips: 48,157,684. Fare-eligible records: 44,727,165. Operational exclusions total 564,918: 214 pickups outside source month, 546,304 nonpositive durations and 18,400 durations over 180 minutes, in disjoint priority order. Missing timestamps add zero exclusions.
Evidence: data/cleaning_funnel.csv; data/cleaning_waterfall.csv

## Why are 48.16 million operational trips different from 44.73 million fare eligible records?
The 48,157,684 operational trips include records that fail fare eligibility. A further 3,430,519 records are excluded from fare analysis: 2,853,180 negative fare/charge records, then 577,339 disputed payments with nonnegative money. The remaining 44,727,165 are fare eligible. Payment and money must be nonmissing; money nonnegative; payment not 4 or 6.
Evidence: data/cleaning_waterfall.csv

## What does payment code 0 mean? Is it unspecified or unknown?
The TLC yellow taxi dictionary dated 18 March 2025 defines payment code 0 as Flex Fare. It is not missing or unspecified payment. Flex Fare has 11,609,242 operational trips (24.11%) and 9,562,369 eligible fare records. Code 5 Unknown contains only 2 operational records.
Evidence: data/payment_diagnostics.csv; QUALITY_INVESTIGATION.md

## Are negative fares refunds? What did the money investigation find?
Negative money is not established to represent refunds. Flex Fare contains 2,047,090 raw negative-money records. Of these, 1,879,872 have negative fare and nonnegative charge. The most frequent such fare value is -4.75 (1,048,380 raw records). The source dictionary does not explain the cause.
Evidence: data/payment_diagnostics.csv; data/negative_money_patterns.csv; data/flex_negative_fare_values.csv

## Does a matching positive counterpart prove refunds or duplicates?
Of 968,516 operational records with both money values negative, 712,945 have at least one matching positive counterpart: timestamps, zone IDs and distance match and fare/charge have opposite signs and equal magnitudes. This is an existence test, not a one-to-one transaction match. It proves neither refunds nor duplication. No deduplication was applied.
Evidence: data/negative_counterpart_check.csv; QUALITY_INVESTIGATION.md

## Why are there JFK to JFK trips? What are the same-zone caveats?
PU132/DO132 means both endpoints share the JFK taxi zone, not identical GPS positions. There are 107,448 operational records; 43,026 (40.04%) have zero recorded distance. Median duration is 0.3 minutes; p90 12.2 minutes. The cause and transaction validity are not established.
Evidence: data/jfk_within_zone_diagnostics.csv

## Which NYC zone has more drop-offs than pickups? Largest net arrivals
East Harlem South has the largest positive annual NYC balance: 550,093 drop-offs minus 355,891 pickups = +194,202. This is an observed endpoint difference, not a recommendation about taxi supply.
Evidence: data/zone_pickup_dropoff_2025.csv

## Which NYC zone has more pickups than drop-offs? Largest net departures
JFK Airport has the largest negative annual NYC balance: 453,087 drop-offs minus 2,047,254 pickups = -1,594,167. Balance is drop-offs minus pickups; negative means more pickups.
Evidence: data/zone_pickup_dropoff_2025.csv

## How is pickup versus drop-off zone balance calculated?
Zone balance = drop-offs minus pickups. Each of the same 48,157,684 operational records contributes one pickup and one drop-off. Positive means more arrivals; negative means more departures. Global endpoint totals reconcile; NYC subtotals need not because other endpoints can be off-city or unknown.
Evidence: data/zone_pickup_dropoff_2025.csv

## How did January August 2026 change versus 2025? Historical volume decrease
January-August 2026 has 29,703,355 published records versus 31,556,438 in January-August 2025, a -5.9% change. These are raw source-file counts, not cleaned operational trips. Neither period is annualized; no cause is established.
Evidence: data/historical_comparable.csv

## Do you have every trip from previous years? What is the dataset coverage?
Historical coverage is January 2009 through August 2026: 212 verified monthly source-file footers. Earlier trip records were not downloaded or cleaned. Detailed operational analysis uses all twelve 2025 trip files. The 2026 period is partial, January-August only.
Evidence: SCOPE.md; Analysis_Report.pdf

## What are median trip duration and p90? Exact pooled statistics
The 2025 operational median duration is 13.6 minutes and p90 is 32.8 minutes. Exact pooled SQL quantile_cont values are used. P90 is a percentile of recorded observations, not a guaranteed travel time. Monthly medians are not averaged into the annual median.
Evidence: data/annual_2025.csv; DATA_DICTIONARY.md

## What are median recorded meter fare and total charge?
For 44,727,165 eligible 2025 records, median meter fare is USD 14.49 and median recorded total charge is USD 22.13. Subtracting these medians does not produce the median surcharge. Monetary values are nominal USD.
Evidence: data/annual_2025.csv

## What is average mean fare per trip and total charge?
For 44,727,165 eligible 2025 records, mean recorded meter fare is USD 20.15 and mean recorded total charge is USD 28.95. Each mean divides the selected monetary sum by its eligible record count.
Evidence: data/annual_2025.csv

## Is the 901.3 million fare total collected revenue, profit or earnings?
The 2025 eligible recorded meter-fare sum is USD 901.3 million. It is a sum of recorded fare_amount values, not a measurement of collected revenue, driver earnings or profit. Cash tips are absent; costs and driver shifts are not supplied.
Evidence: data/annual_2025.csv; Analysis_Report.pdf

## How are missing negative abnormal or zero distance records handled?
Distance summaries use nonmissing reported meter miles from 0 to 100 inclusive. Zero distance is retained. Negative, missing and above-100-mile distance values affect distance metrics only, not otherwise eligible operational counts. The annual distance median is 1.85 miles before display rounding. Unknown zones remain in global activity.
Evidence: DATA_DICTIONARY.md; data/annual_2025.csv

## How are trips by hour daily averages and weekday heatmap calculated?
Annual trips in each pickup hour are divided by all 365 calendar days. Weekday hourly patterns divide by 261 weekdays; weekend patterns by 104 weekend dates. Weekday-hour heatmap cells divide by the number of that weekday: Wednesday 53, other weekdays 52 in 2025. Missing date-zone activity is represented by zero rows in the Explorer calendar.
Evidence: DATA_DICTIONARY.md; Analysis_Report.pdf

## JFK pickup median and p90 travel duration sample size
For JFK pickup in 2025: 2,047,254 operational trips, median duration 41.3 minutes and p90 70.4 minutes. Fare-eligible sample: 1,827,276. These are pooled recorded distributions, not forecasts or guaranteed time buffers.
Evidence: data/airport_only_2025.csv

## LGA pickup median and p90 travel duration sample size
For LGA pickup in 2025: 1,275,310 operational trips, median duration 28.3 minutes and p90 49.4 minutes. Fare-eligible sample: 1,211,942. These are pooled recorded distributions, not forecasts or guaranteed time buffers.
Evidence: data/airport_only_2025.csv

## LGA drop-off median and p90 travel duration sample size
For LGA drop-off in 2025: 416,005 operational trips, median duration 28.4 minutes and p90 45.1 minutes. Fare-eligible sample: 407,368. These are pooled recorded distributions, not forecasts or guaranteed time buffers.
Evidence: data/airport_only_2025.csv

## JFK drop-off median and p90 travel duration sample size
For JFK drop-off in 2025: 332,923 operational trips, median duration 50.8 minutes and p90 75.7 minutes. Fare-eligible sample: 321,229. These are pooled recorded distributions, not forecasts or guaranteed time buffers.
Evidence: data/airport_only_2025.csv

## Newark zone median and p90 travel duration sample size
For Newark zone in 2025: 90,578 operational trips, median duration 36.1 minutes and p90 59.3 minutes. Fare-eligible sample: 87,248. These are pooled recorded distributions, not forecasts or guaranteed time buffers.
Evidence: data/airport_only_2025.csv

## Can I average monthly medians or filter daily average and fares?
Explorer date, pickup borough and taxi zone filters apply to seven views. Daily average = selected trips / distinct selected calendar dates, including zero-activity rows. Mean fare = selected eligible fare sum / selected fare-eligible count. Stored group medians cannot be averaged into filtered medians. The other dashboards are fixed full-year reference views.
Evidence: DATA_DICTIONARY.md; Analysis_Report.pdf

## Can the data explain causes, predict future demand, driver profit or taxi rebalancing?
No causal explanation, forecast, driver profit, utilization, unmet-demand estimate or optimal taxi allocation is established by this analysis. Completed trip records lack failed requests, passenger queues, vehicle availability, costs and driver-shift information. Negative-money meanings and short within-JFK records remain unresolved.
Evidence: Analysis_Report.pdf; QUALITY_INVESTIGATION.md