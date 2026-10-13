-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  fare_usd,
  COUNT(*) AS records,
  COUNT(*) FILTER(WHERE
    operational_valid) AS operational_trips,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY
    charge_usd) AS median_charge_usd,
  MIN(charge_usd) AS minimum_charge_usd,
  MAX(charge_usd) AS maximum_charge_usd
FROM flagged
WHERE
  payment_type = 0 AND fare_usd < 0 AND charge_usd >= 0
GROUP BY
  1
ORDER BY
  records DESC NULLS LAST
LIMIT 20;
