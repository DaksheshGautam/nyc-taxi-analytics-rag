-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
WITH days AS (
  SELECT
    CASE WHEN CAST(EXTRACT(ISODOW FROM d) AS INT) <= 5 THEN 'Weekday' ELSE 'Weekend' END AS day_type,
    COUNT(*) AS calendar_days
  FROM GENERATE_SERIES(CAST('2025-01-01' AS DATE), CAST('2025-12-31' AS DATE), INTERVAL '1 DAY') AS s(d)
  GROUP BY
    1
), counts AS (
  SELECT
    CASE
      WHEN CAST(EXTRACT(ISODOW FROM pickup_at) AS INT) <= 5
      THEN 'Weekday'
      ELSE 'Weekend'
    END AS day_type,
    CAST(EXTRACT(HOUR FROM pickup_at) AS INT) AS "hour",
    COUNT(*) AS trips,
    COUNT(*) FILTER(WHERE
      fare_valid) AS fare_n,
    SUM(fare_usd) FILTER(WHERE
      fare_valid) AS fare_sum_usd
  FROM flagged
  WHERE
    operational_valid
  GROUP BY
    CASE
      WHEN CAST(EXTRACT(ISODOW FROM pickup_at) AS INT) <= 5
      THEN 'Weekday'
      ELSE 'Weekend'
    END,
    CAST(EXTRACT(HOUR FROM pickup_at) AS INT)
)
SELECT
  c.*,
  days.calendar_days,
  CAST(trips AS DOUBLE PRECISION) / CAST(calendar_days AS DOUBLE PRECISION) AS avg_daily_trips,
  CAST(fare_sum_usd AS DOUBLE PRECISION) / NULLIF(fare_n, 0) AS mean_fare_usd
FROM counts AS c
JOIN days
  USING (day_type)
ORDER BY
  day_type,
  2;
