-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  CAST(EXTRACT(ISODOW FROM pickup_at) AS INT) AS weekday_no,
  TO_CHAR(pickup_at, 'Dy') AS weekday,
  CAST(EXTRACT(HOUR FROM pickup_at) AS INT) AS "hour",
  COUNT(*) AS trips,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    duration_min) AS median_duration_min,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY
    duration_min) AS p90_duration_min
FROM flagged
WHERE
  operational_valid
GROUP BY
  CAST(EXTRACT(ISODOW FROM pickup_at) AS INT),
  TO_CHAR(pickup_at, 'Dy'),
  CAST(EXTRACT(HOUR FROM pickup_at) AS INT)
ORDER BY
  weekday_no,
  "hour";
