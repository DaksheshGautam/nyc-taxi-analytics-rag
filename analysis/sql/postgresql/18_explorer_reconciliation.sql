SET search_path TO results, public;
SELECT
  SUM(trips) AS operational_trips,
  SUM(fare_n) AS fare_eligible_records,
  COUNT(DISTINCT pickup_date) AS calendar_days,
  CAST(SUM(fare_sum_usd) AS DOUBLE PRECISION) / NULLIF(SUM(fare_n), 0) AS weighted_mean_fare_usd
FROM interactive_daily_2025;
