-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  airport_group,
  CAST(EXTRACT(HOUR FROM pickup_at) AS INT) AS "hour",
  COUNT(*) AS trips,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    duration_min) AS median_duration_min,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY
    duration_min) AS p90_duration_min
FROM flagged
WHERE
  operational_valid AND airport_group <> 'Other routes'
GROUP BY
  airport_group,
  CAST(EXTRACT(HOUR FROM pickup_at) AS INT);
