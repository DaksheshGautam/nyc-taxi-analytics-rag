-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  COUNT(*) AS raw_records,
  COUNT(*) FILTER(WHERE
    pickup_month = source_month AND duration_min > 0) AS positive_duration_in_month,
  COUNT(*) FILTER(WHERE
    pickup_month = source_month AND duration_min > 0 AND duration_min <= 120) AS within_120min,
  COUNT(*) FILTER(WHERE
    operational_valid) AS within_180min,
  COUNT(*) FILTER(WHERE
    pickup_month = source_month AND duration_min > 0 AND duration_min <= 240) AS within_240min,
  COUNT(*) FILTER(WHERE
    operational_valid AND distance_mi > 0) AS positive_distance_operations
FROM flagged;
