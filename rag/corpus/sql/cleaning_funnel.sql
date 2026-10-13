-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  1 AS stage_no,
  'Published records' AS stage,
  COUNT(*) AS records,
  COUNT(*) - COUNT(*) FILTER(WHERE
    operational_valid) AS removed_to_next
FROM flagged
UNION ALL
SELECT
  2,
  'Operational trips',
  COUNT(*),
  COUNT(*) - COUNT(*) FILTER(WHERE
    fare_valid)
FROM flagged
WHERE
  operational_valid
UNION ALL
SELECT
  3,
  'Fare-eligible trips',
  COUNT(*),
  0
FROM flagged
WHERE
  operational_valid AND fare_valid
ORDER BY
  1;
