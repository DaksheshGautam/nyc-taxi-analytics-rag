SET search_path TO results, public;
SELECT
  stage_no,
  stage,
  records,
  removed_to_next
FROM cleaning_funnel
ORDER BY
  stage_no NULLS FIRST;
