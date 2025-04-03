CREATE OR REPLACE VIEW public.vw_fact_aqi_dup
AS SELECT fact_air_quality.time_id::text AS time_info,
    count(fact_air_quality.location_id) AS occurrences
   FROM fact_air_quality
  GROUP BY fact_air_quality.time_id
UNION ALL
 SELECT 'Total duplicates'::text AS time_info,
    count(*) AS occurrences
   FROM ( SELECT fact_air_quality.time_id,
            fact_air_quality.location_id
           FROM fact_air_quality
          GROUP BY fact_air_quality.time_id, fact_air_quality.location_id
         HAVING count(*) > 1) duplicate_counts;
) AS duplicate_counts;