-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
WITH negative AS (
  SELECT
    pickup_at,
    dropoff_at,
    pu,
    do_zone,
    distance_mi,
    fare_usd,
    charge_usd
  FROM flagged
  WHERE
    operational_valid AND fare_usd < 0 AND charge_usd < 0
), positive AS (
  SELECT
    pickup_at,
    dropoff_at,
    pu,
    do_zone,
    distance_mi,
    fare_usd,
    charge_usd
  FROM flagged
  WHERE
    operational_valid AND fare_usd > 0 AND charge_usd > 0
)
SELECT
  COUNT(*) AS negative_both_money_operational,
  COUNT(*) FILTER(WHERE
    EXISTS(
      SELECT
        1
      FROM positive AS p
      WHERE
        p.pickup_at = n.pickup_at
        AND p.dropoff_at = n.dropoff_at
        AND p.pu = n.pu
        AND p.do_zone = n.do_zone
        AND p.distance_mi = n.distance_mi
        AND p.fare_usd = -n.fare_usd
        AND p.charge_usd = -n.charge_usd
    )) AS exact_positive_counterpart_records
FROM negative AS n;
