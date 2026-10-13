SET search_path TO results, public;
SELECT
  q.source_month,
  q.raw_records,
  q.operational_trips,
  m.trips,
  q.raw_records - q.operational_trips AS exclusions,
  q.operational_trips - m.trips AS reconciliation_difference
FROM quality_month AS q
JOIN monthly_2025 AS m
  USING (source_month)
ORDER BY
  source_month NULLS FIRST;
