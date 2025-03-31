import platform
import streamlit as st
import pandas as pd
import numpy as np
from components.sidebar import *
from services.data_loader import *
from utils.helpers import *
import plotly.express as px

st.set_page_config(
    page_title="Weekly AQI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded" # "expanded", "collapsed", or "auto"
)

# ✅ ซ่อน Sidebar Navigation
hide_sidebar_nav()

# ✅ สร้าง Sidebar Menu
create_sidebar()

# ตั้งค่าการเชื่อมต่อกับ PostgreSQL ถ้าไม่ได้ไปใช้ file backup
data = pd.DataFrame
if connection_str("aqi_database")["status"] == "ok":
    conn_str = str(connection_str("aqi_database")["data"])
    print(conn_str)
    data = fetch_data(conn_str, str("SELECT * FROM vw_air_quality_latest"))
elif platform.system() == "Windows":
    print("🪟 Running on Windows")
    data = pd.read_csv("backup_data\\air_quality_raw_202503202336.csv")
    # Load datasets
    dim_location = pd.read_csv("backup_data\\dim_location_202503292133.csv")
    dim_time = pd.read_csv("backup_data\\dim_time_202503292134.csv")
    fact_air = pd.read_csv("backup_data\\fact_air_quality_202503292134.csv")
else:
    data = pd.read_csv("backup_data/air_quality_raw_202503202336.csv")
    # Load datasets
    dim_location = pd.read_csv("backup_data/dim_location_202503292133.csv")
    dim_time = pd.read_csv("backup_data/dim_time_202503292134.csv")
    fact_air = pd.read_csv("backup_data/fact_air_quality_202503292134.csv")

st.title("Dashboard AQI Weekly 📊")

# Sidebar Filters
st.sidebar.header("🔎 ตัวกรองข้อมูล")

# ✅ 1. เลือก Region
region_options = ["ทั้งหมด"] + sorted(data["region"].dropna().unique())
selected_region = st.sidebar.selectbox("เลือกภูมิภาค", region_options)

# ✅ 2. State Dropdown (ถ้ายังไม่เลือก Region -> ปิด Dropdown)
state_placeholder = st.sidebar.empty()

if selected_region == "ทั้งหมด":
    selected_state = state_placeholder.selectbox("เลือกจังหวัด", ["โปรดเลือกภูมิภาคก่อน"], disabled=True)
else:
    state_options = ["ทั้งหมด"] + sorted(data[data["region"] == selected_region]["state"].dropna().unique())
    selected_state = state_placeholder.selectbox("เลือกจังหวัด", state_options)

# ✅ 3. City Dropdown (ถ้ายังไม่เลือก State -> ปิด Dropdown)
city_placeholder = st.sidebar.empty()

if selected_state == "ทั้งหมด" or selected_state == "โปรดเลือกภูมิภาคก่อน":
    selected_city = city_placeholder.selectbox("เลือกอำเภอ/เขต", ["โปรดเลือกจังหวัดก่อน"], disabled=True)
else:
    city_options = ["ทั้งหมด"] + sorted(data[data["state"] == selected_state]["city"].dropna().unique())
    selected_city = city_placeholder.selectbox("เลือกอำเภอ/เขต", city_options)

# ✅ แสดงค่าที่เลือก
st.sidebar.write(f"🌍 Region: {selected_region}")
st.sidebar.write(f"🏙️ State: {selected_state}")
st.sidebar.write(f"🏘️ City: {selected_city}")

# Join Fact Table กับ Location Table
dwh_data = pd.merge(fact_air, dim_location, on="location_id", how="left")
dwh_data["datetime"] = pd.to_datetime(dwh_data["time_id"].astype(str), format="%Y%m%d%H")
print(dwh_data.head(10))

fact_air["date_str"] = fact_air["time_id"].astype(str).str[:8]  # ตัดเฉพาะ YYYYMMDD
fact_air["date"] = pd.to_datetime(fact_air["date_str"], format="%Y%m%d").dt.date

latest_date = fact_air["date"].max()
str_latest_date = latest_date.strftime('%d %b %Y')

# ✅ Filter latest date by sidebar
data_latest_day = dwh_data[dwh_data["datetime"].dt.date == latest_date]

filtered_hourly = data_latest_day.copy()
if selected_region != "ทั้งหมด":
    filtered_hourly = filtered_hourly[filtered_hourly["region"] == selected_region]
if selected_state != "ทั้งหมด" and selected_state != "โปรดเลือกภูมิภาคก่อน":
    filtered_hourly = filtered_hourly[filtered_hourly["state"] == selected_state]
if selected_city != "ทั้งหมด" and selected_city != "โปรดเลือกจังหวัดก่อน":
    filtered_hourly = filtered_hourly[filtered_hourly["city"] == selected_city]

# ✅ เลือกเฉพาะคอลัมน์ที่เกี่ยวข้อง
aqi_line_data = filtered_hourly[["datetime", "city", "aqius", "aqicn"]].sort_values("datetime")
temp_line_data = filtered_hourly[["datetime", "city", "temperature"]].sort_values("datetime")
humid_line_data = filtered_hourly[["datetime", "city", "humidity"]].sort_values("datetime")

# ✅ ตัวช่วยชื่อสถานที่
chart_location = get_chart_location_label(selected_region, selected_state, selected_city)

# ✅ กรณี 1: เลือกเมือง
if selected_city != "ทั้งหมด" and selected_city != "โปรดเลือกจังหวัดก่อน":
    fig_line = px.line(
        aqi_line_data,
        x="datetime",
        y="aqius",
        title=f"AQI (US) รายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"aqius": "ค่า AQI (US)", "datetime": "เวลา"},
        markers=True
    )
    fig_temp = px.line(
        temp_line_data,
        x="datetime",
        y="temperature",
        title=f"อุณหภูมิ (°C) รายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"temperature": "อุณหภูมิ (°C)", "datetime": "เวลา"},
        markers=True
    )
    fig_humid = px.line(
        humid_line_data,
        x="datetime",
        y="humidity",
        title=f"ความชื้น (%) รายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"humidity": "ความชื้น (%)", "datetime": "เวลา"},
        markers=True
    )

# ✅ กรณี 2: เลือกจังหวัด
elif selected_state != "ทั้งหมด" and selected_state != "โปรดเลือกภูมิภาคก่อน":
    avg_hourly = aqi_line_data.groupby("datetime")[["aqius"]].mean().reset_index()
    fig_line = px.line(
        avg_hourly,
        x="datetime",
        y="aqius",
        title=f"AQI (US) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"aqius": "ค่า AQI (US)", "datetime": "เวลา"},
        markers=True
    )
    avg_temp = temp_line_data.groupby("datetime")[["temperature"]].mean().reset_index()
    fig_temp = px.line(
        avg_temp,
        x="datetime",
        y="temperature",
        title=f"อุณหภูมิ (°C) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"temperature": "อุณหภูมิ (°C)", "datetime": "เวลา"},
        markers=True
    )
    avg_humid = humid_line_data.groupby("datetime")[["humidity"]].mean().reset_index()
    fig_humid = px.line(
        avg_humid,
        x="datetime",
        y="humidity",
        title=f"ความชื้น (%) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"humidity": "ความชื้น (%)", "datetime": "เวลา"},
        markers=True
    )

# ✅ กรณี 3: เลือกภูมิภาค
elif selected_region != "ทั้งหมด":
    avg_hourly = aqi_line_data.groupby("datetime")[["aqius"]].mean().reset_index()
    fig_line = px.line(
        avg_hourly,
        x="datetime",
        y="aqius",
        title=f"AQI (US) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"aqius": "ค่า AQI (US)", "datetime": "เวลา"},
        markers=True
    )
    avg_temp = temp_line_data.groupby("datetime")[["temperature"]].mean().reset_index()
    fig_temp = px.line(
        avg_temp,
        x="datetime",
        y="temperature",
        title=f"อุณหภูมิ (°C) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"temperature": "อุณหภูมิ (°C)", "datetime": "เวลา"},
        markers=True
    )
    avg_humid = humid_line_data.groupby("datetime")[["humidity"]].mean().reset_index()
    fig_humid = px.line(
        avg_humid,
        x="datetime",
        y="humidity",
        title=f"ความชื้น (%) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"humidity": "ความชื้น (%)", "datetime": "เวลา"},
        markers=True
    )

# ✅ กรณี 4: ไม่เลือกอะไรเลย (ทั่วประเทศ)
else:
    avg_hourly = aqi_line_data.groupby("datetime")[["aqius"]].mean().reset_index()
    fig_line = px.line(
        avg_hourly,
        x="datetime",
        y="aqius",
        title=f"AQI (US) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"aqius": "ค่า AQI (US)", "datetime": "เวลา"},
        markers=True
    )
    avg_temp = temp_line_data.groupby("datetime")[["temperature"]].mean().reset_index()
    fig_temp = px.line(
        avg_temp,
        x="datetime",
        y="temperature",
        title=f"อุณหภูมิ (°C) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"temperature": "อุณหภูมิ (°C)", "datetime": "เวลา"},
        markers=True
    )
    avg_humid = humid_line_data.groupby("datetime")[["humidity"]].mean().reset_index()
    fig_humid = px.line(
        avg_humid,
        x="datetime",
        y="humidity",
        title=f"ความชื้น (%) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"humidity": "ความชื้น (%)", "datetime": "เวลา"},
        markers=True
    )


# ✅ ปรับ layout เพิ่มเติม (optional)
fig_line.update_layout(
    xaxis_tickformat="%H:%M",
    yaxis_tickformat=".2f",
    hovermode="x unified"
)

# ✅ แสดงกราฟ
st.plotly_chart(fig_line, use_container_width=True)
st.plotly_chart(fig_temp, use_container_width=True)
st.plotly_chart(fig_humid, use_container_width=True)

# ✅ Select columns and sort
hourly_view = filtered_hourly[[
    "datetime", "region", "state", "city", "aqius", "aqicn", "mainus", "maincn", "temperature", "humidity"
]].sort_values(by="datetime", ascending=False)

# ✅ Show table
with st.expander("📊 ตารางข้อมูล AQI รายชั่วโมง"):
    st.dataframe(
        hourly_view.style.format({
            "aqius": "{:.3f}",
            "aqicn": "{:.3f}"
        }),
        use_container_width=True
    )
