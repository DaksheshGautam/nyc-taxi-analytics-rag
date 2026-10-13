-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  year,
  SUM(raw_records) AS jan_aug_records,
  CAST(SUM(raw_records) AS DOUBLE PRECISION) / (
    CASE WHEN year % 4 = 0 THEN 244.0 ELSE 243.0 END
  ) AS records_per_day,
  100.0 * (
    CAST(SUM(raw_records) AS DOUBLE PRECISION) / LAG(SUM(raw_records)) OVER (ORDER BY year) - 1
  ) AS yoy_pct
FROM historical_month
WHERE
  month <= 8
GROUP BY
  year
ORDER BY
  year;
