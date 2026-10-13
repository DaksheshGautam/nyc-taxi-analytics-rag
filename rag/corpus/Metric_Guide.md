# Metric and population guide

## Three populations
Historical counts mean published source-file rows, before cleaning. Detailed 2025 operational trips require source-month-matched pickup, both timestamps and duration greater than zero and at most 180 minutes. Fare eligibility is an operational subset with nonmissing nonnegative fare/charge and payment not disputed or voided. Do not mix their denominators.

## Monetary fields
fare_amount is recorded meter fare; total_amount is the recorded total passenger charge. Cash tips are absent. Recorded sums do not establish collected revenue, profit or driver earnings. Means divide monetary sums by fare-eligible counts. Separate medians cannot be subtracted to obtain median surcharges.

## Percentiles and distance
SQL exact pooled quantile_cont calculates median and p90. Percentiles are not additive and stored group medians cannot be averaged. Distance metrics separately require reported distance from 0 through 100 miles inclusive. Zero distance remains eligible for distance and activity.

## Endpoint and map geography
Net zone balance equals drop-offs minus pickups. Positive means more recorded arrivals and negative more recorded departures. Both endpoint counts use the same operational records. Cross-boundary and unknown endpoints can prevent NYC subtotals balancing. Tableau's density map weights 259 representative NYC zone points by pickups; these are approximate zone locations, not trip GPS.

## Daily denominators
Hourly daily activity uses all 365 calendar days in 2025, or 261 weekdays and 104 weekend days. Heatmap weekday counts use actual occurrences. Selected Explorer daily averages use all selected dates, including zero-activity date-zone combinations. Fare means use selected eligible counts.

Evidence: DATA_DICTIONARY.md, Analysis_Report.pdf pages 2-4, 6-8 and 10; retained SQL summary tables.
