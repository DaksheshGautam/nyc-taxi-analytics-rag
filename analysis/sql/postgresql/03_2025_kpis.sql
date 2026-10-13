SET search_path TO results, public;
SELECT
  trips,
  median_duration_min,
  p90_duration_min,
  median_distance_mi,
  fare_n,
  median_fare_usd,
  median_charge_usd,
  CAST(fare_sum_usd AS DOUBLE PRECISION) / NULLIF(fare_n, 0) AS mean_meter_fare_usd,
  CAST(charge_sum_usd AS DOUBLE PRECISION) / NULLIF(fare_n, 0) AS mean_passenger_charge_usd
FROM annual_2025;
