-- public.vw_air_quality_latest_per_location_today source

CREATE OR REPLACE VIEW public.vw_air_quality_latest_per_location_today
AS SELECT DISTINCT ON (fa.location_id) fa.fact_id,
    fa.time_id,
    fa.location_id,
    fa.aqius,
    fa.mainus,
    fa.aqicn,
    fa.maincn,
    fa.temperature,
    fa.pressure,
    fa.humidity,
    fa.wind_speed,
    fa.wind_direction,
    fa.weather_icon
   FROM fact_air_quality fa
  WHERE (fa.time_id IN ( SELECT vw_latest_dim_time.time_id
           FROM vw_latest_dim_time))
  ORDER BY fa.location_id DESC;