-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  pu AS location_id,
  COALESCE(z.Zone, 'Unknown/outside mapped zones') AS "zone",
  COALESCE(z.Borough, 'Unknown') AS borough,
  COUNT(*) AS trips,
  CAST(COUNT(*) AS DOUBLE PRECISION) / SUM(COUNT(*)) OVER () AS pickup_share,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    duration_min) AS median_duration_min
FROM flagged AS f
LEFT JOIN zones AS z
  ON f.pu = z.LocationID
WHERE
  operational_valid
GROUP BY
  pu,
  COALESCE(z.Zone, 'Unknown/outside mapped zones'),
  COALESCE(z.Borough, 'Unknown')
ORDER BY
  trips DESC NULLS LAST;
