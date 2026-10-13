SET search_path TO results, public;
SELECT
  a.trips AS annual_trips,
  m.monthly_sum,
  w.weekday_hour_sum,
  z.zone_sum,
  (
    a.trips = m.monthly_sum AND a.trips = w.weekday_hour_sum AND a.trips = z.zone_sum
  ) AS all_match
FROM annual_2025 AS a
CROSS JOIN (
  SELECT
    SUM(trips) AS monthly_sum
  FROM monthly_2025
) AS m
CROSS JOIN (
  SELECT
    SUM(trips) AS weekday_hour_sum
  FROM weekday_hour_2025
) AS w
CROSS JOIN (
  SELECT
    SUM(trips) AS zone_sum
  FROM zone_2025
) AS z;
