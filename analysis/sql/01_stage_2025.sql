-- PostgreSQL 18. Trip-level queries require raw_trip_source; derived inputs live in results.
SET search_path TO taxi_analysis, public;
-- Import raw source fields into raw_trip_source before running trip-level analyses.
CREATE OR REPLACE VIEW trips AS
SELECT to_char(tpep_pickup_datetime,'YYYY-MM') pickup_month, source_month,
tpep_pickup_datetime pickup_at,tpep_dropoff_datetime dropoff_at,
extract(epoch FROM (tpep_dropoff_datetime-tpep_pickup_datetime))/60.0 duration_min,
trip_distance distance_mi,pulocationid pu,dolocationid do_zone,
ratecodeid rate_code,payment_type,fare_amount fare_usd,total_amount charge_usd,
tip_amount tip_usd,cbd_congestion_fee cbd_fee_usd FROM raw_trip_source;
