-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  rate_code,
  COUNT(*) AS trips,
  COUNT(*) FILTER(WHERE
    distance_valid) AS distance_n,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    duration_min) AS median_duration_min,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY
    duration_min) AS p90_duration_min,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    distance_mi) FILTER(WHERE
    distance_valid) AS median_distance_mi,
  SUM(distance_mi) FILTER(WHERE
    distance_valid) AS distance_sum_mi,
  COUNT(*) FILTER(WHERE
    fare_valid) AS fare_n,
  SUM(fare_usd) FILTER(WHERE
    fare_valid) AS fare_sum_usd,
  SUM(charge_usd) FILTER(WHERE
    fare_valid) AS charge_sum_usd,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    fare_usd) FILTER(WHERE
    fare_valid) AS median_fare_usd,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    charge_usd) FILTER(WHERE
    fare_valid) AS median_charge_usd
FROM flagged
WHERE
  operational_valid
GROUP BY
  rate_code
ORDER BY
  trips DESC NULLS LAST;
