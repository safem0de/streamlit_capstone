CREATE OR REPLACE VIEW public.vw_dim_location_null
AS SELECT count(*) FILTER (WHERE dl.city IS NULL) AS null_city,
    count(*) FILTER (WHERE dl.state IS NULL) AS null_state,
    count(*) FILTER (WHERE dl.country IS NULL) AS null_country,
    count(*) FILTER (WHERE dl.region IS NULL) AS null_region
   FROM dim_location dl;