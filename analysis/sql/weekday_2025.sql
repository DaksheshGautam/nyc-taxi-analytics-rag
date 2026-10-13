-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  CAST(EXTRACT(ISODOW FROM pickup_at) AS INT) AS weekday_no,
  TO_CHAR(pickup_at, 'Dy') AS weekday,
  COUNT(*) AS trips,
  COUNT(DISTINCT CAST(pickup_at AS DATE)) AS calendar_days,
  CAST(COUNT(*) AS DOUBLE PRECISION) / COUNT(DISTINCT CAST(pickup_at AS DATE)) AS trips_per_day
FROM flagged
WHERE
  operational_valid
GROUP BY
  CAST(EXTRACT(ISODOW FROM pickup_at) AS INT),
  TO_CHAR(pickup_at, 'Dy')
ORDER BY
  weekday_no;
