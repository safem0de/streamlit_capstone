CREATE OR REPLACE VIEW public.vw_dim_location_dup
AS SELECT concat(dim_location.city, ',', dim_location.state, ',', dim_location.country, ',', dim_location.region) AS location,
    count(*) AS duplicate_count
   FROM dim_location
  GROUP BY dim_location.city, dim_location.state, dim_location.country, dim_location.region
UNION ALL
 SELECT 'Total duplicates'::text AS location,
    count(*) AS duplicate_count
   FROM ( SELECT dim_location.city,
            dim_location.state,
            dim_location.country,
            dim_location.region
           FROM dim_location
          GROUP BY dim_location.city, dim_location.state, dim_location.country, dim_location.region
         HAVING count(*) > 1) duplicates;