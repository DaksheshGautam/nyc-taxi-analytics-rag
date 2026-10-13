SET search_path TO results, public;
SELECT
  distance_band,
  trips,
  fare_n,
  median_fare_usd,
  median_charge_usd,
  CAST(fare_sum_usd AS DOUBLE PRECISION) / NULLIF(fare_n, 0) AS mean_meter_fare_usd,
  CAST(charge_sum_usd AS DOUBLE PRECISION) / NULLIF(fare_n, 0) AS mean_passenger_charge_usd
FROM fare_band_2025
ORDER BY
  median_distance_mi NULLS FIRST;
