SET search_path TO results, public;
SELECT
  *
FROM payment_diagnostics
ORDER BY
  payment_type NULLS FIRST;
