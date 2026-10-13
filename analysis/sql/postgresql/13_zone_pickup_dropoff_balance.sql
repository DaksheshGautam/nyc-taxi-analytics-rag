SET search_path TO results, public;
SELECT
  location_id,
  zone,
  borough,
  pickups,
  dropoffs,
  net_dropoffs
FROM zone_pickup_dropoff_2025
WHERE
  borough IN ('Manhattan', 'Queens', 'Brooklyn', 'Bronx', 'Staten Island')
ORDER BY
  net_dropoffs DESC NULLS LAST;
