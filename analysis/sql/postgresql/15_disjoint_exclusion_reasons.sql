SET search_path TO results, public;
SELECT
  stage,
  reason,
  records
FROM cleaning_waterfall
ORDER BY
  stage NULLS FIRST,
  reason NULLS FIRST;
