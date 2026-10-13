-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  payment_type,
  COUNT(*) AS trips,
  COUNT(*) FILTER(WHERE
    fare_valid) AS fare_n,
  SUM(fare_usd) FILTER(WHERE
    fare_valid) AS fare_sum_usd,
  SUM(charge_usd) FILTER(WHERE
    fare_valid) AS charge_sum_usd,
  SUM(tip_usd) FILTER(WHERE
    fare_valid AND payment_type = 1) AS recorded_card_tip_usd
FROM flagged
WHERE
  operational_valid
GROUP BY
  payment_type
ORDER BY
  trips DESC NULLS LAST;
