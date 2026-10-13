-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  *
FROM results.airport_2025
WHERE
  airport_group <> 'Other routes';
