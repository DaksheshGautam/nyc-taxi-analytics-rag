-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  pu,
  do_zone,
  COALESCE(p.Zone, 'Unknown') AS pickup_zone,
  COALESCE(d.Zone, 'Unknown') AS dropoff_zone,
  COALESCE(p.Zone, 'Unknown') || ' → ' || COALESCE(d.Zone, 'Unknown') AS route,
  COUNT(*) AS trips,
  COUNT(*) FILTER(WHERE
    distance_valid) AS distance_n,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    duration_min) AS median_duration_min,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY
    duration_min) AS p90_duration_min,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    distance_mi) FILTER(WHERE
    distance_valid) AS median_distance_mi,
  SUM(distance_mi) FILTER(WHERE
    distance_valid) AS distance_sum_mi,
  COUNT(*) FILTER(WHERE
    fare_valid) AS fare_n,
  SUM(fare_usd) FILTER(WHERE
    fare_valid) AS fare_sum_usd,
  SUM(charge_usd) FILTER(WHERE
    fare_valid) AS charge_sum_usd,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    fare_usd) FILTER(WHERE
    fare_valid) AS median_fare_usd,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    charge_usd) FILTER(WHERE
    fare_valid) AS median_charge_usd
FROM flagged AS f
LEFT JOIN zones AS p
  ON f.pu = p.LocationID
LEFT JOIN zones AS d
  ON f.do_zone = d.LocationID
WHERE
  operational_valid AND pu_known AND do_known
GROUP BY
  pu,
  do_zone,
  COALESCE(p.Zone, 'Unknown'),
  COALESCE(d.Zone, 'Unknown'),
  COALESCE(p.Zone, 'Unknown') || ' → ' || COALESCE(d.Zone, 'Unknown')
HAVING
  COUNT(*) >= 100
ORDER BY
  trips DESC NULLS LAST;
