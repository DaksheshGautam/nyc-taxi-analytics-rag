-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
WITH agg AS (
  SELECT
    CAST(pickup_at AS DATE) AS pickup_date,
    pu AS location_id,
    COUNT(*) AS trips,
    COUNT(*) FILTER(WHERE
      fare_valid) AS fare_n,
    SUM(fare_usd) FILTER(WHERE
      fare_valid) AS fare_sum_usd,
    SUM(charge_usd) FILTER(WHERE
      fare_valid) AS charge_sum_usd,
    COUNT(*) FILTER(WHERE
      distance_valid) AS distance_n,
    SUM(distance_mi) FILTER(WHERE
      distance_valid) AS distance_sum_mi
  FROM flagged
  WHERE
    operational_valid
  GROUP BY
    1,
    2
), locations AS (
  SELECT DISTINCT
    pu AS location_id
  FROM flagged
  WHERE
    operational_valid
), dates AS (
  SELECT
    CAST(d AS DATE) AS pickup_date
  FROM GENERATE_SERIES(CAST('2025-01-01' AS DATE), CAST('2025-12-31' AS DATE), INTERVAL '1 DAY') AS g(d)
), points AS (
  SELECT
    *
  FROM results.zone_map_2025
)
SELECT
  d.pickup_date,
  l.location_id,
  COALESCE(z.Zone, 'Unknown/outside mapped zones') AS "zone",
  COALESCE(z.Borough, 'Unknown') AS borough,
  p.latitude,
  p.longitude,
  COALESCE(a.trips, 0) AS trips,
  COALESCE(a.fare_n, 0) AS fare_n,
  COALESCE(a.fare_sum_usd, 0) AS fare_sum_usd,
  COALESCE(a.charge_sum_usd, 0) AS charge_sum_usd,
  COALESCE(a.distance_n, 0) AS distance_n,
  COALESCE(a.distance_sum_mi, 0) AS distance_sum_mi
FROM dates AS d
CROSS JOIN locations AS l
LEFT JOIN agg AS a
  ON d.pickup_date = a.pickup_date
  AND l.location_id IS NOT DISTINCT FROM a.location_id
LEFT JOIN zones AS z
  ON l.location_id = z.LocationID
LEFT JOIN points AS p
  ON l.location_id = p.location_id
ORDER BY
  1,
  2;
