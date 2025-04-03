CREATE OR REPLACE VIEW public.vw_dim_time_null
AS SELECT count(*) FILTER (WHERE dt.date IS NULL) AS null_date,
    count(*) FILTER (WHERE dt.hour IS NULL) AS null_hour,
    count(*) FILTER (WHERE dt.day_of_week IS NULL) AS null_day_of_week,
    count(*) FILTER (WHERE dt.month_name IS NULL) AS null_month_name,
    count(*) FILTER (WHERE dt.quarter IS NULL) AS null_quarter,
    count(*) FILTER (WHERE dt.week_of_year IS NULL) AS null_week_of_year,
    count(*) FILTER (WHERE dt.is_weekend IS NULL) AS null_is_weekend,
    count(*) FILTER (WHERE dt.is_holiday IS NULL) AS null_is_holiday
   FROM dim_time dt;