-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  *
FROM results.zone_2025
WHERE
  location_id BETWEEN 1 AND 263
ORDER BY
  trips DESC NULLS LAST
LIMIT 15;
