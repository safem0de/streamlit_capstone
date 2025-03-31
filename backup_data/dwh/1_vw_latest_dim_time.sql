-- public.vw_latest_dim_time source

CREATE OR REPLACE VIEW public.vw_latest_dim_time
AS SELECT dt.time_id,
    dt.date,
    dt.hour,
    dt.day_of_week,
    dt.month_name,
    dt.quarter,
    dt.week_of_year,
    dt.is_weekend,
    dt.is_holiday
   FROM dim_time dt
  WHERE dt.date = (( SELECT max(dim_time.date) AS max
           FROM dim_time));