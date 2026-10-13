-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
WITH endpoints AS (
SELECT pu location_id,count(*) pickups,0::bigint dropoffs FROM flagged WHERE operational_valid GROUP BY pu
UNION ALL SELECT do_zone,count(*)*0,count(*) FROM flagged WHERE operational_valid GROUP BY do_zone),
counts AS(SELECT location_id,sum(pickups)::bigint pickups,sum(dropoffs)::bigint dropoffs FROM endpoints GROUP BY location_id)
SELECT c.location_id,coalesce(z.zone,'Unknown/outside mapped zones') AS zone,coalesce(z.borough,'Unknown') borough,
c.pickups,c.dropoffs,c.dropoffs-c.pickups net_dropoffs,
CASE WHEN c.dropoffs>c.pickups THEN 'More drop-offs' ELSE 'More pickups' END direction
FROM counts c LEFT JOIN zones z ON c.location_id=z.locationid ORDER BY net_dropoffs DESC;
