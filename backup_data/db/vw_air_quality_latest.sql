CREATE OR REPLACE VIEW public.vw_air_quality_latest
AS SELECT air_quality_raw.aqi_id,
    air_quality_raw.city,
    air_quality_raw.state,
    air_quality_raw.region,
    air_quality_raw.country,
    air_quality_raw.latitude,
    air_quality_raw.longitude,
    air_quality_raw."timestamp",
    air_quality_raw.aqius,
    air_quality_raw.mainus,
    air_quality_raw.aqicn,
    air_quality_raw.maincn,
    air_quality_raw.temperature,
    air_quality_raw.pressure,
    air_quality_raw.humidity,
    air_quality_raw.wind_speed,
    air_quality_raw.wind_direction
   FROM air_quality_raw
  WHERE date(air_quality_raw."timestamp") = ((SELECT max(date(raw_data."timestamp")) AS max
           FROM air_quality_raw raw_data));