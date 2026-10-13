SET search_path TO results, public;
SELECT
  "hour",
  trips,
  CAST(trips AS DOUBLE PRECISION) / NULLIF(365.0, 0) AS average_daily_trips,
  CAST(fare_sum_usd AS DOUBLE PRECISION) / NULLIF(365.0, 0) AS average_daily_meter_fares_usd,
  CAST(fare_sum_usd AS DOUBLE PRECISION) / NULLIF(NULLIF(fare_n, 0), 0) AS average_fare_per_eligible_trip_usd,
  CAST(charge_sum_usd AS DOUBLE PRECISION) / NULLIF(NULLIF(fare_n, 0), 0) AS average_charge_per_eligible_trip_usd
FROM hourly_dashboard_2025
ORDER BY
  "hour" NULLS FIRST;
