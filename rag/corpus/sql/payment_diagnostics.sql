-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  payment_type,
  CASE payment_type
    WHEN 0
    THEN 'Flex Fare'
    WHEN 1
    THEN 'Card'
    WHEN 2
    THEN 'Cash'
    WHEN 3
    THEN 'No charge'
    WHEN 4
    THEN 'Dispute'
    WHEN 5
    THEN 'Unknown'
    WHEN 6
    THEN 'Voided'
    ELSE 'Missing/unrecognized'
  END AS payment_label,
  COUNT(*) AS raw_records,
  COUNT(*) FILTER(WHERE
    operational_valid) AS operational_trips,
  COUNT(*) FILTER(WHERE
    operational_valid AND fare_valid) AS fare_n,
  COUNT(*) FILTER(WHERE
    fare_usd < 0 OR charge_usd < 0) AS negative_money_raw,
  COUNT(*) FILTER(WHERE
    operational_valid AND (
      fare_usd < 0 OR charge_usd < 0
    )) AS negative_money_operational,
  COUNT(*) FILTER(WHERE
    fare_usd IS NULL OR charge_usd IS NULL) AS missing_money,
  COUNT(*) FILTER(WHERE
    fare_usd = 0 AND charge_usd = 0) AS zero_money,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    fare_usd) FILTER(WHERE
    operational_valid AND fare_valid) AS median_eligible_fare_usd,
  SUM(fare_usd) FILTER(WHERE
    operational_valid AND fare_valid) AS eligible_fare_sum_usd
FROM flagged
GROUP BY
  1
ORDER BY
  1;
