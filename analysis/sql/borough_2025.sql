-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  COALESCE(z.Borough, 'Unknown') AS borough,
  COUNT(*) AS trips,
  CAST(COUNT(*) AS DOUBLE PRECISION) / SUM(COUNT(*)) OVER () AS pickup_share
FROM flagged AS f
LEFT JOIN zones AS z
  ON f.pu = z.LocationID
WHERE
  operational_valid
GROUP BY
  COALESCE(z.Borough, 'Unknown')
ORDER BY
  trips DESC NULLS LAST;
