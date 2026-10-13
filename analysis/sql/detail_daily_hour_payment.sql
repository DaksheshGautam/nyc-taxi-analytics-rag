SET search_path TO taxi_analysis,public;
SELECT
  CAST(pickup_at AS DATE) AS pickup_date,
  CAST(EXTRACT(HOUR FROM pickup_at) AS INT) AS pickup_hour,
  payment_type,
  COUNT(*) AS trips,
  COUNT(*) FILTER(WHERE
    fare_valid) AS fare_n,
  COUNT(*) FILTER(WHERE
    distance_valid) AS distance_n,
  SUM(duration_min) AS duration_sum_min,
  SUM(distance_mi) FILTER(WHERE
    distance_valid) AS distance_sum_mi,
  SUM(fare_usd) FILTER(WHERE
    fare_valid) AS fare_sum_usd,
  SUM(charge_usd) FILTER(WHERE
    fare_valid) AS charge_sum_usd,
  COUNT(*) FILTER(WHERE
    fare_valid AND payment_type = 1 AND tip_usd IS NOT NULL) AS card_tip_n,
  SUM(tip_usd) FILTER(WHERE
    fare_valid AND payment_type = 1) AS card_tip_sum_usd,
  COUNT(*) FILTER(WHERE
    fare_valid AND cbd_fee_usd IS NOT NULL) AS cbd_fee_n,
  SUM(cbd_fee_usd) FILTER(WHERE
    fare_valid) AS cbd_fee_sum_usd,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    duration_min) AS median_duration_min,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY
    duration_min) AS p90_duration_min,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    fare_usd) FILTER(WHERE
    fare_valid) AS median_fare_usd
FROM flagged
WHERE
  operational_valid
GROUP BY
  1,
  2,
  3;
