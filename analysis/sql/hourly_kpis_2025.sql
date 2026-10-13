-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  a.trips AS annual_trips,
  CAST(a.trips AS DOUBLE PRECISION) / 365.0 AS avg_daily_trips,
  (
    SELECT
      "hour"
    FROM results.hourly_dashboard_2025
    ORDER BY
      trips DESC NULLS LAST
    LIMIT 1
  ) AS busiest_hour,
  (
    SELECT
      CAST(MAX(trips) AS DOUBLE PRECISION) / SUM(trips)
    FROM results.hourly_dashboard_2025
  ) AS peak_hour_share,
  a.fare_sum_usd,
  a.charge_sum_usd,
  CAST(a.fare_sum_usd AS DOUBLE PRECISION) / a.fare_n AS mean_fare_usd,
  CAST(a.charge_sum_usd AS DOUBLE PRECISION) / a.fare_n AS mean_charge_usd,
  (
    SELECT
      "hour"
    FROM results.hourly_dashboard_2025
    ORDER BY
      fare_sum_usd DESC NULLS LAST
    LIMIT 1
  ) AS peak_fare_hour
FROM results.annual_2025 AS a;
