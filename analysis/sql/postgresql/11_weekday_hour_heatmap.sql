SET search_path TO results, public;
SELECT
  weekday,
  "hour",
  trips,
  calendar_days,
  CAST(trips AS DOUBLE PRECISION) / NULLIF(calendar_days, 0) AS average_daily_trips
FROM weekday_heatmap_2025
ORDER BY
  weekday_no NULLS FIRST,
  "hour" NULLS FIRST;
