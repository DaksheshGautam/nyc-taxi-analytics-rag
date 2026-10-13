-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  COUNT(*) AS trips,
  COUNT(*) FILTER(WHERE
    distance_valid) AS distance_n,
  COUNT(*) FILTER(WHERE
    distance_mi = 0) AS zero_distance_trips,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    duration_min) AS median_duration_min,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY
    duration_min) AS p90_duration_min,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    distance_mi) FILTER(WHERE
    distance_valid) AS median_distance_mi,
  COUNT(*) FILTER(WHERE
    fare_valid) AS fare_n,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    fare_usd) FILTER(WHERE
    fare_valid) AS median_fare_usd
FROM flagged
WHERE
  operational_valid AND pu = 132 AND do_zone = 132;
