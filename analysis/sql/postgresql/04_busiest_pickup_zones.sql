SET search_path TO results, public;
SELECT
  location_id,
  zone,
  borough,
  trips,
  pickup_share
FROM zone_2025
WHERE
  location_id BETWEEN 1 AND 263
ORDER BY
  trips DESC NULLS LAST
LIMIT 15;
