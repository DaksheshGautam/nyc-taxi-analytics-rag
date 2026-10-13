-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
CREATE OR REPLACE VIEW flagged AS
SELECT
  *,
  COALESCE(
    pickup_month = source_month
    AND NOT dropoff_at IS NULL
    AND duration_min > 0
    AND duration_min <= 180,
    FALSE
  ) AS operational_valid,
  COALESCE(distance_mi >= 0 AND distance_mi <= 100, FALSE) AS distance_valid,
  COALESCE(fare_usd >= 0 AND charge_usd >= 0 AND NOT payment_type IN (4, 6), FALSE) AS fare_valid,
  COALESCE(pu BETWEEN 1 AND 263, FALSE) AS pu_known,
  COALESCE(do_zone BETWEEN 1 AND 263, FALSE) AS do_known,
  CASE
    WHEN pu = 132
    THEN 'JFK pickup'
    WHEN pu = 138
    THEN 'LGA pickup'
    WHEN do_zone = 132
    THEN 'JFK drop-off'
    WHEN do_zone = 138
    THEN 'LGA drop-off'
    WHEN pu = 1 OR do_zone = 1
    THEN 'Newark zone'
    ELSE 'Other routes'
  END AS airport_group,
  CASE
    WHEN distance_mi IS NULL OR distance_mi < 0 OR distance_mi > 100
    THEN 'Invalid distance'
    WHEN distance_mi = 0
    THEN '0 miles'
    WHEN distance_mi <= 1
    THEN '0-1 miles'
    WHEN distance_mi <= 3
    THEN '1-3 miles'
    WHEN distance_mi <= 5
    THEN '3-5 miles'
    WHEN distance_mi <= 10
    THEN '5-10 miles'
    ELSE '10-100 miles'
  END AS distance_band
FROM trips;
