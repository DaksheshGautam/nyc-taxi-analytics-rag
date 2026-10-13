SET search_path TO results, public;
SELECT
  airport_group,
  trips,
  median_duration_min,
  p90_duration_min,
  p90_duration_min - median_duration_min AS p90_median_gap_min
FROM airport_only_2025
ORDER BY
  trips DESC NULLS LAST;
