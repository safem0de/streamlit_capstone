CREATE OR REPLACE VIEW public.vw_fact_aqi_zero
AS SELECT count(*) FILTER (WHERE fact_air_quality.aqius = 0) AS zero_aqius,
    count(*) FILTER (WHERE fact_air_quality.temperature = 0) AS zero_temperature,
    count(*) FILTER (WHERE fact_air_quality.pressure = 0) AS zero_pressure,
    count(*) FILTER (WHERE fact_air_quality.humidity = 0) AS zero_humidity,
    count(*) FILTER (WHERE fact_air_quality.wind_speed = 0::numeric) AS zero_wind_speed
   FROM fact_air_quality;