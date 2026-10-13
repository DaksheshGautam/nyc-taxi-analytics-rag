-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
WITH totals AS(SELECT sum(pickup_outside_source_month) outside_month,sum(nonpositive_duration) nonpositive_duration,
sum(over_180_minutes) over_180_minutes,sum(zero_distance) zero_distance,sum(negative_money) negative_money,
sum(unknown_pickup) unknown_pickup,sum(disputed) disputed,sum(voided) voided FROM results.quality_month)
SELECT metric,records FROM totals CROSS JOIN LATERAL (VALUES
('outside_month',outside_month),('nonpositive_duration',nonpositive_duration),('over_180_minutes',over_180_minutes),
('zero_distance',zero_distance),('negative_money',negative_money),('unknown_pickup',unknown_pickup),
('disputed',disputed),('voided',voided)) AS unpivoted(metric,records);
