-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
WITH classified AS (
  SELECT
    *,
    CASE
      WHEN pickup_at IS NULL OR dropoff_at IS NULL
      THEN '1 Missing pickup/drop-off timestamp'
      WHEN NOT COALESCE(pickup_month = source_month, FALSE)
      THEN '2 Pickup outside source month'
      WHEN duration_min <= 0
      THEN '3 Nonpositive duration'
      WHEN duration_min > 180
      THEN '4 Duration over 180 minutes'
      ELSE '5 Operational trips'
    END AS operational_reason,
    CASE
      WHEN fare_usd IS NULL OR charge_usd IS NULL OR payment_type IS NULL
      THEN '1 Missing fare/charge/payment'
      WHEN fare_usd < 0 OR charge_usd < 0
      THEN '2 Negative fare or total charge'
      WHEN payment_type = 4
      THEN '3 Disputed payment (nonnegative money)'
      WHEN payment_type = 6
      THEN '4 Voided payment (nonnegative money)'
      ELSE '5 Fare-eligible trips'
    END AS fare_reason
  FROM flagged
)
SELECT
  'Operational exclusion' AS stage,
  operational_reason AS reason,
  COUNT(*) AS records
FROM classified
GROUP BY
  2
UNION ALL
SELECT
  'Fare eligibility',
  fare_reason,
  COUNT(*)
FROM classified
WHERE
  operational_valid
GROUP BY
  2
ORDER BY
  1,
  2;
