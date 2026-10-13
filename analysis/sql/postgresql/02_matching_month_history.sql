SET search_path TO results, public;
SELECT
  year,
  jan_aug_records,
  records_per_day,
  yoy_pct
FROM historical_comparable
ORDER BY
  year NULLS FIRST;
