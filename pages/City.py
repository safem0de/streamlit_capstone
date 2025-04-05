import platform
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from components.sidebar import *
from services.data_loader import *
from utils.helpers import *

st.set_page_config(
    page_title="State",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded" # "expanded", "collapsed", or "auto"
)

# ✅ สร้าง Sidebar Menu
create_sidebar()

# ตั้งค่าการเชื่อมต่อกับ PostgreSQL ถ้าไม่ได้ไปใช้ file backup
if connection_str("aqi_database")["status"] == "ok" and connection_str("aqi_datawarehouse")["status"] == "ok":
    conn_str_dwh = str(connection_str("aqi_datawarehouse")["data"])
    dim_location = fetch_data(conn_str_dwh, "SELECT * FROM dim_location")
    dim_time = fetch_data(conn_str_dwh, "SELECT * FROM dim_time")           # Scope for Weekly show
    fact_air = fetch_data(conn_str_dwh, "SELECT * FROM fact_air_quality")   # create view for simple
elif platform.system() == "Windows":
    print("📱 Running on Windows")
    dim_location = pd.read_csv("backup_data\\dim_location_202503292133.csv")
    dim_time = pd.read_csv("backup_data\\dim_time_202503292134.csv")
    fact_air = pd.read_csv("backup_data\\fact_air_quality_202503292134.csv")
else:
    dim_location = pd.read_csv("backup_data\\dim_location_202503292133.csv")
    dim_time = pd.read_csv("backup_data\\dim_time_202503292134.csv")
    fact_air = pd.read_csv("backup_data\\fact_air_quality_202503292134.csv")

dwh_data = pd.merge(fact_air, dim_location, on="location_id", how="inner")
print(dwh_data.head(5))
dwh_data = pd.merge(dwh_data, dim_time, on="time_id", how="inner")
print(dwh_data.head(5))


# ✅ Convert time_id เป็น datetime เพื่อความชัวร์ในการจัดลำดับ
dwh_data["datetime"] = pd.to_datetime(dwh_data["time_id"].astype(str), format="%Y%m%d%H")

# ✅ Sort ตาม location + datetime ล่าสุดมาก่อน
dwh_sorted = dwh_data.sort_values(by=["location_id", "datetime"], ascending=[True, False])
dwh_sorted["aqius_prev"] = dwh_sorted.groupby("location_id")["aqius"].shift(-1)
dwh_sorted["aqicn_prev"] = dwh_sorted.groupby("location_id")["aqicn"].shift(-1)
dwh_sorted["temperature_prev"] = dwh_sorted.groupby("location_id")["temperature"].shift(-1)
dwh_sorted["pressure_prev"] = dwh_sorted.groupby("location_id")["pressure"].shift(-1)
dwh_sorted["humidity_prev"] = dwh_sorted.groupby("location_id")["humidity"].shift(-1)
dwh_sorted["wind_speed_prev"] = dwh_sorted.groupby("location_id")["wind_speed"].shift(-1)

# ✅ ดึงเฉพาะแถวล่าสุดของแต่ละ location
print(dwh_sorted.head(5))

# Sidebar Filters
st.sidebar.header("🔎 ตัวกรองข้อมูล")

# ✅ 1. เลือก Region
region_options = ["ทั้งหมด"] + sorted(dim_location["region"].dropna().unique())
selected_region = st.sidebar.selectbox("เลือกภูมิภาค", region_options)

# ✅ 2. State Dropdown (ถ้ายังไม่เลือก Region -> ปิด Dropdown)
state_placeholder = st.sidebar.empty()

if selected_region == "ทั้งหมด":
    selected_state = state_placeholder.selectbox("เลือกจังหวัด", ["โปรดเลือกภูมิภาคก่อน"], disabled=True)
else:
    state_options = ["ทั้งหมด"] + sorted(dim_location[dim_location["region"] == selected_region]["state"].dropna().unique())
    selected_state = state_placeholder.selectbox("เลือกจังหวัด", state_options)

# ✅ 3. City Dropdown (ถ้ายังไม่เลือก State -> ปิด Dropdown)
city_placeholder = st.sidebar.empty()

if selected_state == "ทั้งหมด" or selected_state == "โปรดเลือกภูมิภาคก่อน":
    selected_city = city_placeholder.selectbox("เลือกอำเภอ/เขต", ["โปรดเลือกจังหวัดก่อน"], disabled=True)
else:
    city_options = ["ทั้งหมด"] + sorted(dim_location[dim_location["state"] == selected_state]["city"].dropna().unique())
    selected_city = city_placeholder.selectbox("เลือกอำเภอ/เขต", city_options)

# ✅ แสดงค่าที่เลือก

st.sidebar.write(f"🌍 Region: {selected_region}")
st.sidebar.write(f"🏙️ State: {selected_state}")
st.sidebar.write(f"🏘️ City: {selected_city}")

# ✅ ดึง "แถวล่าสุด" ของแต่ละ location
latest_per_location = dwh_sorted.groupby("location_id").head(1).copy()


# ✅ ดึงค่า AQI ล่าสุดและค่าก่อนหน้า
latest_per_location["aqius_diff"] = (
    latest_per_location["aqius"] - latest_per_location["aqius_prev"]
)

latest_per_location["aqicn_diff"] = (
    latest_per_location["aqicn"] - latest_per_location["aqicn_prev"]
)

latest_per_location["temperature_diff"] = (
    latest_per_location["temperature"] - latest_per_location["temperature_prev"]
)

latest_per_location["pressure_diff"] = (
    latest_per_location["pressure"] - latest_per_location["pressure_prev"]
)

latest_per_location["humidity_diff"] = (
    latest_per_location["humidity"] - latest_per_location["humidity_prev"]
)

latest_per_location["wind_speed_diff"] = (
    latest_per_location["wind_speed"] - latest_per_location["wind_speed_prev"]
)

print(latest_per_location.head(5))
if selected_region != "ทั้งหมด":
    latest_per_location = latest_per_location[latest_per_location["region"] == selected_region]
if selected_state != "ทั้งหมด" and selected_state != "โปรดเลือกภูมิภาคก่อน":
    latest_per_location = latest_per_location[latest_per_location["state"] == selected_state]
if selected_city != "ทั้งหมด" and selected_city != "โปรดเลือกจังหวัดก่อน":
    latest_per_location = latest_per_location[latest_per_location["city"] == selected_city]

# 📊 ค่าตัวแปรที่ต้องการแสดง
latest_timestamp_str = latest_per_location["datetime"].max().strftime("%d %b %Y %H:%M")

average_aqius = round(latest_per_location["aqius"].dropna().mean(), 3)
average_aqicn = round(latest_per_location["aqicn"].dropna().mean(), 3)
average_temp = round(latest_per_location["temperature"].dropna().mean(), 3)
average_pressure = round(latest_per_location["pressure"].dropna().mean(), 3)
average_humidity = round(latest_per_location["humidity"].dropna().mean(), 3)
average_wind_speed = round(latest_per_location["wind_speed"].dropna().mean(), 3)

delta_aqius = round(latest_per_location["aqius_diff"].dropna().mean(), 3)
delta_aqicn = round(latest_per_location["aqicn_diff"].dropna().mean(), 3)
delta_temp = round(latest_per_location["temperature_diff"].dropna().mean(), 3)
delta_pressure = round(latest_per_location["pressure_diff"].dropna().mean(), 3)
delta_humidity = round(latest_per_location["humidity_diff"].dropna().mean(), 3)
delta_wind_speed = round(latest_per_location["wind_speed_diff"].dropna().mean(), 3)

col1, col2, col3 = st.columns([1,1,1])
with col1:
    make_responsive("💨 ค่าเฉลี่ย AQI (US & CN)")
    # st.subheader("💨 ค่าเฉลี่ย AQI (US & CN)") 
    #"normal" (ค่าเริ่มต้น) "inverse" (สลับสีเขียว-แดง) "off" (ปิดการแสดงผล)
    st.metric(label="AQI (US)", value=f"{average_aqius:.3f}", delta=int(delta_aqius), delta_color="inverse")
    st.metric(label="AQI (CN)", value=f"{average_aqicn:.3f}", delta=int(delta_aqicn), delta_color="inverse")

with col2:
    make_responsive("🌡️ ค่าเฉลี่ยสภาพอากาศ")
    st.metric(label="Temperature (°C)", value=f"{average_temp:.3f}", delta=int(delta_temp), delta_color="inverse")
    st.metric(label="Pressure (hPa)", value=f"{average_pressure:.3f}", delta=int(delta_pressure), delta_color="normal")

with col3:
    make_responsive("💨 ค่าเฉลี่ยความชื้น/ความเร็วลม")
    st.metric(label="Humidity (%)", value=f"{average_humidity:.3f}", delta=int(delta_humidity), delta_color="normal")
    st.metric(label="Wind Speed (m/s)", value=f"{average_wind_speed:.3f}", delta=int(delta_wind_speed), delta_color="normal")

st.markdown("---")
# ✅ กราฟเปรียบเทียบ AQI ระหว่างภูมิภาค (ด้านล่าง col3)
make_responsive("📊 เปรียบเทียบ AQI ระหว่างภูมิภาค") 

region_aqi_data = (
    latest_per_location
    .groupby("region")[["aqius"]]
    .mean()
    .reset_index()
    .sort_values("aqius", ascending=False)
)

region_aqicn_data = (
    latest_per_location
    .groupby("region")[["aqicn"]]
    .mean()
    .reset_index()
    .sort_values("aqicn", ascending=False)
)

num_regions = len(region_aqi_data)

if num_regions > 5:
    _bargap = 0.3
elif 2 <= num_regions <= 5:
    _bargap = 0.5
else:
    _bargap = 0.6

if selected_region != "ทั้งหมด":
    state_in_region = (
        latest_per_location.groupby("state")["city"]
    )

    cites_in_region = (
        latest_per_location
        .groupby(["state", "city"])[["aqius", "aqicn"]]
        .mean()
        .reset_index()
        .sort_values(["state", "city"])
        .rename(columns={
            "state": "จังหวัด",
            "city": "อำเภอ",
            "aqius": "AQI (US) เฉลี่ย",
            "aqicn": "AQI (CN) เฉลี่ย"
        })
    )
    cites_in_region["AQI (US) เฉลี่ย"] = cites_in_region["AQI (US) เฉลี่ย"].apply(lambda x: f"{x:.3f}")
    cites_in_region["AQI (CN) เฉลี่ย"] = cites_in_region["AQI (CN) เฉลี่ย"].apply(lambda x: f"{x:.3f}")
    cites_in_region.index = cites_in_region.index + 1 # start no.=1

    row1_col_left, row1_col_right = st.columns([1, 1])
    with row1_col_left:
         # ✅ สร้างกราฟ Plotly Bar Chart
        aq_bar_chart = px.bar(region_aqi_data,
                            x="region", y="aqius", color="aqius",
                            title=f"ค่า AQI (US) เฉลี่ยของแต่ละภูมิภาค - อัปเดตล่าสุด ({latest_timestamp_str})",
                            labels={"aqius": "ค่า AQI (US)"},
                            text_auto=True,
                            height=500,
                            width=200)

        # ✅ ปรับขนาดแท่งของกราฟ
        aq_bar_chart.update_traces(texttemplate='%{y:.3f}', textposition='outside')
        aq_bar_chart.update_layout(
            xaxis_title="ภูมิภาค (Region)",
            yaxis_title="ค่า AQI เฉลี่ย (US)",
            showlegend=False,
            bargap=_bargap,  # ✅ ลดความกว้างระหว่างแท่ง
            bargroupgap=0.1,  # ✅ ลดระยะห่างของกลุ่มแท่ง
            xaxis=dict(categoryorder="total descending")  # ✅ เรียงแท่งจากมากไปน้อย
        )

        # ✅ แสดงกราฟ
        st.plotly_chart(aq_bar_chart, use_container_width=True)

    with row1_col_right:
        aqicn_chart = px.bar(
            region_aqicn_data,
            x="region",
            y="aqicn",
            color="aqicn",
            color_continuous_scale=px.colors.sequential.Agsunset,
            title=f"ค่า AQI (CN) เฉลี่ยของแต่ละภูมิภาค - อัปเดตล่าสุด: ({latest_timestamp_str})",
            labels={"aqicn": "ค่า AQI (CN)"},
            text_auto=True,
            height=500,
            text="aqicn"
        )
        aqicn_chart.update_traces(texttemplate='%{y:.3f}', textposition='outside')
        aqicn_chart.update_layout(
            xaxis_title="ภูมิภาค (Region)",
            yaxis_title="ค่า AQI เฉลี่ย (CN)",
            showlegend=False,
            bargap=_bargap,
            xaxis=dict(categoryorder="total descending")
        )

        st.plotly_chart(aqicn_chart, use_container_width=True)


    row2_col_left, row2_col_right = st.columns([1, 1])
    with row2_col_left:
        make_responsive(f"""🗺️ ภูมิภาค 
                        {selected_region}/
                        {selected_state}
                        {'' if any(x in selected_city for x in ['โปรด', 'ทั้ง']) else '/' + selected_city} : ({len(state_in_region)} จังหวัด/{len(cites_in_region)} เขต)""")
        st.dataframe(cites_in_region, use_container_width=True)


else:
    # ✅ สร้างกราฟ Plotly Bar Chart
    aq_bar_chart = px.bar(region_aqi_data,
                        x="region", y="aqius", color="aqius",
                        title=f"ค่า AQI (US) เฉลี่ยของแต่ละภูมิภาค - อัปเดตล่าสุด ({latest_timestamp_str})",
                        labels={"aqius": "ค่า AQI (US)"},
                        text_auto=True,
                        height=500,
                        width=200)

    # ✅ ปรับขนาดแท่งของกราฟ
    aq_bar_chart.update_traces(texttemplate='%{y:.3f}', textposition='outside')
    aq_bar_chart.update_layout(
        xaxis_title="ภูมิภาค (Region)",
        yaxis_title="ค่า AQI เฉลี่ย (US)",
        showlegend=False,
        bargap=_bargap,  # ✅ ลดความกว้างระหว่างแท่ง
        bargroupgap=0.1,  # ✅ ลดระยะห่างของกลุ่มแท่ง
        xaxis=dict(categoryorder="total descending")  # ✅ เรียงแท่งจากมากไปน้อย
    )

    # ✅ แสดงกราฟ
    st.plotly_chart(aq_bar_chart, use_container_width=True)

    aqicn_chart = px.bar(
        region_aqicn_data,
        x="region",
        y="aqicn",
        color="aqicn",
        color_continuous_scale=px.colors.sequential.Agsunset,
        title=f"ค่า AQI (CN) เฉลี่ยของแต่ละภูมิภาค - อัปเดตล่าสุด: ({latest_timestamp_str})",
        labels={"aqicn": "ค่า AQI (CN)"},
        text_auto=True,
        height=500,
    )
    aqicn_chart.update_traces(texttemplate='%{y:.3f}', textposition='outside')
    aqicn_chart.update_layout(
        xaxis_title="ภูมิภาค (Region)",
        yaxis_title="ค่า AQI เฉลี่ย (CN)",
        showlegend=False,
        bargap=_bargap,
        xaxis=dict(categoryorder="total descending")
    )

    st.plotly_chart(aqicn_chart, use_container_width=True)