-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  source_month,
  pu AS location_id,
  COALESCE(z.Zone, 'Unknown/outside mapped zones') AS "zone",
  COALESCE(z.Borough, 'Unknown') AS borough,
  COUNT(*) AS trips
FROM flagged AS f
LEFT JOIN zones AS z
  ON f.pu = z.LocationID
WHERE
  operational_valid
GROUP BY
  source_month,
  pu,
  COALESCE(z.Zone, 'Unknown/outside mapped zones'),
  COALESCE(z.Borough, 'Unknown');
