-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
SELECT
  *,
  CASE payment_type
    WHEN 0
    THEN 'Flex Fare'
    WHEN 1
    THEN 'Card'
    WHEN 2
    THEN 'Cash'
    WHEN 3
    THEN 'No charge'
    WHEN 4
    THEN 'Dispute'
    WHEN 5
    THEN 'Unknown'
    WHEN 6
    THEN 'Voided'
    ELSE 'Unspecified (0)'
  END AS payment_label,
  CAST(trips AS DOUBLE PRECISION) / SUM(trips) OVER () AS trip_share
FROM results.payment_2025
ORDER BY
  trips DESC NULLS LAST;
