import platform
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
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
if connection_str("aqi_database")["status"] == "ok" and connection_str("aqi_datawarehouse")["status"] == "ok":
    conn_str_db = str(connection_str("aqi_database")["data"])
    conn_str_dwh = str(connection_str("aqi_datawarehouse")["data"])
    # print(conn_str_db)
    data = fetch_data(conn_str_db, str("SELECT * FROM air_quality_raw")) # Change to dwh data
    dim_location = fetch_data(conn_str_dwh, "SELECT * FROM dim_location")
    dim_time = fetch_data(conn_str_dwh, "SELECT * FROM dim_time") # Scope for Weekly show
    fact_air = fetch_data(conn_str_dwh, "SELECT * FROM fact_air_quality") # create view for simple
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
    dim_location = pd.read_csv("backup_data\\dim_location_202503292133.csv")
    dim_time = pd.read_csv("backup_data\\dim_time_202503292134.csv")
    fact_air = pd.read_csv("backup_data\\fact_air_quality_202503292134.csv")

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
dwh_data = pd.merge(fact_air, dim_location, on="location_id", how="inner")
dwh_data["datetime"] = pd.to_datetime(dwh_data["time_id"].astype(str), format="%Y%m%d%H")

dwh_data["date_str"] = dwh_data["time_id"].astype(str).str[:8]  # ตัดเฉพาะ YYYYMMDD
dwh_data["date"] = pd.to_datetime(dwh_data["date_str"], format="%Y%m%d").dt.date
print(dwh_data.head(5))

latest_date = dwh_data["date"].max()
print("latest:",latest_date)
str_latest_date = latest_date.strftime('%d %b %Y')

start_date = latest_date - pd.Timedelta(days=6)
print("start:",start_date)
# ✅ Filter latest date by sidebar
weekly_data = dwh_data[(dwh_data["date"] >= start_date) & (dwh_data["date"] <= latest_date)]
print(weekly_data.head(5))

filtered_daily = weekly_data.copy()
if selected_region != "ทั้งหมด":
    filtered_daily = filtered_daily[filtered_daily["region"] == selected_region]
if selected_state != "ทั้งหมด" and selected_state != "โปรดเลือกภูมิภาคก่อน":
    filtered_daily = filtered_daily[filtered_daily["state"] == selected_state]
if selected_city != "ทั้งหมด" and selected_city != "โปรดเลือกจังหวัดก่อน":
    filtered_daily = filtered_daily[filtered_daily["city"] == selected_city]

# ✅ เลือกเฉพาะคอลัมน์ที่เกี่ยวข้อง
aqi_line_data = filtered_daily[["date", "city", "aqius", "aqicn"]].sort_values("date")
temp_line_data = filtered_daily[["date", "city", "temperature"]].sort_values("date")
humid_line_data = filtered_daily[["date", "city", "humidity"]].sort_values("date")

# ✅ ตัวช่วยชื่อสถานที่
chart_location = get_chart_location_label(selected_region, selected_state, selected_city)

# ✅ กรณี 1: เลือกเมือง
if selected_city != "ทั้งหมด" and selected_city != "โปรดเลือกจังหวัดก่อน":
    fig_line = px.line(
        aqi_line_data,
        x="date",
        y="aqius",
        title=f"AQI (US) รายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"aqius": "ค่า AQI (US)", "date": "วันที่"},
        markers=True
    )
    fig_temp = px.line(
        temp_line_data,
        x="date",
        y="temperature",
        title=f"อุณหภูมิ (°C) รายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"temperature": "อุณหภูมิ (°C)", "date": "วันที่"},
        markers=True
    )
    fig_humid = px.line(
        humid_line_data,
        x="date",
        y="humidity",
        title=f"ความชื้น (%) รายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"humidity": "ความชื้น (%)", "date": "วันที่"},
        markers=True
    )
# ✅ กรณี 2: เลือกจังหวัด
elif selected_state != "ทั้งหมด" and selected_state != "โปรดเลือกภูมิภาคก่อน":
    avg_hourly = aqi_line_data.groupby("datetime")[["aqius"]].mean().reset_index()
    fig_line = px.line(
        avg_hourly,
        x="date",
        y="aqius",
        title=f"AQI (US) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"aqius": "ค่า AQI (US)", "date": "วันที่"},
        markers=True
    )
    avg_temp = temp_line_data.groupby("datetime")[["temperature"]].mean().reset_index()
    fig_temp = px.line(
        avg_temp,
        x="date",
        y="temperature",
        title=f"อุณหภูมิ (°C) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"temperature": "อุณหภูมิ (°C)", "date": "วันที่"},
        markers=True
    )
    avg_humid = humid_line_data.groupby("datetime")[["humidity"]].mean().reset_index()
    fig_humid = px.line(
        avg_humid,
        x="date",
        y="humidity",
        title=f"ความชื้น (%) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"humidity": "ความชื้น (%)", "date": "วันที่"},
        markers=True
    )
# ✅ กรณี 3: เลือกภูมิภาค
elif selected_region != "ทั้งหมด":
    avg_hourly = aqi_line_data.groupby("datetime")[["aqius"]].mean().reset_index()
    fig_line = px.line(
        avg_hourly,
        x="date",
        y="aqius",
        title=f"AQI (US) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"aqius": "ค่า AQI (US)", "date": "วันที่"},
        markers=True
    )
    avg_temp = temp_line_data.groupby("datetime")[["temperature"]].mean().reset_index()
    fig_temp = px.line(
        avg_temp,
        x="date",
        y="temperature",
        title=f"อุณหภูมิ (°C) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"temperature": "อุณหภูมิ (°C)", "date": "วันที่"},
        markers=True
    )
    avg_humid = humid_line_data.groupby("date")[["humidity"]].mean().reset_index()
    fig_humid = px.line(
        avg_humid,
        x="date",
        y="humidity",
        title=f"ความชื้น (%) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"humidity": "ความชื้น (%)", "date": "วันที่"},
        markers=True
    )
# ✅ กรณี 4: ไม่เลือกอะไรเลย (ทั่วประเทศ)
else:
    avg_hourly = aqi_line_data.groupby("date")[["aqius"]].mean().reset_index()
    fig_line = px.line(
        avg_hourly,
        x="date",
        y="aqius",
        title=f"AQI (US) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"aqius": "ค่า AQI (US)", "date": "วันที่"},
        markers=True
    )
    avg_temp = temp_line_data.groupby("date")[["temperature"]].mean().reset_index()
    fig_temp = px.line(
        avg_temp,
        x="date",
        y="temperature",
        title=f"อุณหภูมิ (°C) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"temperature": "อุณหภูมิ (°C)", "date": "วันที่"},
        markers=True
    )
    avg_humid = humid_line_data.groupby("date")[["humidity"]].mean().reset_index()
    fig_humid = px.line(
        avg_humid,
        x="date",
        y="humidity",
        title=f"ความชื้น (%) เฉลี่ยรายชั่วโมง — {chart_location} ({latest_date.strftime('%d %b %Y')})",
        labels={"humidity": "ความชื้น (%)", "date": "วันที่"},
        markers=True
    )


# ✅ ปรับ layout เพิ่มเติม (optional)
fig_line.update_layout(
    xaxis_tickformat="%d %b \n(%a)", # %d = วันที่ (01–31), %b = ชื่อเดือนแบบย่อ (Jan–Dec / ม.ค.–ธ.ค.), %B = ชื่อเดือนเต็ม (January / March / ฯลฯ), %A = ชื่อวันเต็ม (Monday), %a = ชื่อวันย่อ (Mon)
    xaxis=dict(tickmode="linear"), # เพื่อจัดช่วงวันที่ให้แน่นอน
    yaxis_tickformat=".2f",
    hovermode="x unified"
)
fig_temp.update_layout(
    xaxis_tickformat="%d %b \n(%a)",
    xaxis=dict(tickmode="linear"),
    yaxis_tickformat=".2f",
    hovermode="x unified"
)
fig_humid.update_layout(
    xaxis_tickformat="%d %b \n(%a)",
    xaxis=dict(tickmode="linear"),
    yaxis_tickformat=".2f",
    hovermode="x unified"
)

# ✅ แสดงกราฟ
st.plotly_chart(fig_line, use_container_width=True)
st.plotly_chart(fig_temp, use_container_width=True)
st.plotly_chart(fig_humid, use_container_width=True)

# ✅ Select columns and sort
daily_view = filtered_daily[[
    "date", "region", "state", "city", "aqius", "aqicn", "mainus", "maincn", "temperature", "humidity"
]].sort_values(by="date", ascending=False)

# ✅ Show table
with st.expander("📊 ตารางข้อมูล AQI รายวัน"):
    st.dataframe(
        daily_view.style.format({
            "aqius": "{:.3f}",
            "aqicn": "{:.3f}"
        }),
        use_container_width=True
    )

# คำนวณ AQI (US) เฉลี่ยสำหรับแต่ละจังหวัด
province_aqi = dwh_data.groupby("state")[["aqius", "aqicn"]].mean().reset_index()

# ปัดทศนิยม 3 ตำแหน่ง
province_aqi["aqius"] = province_aqi["aqius"].round(3)
province_aqi["aqicn"] = province_aqi["aqicn"].round(3)

# เรียงลำดับ AQI จากมากไปน้อย
top_10_best = province_aqi.sort_values(by="aqius", ascending=True).head(10)
top_10_worst = province_aqi.sort_values(by="aqius", ascending=False).head(10)

top_10_best["aqius_text"] = top_10_best["aqius"].apply(lambda x: f"{x:.3f}")
top_10_worst["aqius_text"] = top_10_worst["aqius"].apply(lambda x: f"{x:.3f}")

# Bar Chart สำหรับ Top 10 จังหวัดที่ AQI ดีที่สุด
fig_best = px.bar(
    top_10_best,
    x="state",
    y="aqius",
    title=f"Top 10 จังหวัด AQI ดีที่สุด (US) — เฉลี่ยรายสัปดาห์\nช่วง {start_date.strftime('%d %b')} - {latest_date.strftime('%d %b %Y')}",
    labels={"aqius": "ค่า AQI (US)", "state": "จังหวัด"},
    color="aqius",
    color_continuous_scale="Viridis",
    text="aqius_text"
)

fig_best.update_traces(texttemplate='%{text}', textposition='outside')
fig_best.update_layout(yaxis_tickformat=".3f", margin=dict(l=80, r=20, t=40, b=20))

# Bar Chart สำหรับ Top 10 จังหวัดที่ AQI แย่ที่สุด
fig_worst = px.bar(
    top_10_worst,
    x="state",
    y="aqius",
    title=f"Top 10 จังหวัด AQI แย่ที่สุด (US) — เฉลี่ยรายสัปดาห์\nช่วง {start_date.strftime('%d %b')} - {latest_date.strftime('%d %b %Y')}",
    labels={"aqius": "ค่า AQI (US)", "state": "จังหวัด"},
    color="aqius",
    color_continuous_scale="Reds",
    text="aqius_text"
)

fig_worst.update_traces(texttemplate='%{text}', textposition='outside')
fig_worst.update_layout(yaxis_tickformat=".3f", margin=dict(l=80, r=20, t=40, b=20))

# แสดงกราฟ
st.plotly_chart(fig_best, use_container_width=True)
show_responsive_table(top_10_best[["state", "aqius", "aqicn"]].style.format({"aqius": "{:.3f}", "aqicn": "{:.3f}"}),"📋 คลิกเพื่อดูตารางจังหวัดที่ AQI ดีที่สุด")
    
st.markdown("---")

st.plotly_chart(fig_worst, use_container_width=True)
show_responsive_table(top_10_worst[["state", "aqius", "aqicn"]].style.format({"aqius": "{:.3f}", "aqicn": "{:.3f}"}),"📋 คลิกเพื่อดูตารางจังหวัดที่ AQI แย่ที่สุด")

st.write("---")