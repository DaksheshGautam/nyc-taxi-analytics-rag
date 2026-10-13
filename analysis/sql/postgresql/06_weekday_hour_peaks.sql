SET search_path TO results, public;
SELECT
  weekday,
  "hour",
  trips,
  median_duration_min,
  p90_duration_min
FROM weekday_hour_2025
ORDER BY
  trips DESC NULLS LAST
LIMIT 15;
