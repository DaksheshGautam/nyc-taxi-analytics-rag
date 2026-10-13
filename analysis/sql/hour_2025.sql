-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  CAST(EXTRACT(HOUR FROM pickup_at) AS INT) AS "hour",
  COUNT(*) AS trips
FROM flagged
WHERE
  operational_valid
GROUP BY
  "hour"
ORDER BY
  "hour";
