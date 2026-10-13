-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  source_month,
  COUNT(*) AS raw_records,
  COUNT(*) FILTER(WHERE
    operational_valid) AS operational_trips,
  COUNT(*) FILTER(WHERE
    NOT COALESCE(pickup_month = source_month, FALSE)) AS pickup_outside_source_month,
  COUNT(*) FILTER(WHERE
    pickup_at IS NULL OR dropoff_at IS NULL) AS missing_timestamps,
  COUNT(*) FILTER(WHERE
    duration_min <= 0) AS nonpositive_duration,
  COUNT(*) FILTER(WHERE
    duration_min > 180) AS over_180_minutes,
  COUNT(*) FILTER(WHERE
    distance_mi = 0) AS zero_distance,
  COUNT(*) FILTER(WHERE
    distance_mi IS NULL) AS missing_distance,
  COUNT(*) FILTER(WHERE
    distance_mi < 0 OR distance_mi > 100) AS implausible_distance,
  COUNT(*) FILTER(WHERE
    fare_usd < 0 OR charge_usd < 0) AS negative_money,
  COUNT(*) FILTER(WHERE
    payment_type = 4) AS disputed,
  COUNT(*) FILTER(WHERE
    payment_type = 6) AS voided,
  COUNT(*) FILTER(WHERE
    NOT pu_known) AS unknown_pickup,
  COUNT(*) FILTER(WHERE
    NOT do_known) AS unknown_dropoff,
  COUNT(*) FILTER(WHERE
    operational_valid AND fare_valid) AS fare_sample,
  COUNT(*) FILTER(WHERE
    operational_valid AND distance_valid) AS distance_sample
FROM flagged
GROUP BY
  source_month
ORDER BY
  source_month;
