SET search_path TO results, public;
SELECT
  *
FROM flex_negative_fare_values
ORDER BY
  records DESC NULLS LAST;
