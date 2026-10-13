-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  year,
  COUNT(*) AS months_available,
  SUM(raw_records) AS raw_records,
  SUM(compressed_bytes) AS compressed_bytes,
  CASE WHEN COUNT(*) = 12 THEN 'Full year' ELSE 'Partial Jan-Aug' END AS period_status
FROM historical_month
GROUP BY
  year
ORDER BY
  year;
