-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
WITH nyc AS (
  SELECT
    *
  FROM results.zone_pickup_dropoff_2025
  WHERE
    borough IN ('Manhattan', 'Queens', 'Brooklyn', 'Bronx', 'Staten Island')
), ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY direction ORDER BY ABS(net_dropoffs) DESC NULLS LAST) AS rank_in_direction
  FROM nyc
)
SELECT
  location_id,
  "zone",
  borough,
  pickups,
  dropoffs,
  net_dropoffs,
  direction
FROM ranked
WHERE
  rank_in_direction <= 10
ORDER BY
  net_dropoffs DESC NULLS LAST;
