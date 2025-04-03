CREATE OR REPLACE VIEW public.vw_dim_time_dup
AS WITH dim_time_data AS (
         SELECT concat(dt.date, ',', dt.hour, ',', btrim(dt.day_of_week::text), ',', btrim(dt.month_name::text), ',', dt.quarter, ',', dt.week_of_year, ',', dt.is_weekend, ',', dt.is_holiday) AS dimension_time,
            count(*) AS duplicate_count
           FROM dim_time dt
          GROUP BY dt.date, dt.hour, dt.day_of_week, dt.month_name, dt.quarter, dt.week_of_year, dt.is_weekend, dt.is_holiday
        )
 SELECT dim_time_data.dimension_time,
    dim_time_data.duplicate_count
   FROM dim_time_data
UNION ALL
 SELECT 'Total duplicates'::text AS dimension_time,
    count(*) AS duplicate_count
   FROM ( SELECT dim_time_data.dimension_time
           FROM dim_time_data
          WHERE dim_time_data.duplicate_count > 1) duplicates_count;