-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  source_month,
  payment_type,
  operational_valid,
  COUNT(*) AS records,
  COUNT(*) FILTER(WHERE
    fare_usd < 0 AND charge_usd < 0) AS both_negative,
  COUNT(*) FILTER(WHERE
    fare_usd < 0 AND COALESCE(charge_usd >= 0, FALSE)) AS fare_only_negative,
  COUNT(*) FILTER(WHERE
    charge_usd < 0 AND COALESCE(fare_usd >= 0, FALSE)) AS charge_only_negative,
  COUNT(*) FILTER(WHERE
    duration_min <= 0) AS nonpositive_duration,
  COUNT(*) FILTER(WHERE
    distance_mi = 0) AS zero_distance,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    fare_usd) AS median_recorded_fare_usd
FROM flagged
WHERE
  fare_usd < 0 OR charge_usd < 0
GROUP BY
  source_month,
  payment_type,
  operational_valid
ORDER BY
  1,
  2,
  3;
