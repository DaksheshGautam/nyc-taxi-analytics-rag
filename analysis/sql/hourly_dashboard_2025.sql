-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  *,
  CAST(trips AS DOUBLE PRECISION) / 365.0 AS avg_daily_trips,
  CAST(fare_sum_usd AS DOUBLE PRECISION) / 365.0 AS avg_daily_fare_usd,
  CAST(charge_sum_usd AS DOUBLE PRECISION) / 365.0 AS avg_daily_charge_usd,
  CAST(fare_sum_usd AS DOUBLE PRECISION) / NULLIF(fare_n, 0) AS mean_fare_usd,
  CAST(charge_sum_usd AS DOUBLE PRECISION) / NULLIF(fare_n, 0) AS mean_charge_usd,
  CAST(distance_sum_mi AS DOUBLE PRECISION) / NULLIF(distance_n, 0) AS mean_distance_mi,
  CAST(trips AS DOUBLE PRECISION) / SUM(trips) OVER () AS trip_share,
  CASE WHEN trips = MAX(trips) OVER () THEN 'Peak hour' ELSE 'Other hours' END AS peak_status,
  LPAD(CAST("hour" AS TEXT), 2, '0') || ':00' AS hour_label
FROM results.fare_hour_2025
ORDER BY
  1;
