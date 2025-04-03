CREATE OR REPLACE VIEW public.vw_fact_aqi_null
AS SELECT count(*) FILTER (WHERE fact_air_quality.aqius IS NULL) AS null_aqius,
    count(*) FILTER (WHERE fact_air_quality.mainus IS NULL) AS null_mainus,
    count(*) FILTER (WHERE fact_air_quality.aqicn IS NULL) AS null_aqicn,
    count(*) FILTER (WHERE fact_air_quality.temperature IS NULL) AS null_temperature,
    count(*) FILTER (WHERE fact_air_quality.pressure IS NULL) AS null_pressure,
    count(*) FILTER (WHERE fact_air_quality.humidity IS NULL) AS null_humidity,
    count(*) FILTER (WHERE fact_air_quality.wind_speed IS NULL) AS null_wind_speed,
    count(*) FILTER (WHERE fact_air_quality.wind_direction IS NULL) AS null_wind_direction
FROM fact_air_quality;