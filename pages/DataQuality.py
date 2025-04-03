import streamlit as st
from components.sidebar import *
from services.data_loader import *
from utils.helpers import *

st.set_page_config(
    page_title="Data Quality Report",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded" # "expanded", "collapsed", or "auto"
)

# ✅ สร้าง Sidebar Menu
create_sidebar()

if connection_str("aqi_database")["status"] == "ok" and connection_str("aqi_datawarehouse")["status"] == "ok":
    conn_str_dwh = str(connection_str("aqi_datawarehouse")["data"])
    #/* null check */
    dim_loc_null = fetch_data(conn_str_dwh, "SELECT * FROM vw_dim_location_null")
    dim_time_null = fetch_data(conn_str_dwh, "SELECT * FROM vw_dim_time_null")
    fact_air_null = fetch_data(conn_str_dwh, "SELECT * FROM vw_fact_aqi_null")
    #/* zero check */
    fact_air_zero = fetch_data(conn_str_dwh, "SELECT * FROM vw_fact_aqi_zero")
    #/* duplicate check */
    dim_loc_dup = fetch_data(conn_str_dwh, "SELECT * FROM vw_dim_location_dup")
    dim_time_dup = fetch_data(conn_str_dwh, "SELECT * FROM vw_dim_time_dup")
    fact_air_dup = fetch_data(conn_str_dwh, "SELECT * FROM vw_fact_aqi_dup")


# ✅ หมวด Null Check
render_section(
    "Null Value Check",
    [
        ("dimension table - location (null)", dim_loc_null),
        ("dimension table - time (null)", dim_time_null),
        ("fact table - aqi (null)", fact_air_null)
    ]
)

# ✅ หมวด Zero Value Check
render_section(
    "Zero Value Check",
    [
        ("fact table - aqi (zero)", fact_air_zero)
    ]
)

# ✅ หมวด Duplicate Check
render_section(
    "Duplicate Value Check",
    [
        ("dimension table - location (duplicate)", dim_loc_dup),
        ("dimension table - time (duplicate)", dim_time_dup),
        ("fact table - aqi (duplicate)", fact_air_dup)
    ]
)