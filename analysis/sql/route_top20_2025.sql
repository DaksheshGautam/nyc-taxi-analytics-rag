-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  *
FROM results.routes_2025
ORDER BY
  trips DESC NULLS LAST
LIMIT 20;
