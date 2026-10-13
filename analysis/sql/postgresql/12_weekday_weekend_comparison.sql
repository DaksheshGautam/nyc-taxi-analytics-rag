SET search_path TO results, public;
SELECT
  day_type,
  "hour",
  calendar_days,
  CAST(trips AS DOUBLE PRECISION) / NULLIF(calendar_days, 0) AS average_daily_trips
FROM daytype_hour_2025
ORDER BY
  day_type NULLS FIRST,
  "hour" NULLS FIRST;
