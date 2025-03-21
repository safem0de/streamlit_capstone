import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from datetime import date
from components.sidebar import hide_sidebar_nav, create_sidebar

st.set_page_config(
    page_title="Region",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded" # "expanded", "collapsed", or "auto"
)

# ✅ ซ่อน Sidebar Navigation
hide_sidebar_nav()

# ✅ สร้าง Sidebar Menu
create_sidebar()

# ตั้งค่าการเชื่อมต่อกับ PostgreSQL
# db_config = {
#     "dbname": "aqi_database",
#     "user": "airflow",
#     "password": "airflow",
#     "host": "localhost",
#     "port": "30524"
# }
# engine = create_engine(f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}")

# # ดึงข้อมูลจาก Database
# data = pd.read_sql("SELECT * FROM air_quality_raw", con=engine)
data = pd.read_csv("backup_data\\air_quality_raw_202503202336.csv")


data.columns = data.columns.str.lower()  # แปลงชื่อคอลัมน์เป็นตัวพิมพ์เล็กทั้งหมด
data['timestamp'] = pd.to_datetime(data['timestamp'])
data = data.sort_values(by="timestamp", ascending=True)

# Sidebar Filters
st.sidebar.header("🔎 ตัวกรองข้อมูล")

# ✅ 1. เลือก Region
region_options = ["ทั้งหมด"] + sorted(data["region"].dropna().unique())
selected_region = st.sidebar.selectbox("เลือกภูมิภาค", region_options)

# ✅ กรองข้อมูลตาม Region ที่เลือก
if selected_region != "ทั้งหมด":
    filtered_data = data[data["region"] == selected_region]
else:
    filtered_data = data  # ใช้ข้อมูลทั้งหมด

# ✅ แสดงค่าที่เลือก
st.title(f"🌍 Air Quality Dashboard - {selected_region}")
st.sidebar.write(f"🌍 Region: {selected_region}")

# 📊 คำนวณค่าเฉลี่ยของตัวแปรที่ต้องการแสดง
average_aqius = round(filtered_data["aqius"].mean(), 3)
average_aqicn = round(filtered_data["aqicn"].mean(), 3)
average_temp = round(filtered_data["temperature"].mean(), 3)
average_pressure = round(filtered_data["pressure"].mean(), 3)
average_humidity = round(filtered_data["humidity"].mean(), 3)
average_wind_speed = round(filtered_data["wind_speed"].mean(), 3)

# ✅ ดึงค่า AQI ล่าสุดและค่าก่อนหน้า
latest_data = filtered_data.iloc[-1]  # แถวล่าสุด
previous_data = filtered_data.iloc[-2] if len(filtered_data) > 1 else filtered_data  # แถวก่อนหน้า

latest_aqius = latest_data["aqius"]
previous_aqius = previous_data["aqius"]
delta_aqius = round((latest_aqius - previous_aqius),3)  # คำนวณ delta

latest_aqicn = latest_data["aqicn"]
previous_aqicn = previous_data["aqicn"]
delta_aqicn = round((latest_aqicn - previous_aqicn),3)

latest_temperature = latest_data["temperature"]
previous_temperature = previous_data["temperature"]
delta_temperature = round((latest_temperature - previous_temperature),3)

latest_pressure = latest_data["pressure"]
previous_pressure = previous_data["pressure"]
delta_pressure = round((latest_pressure - previous_pressure),3)

latest_humidity = latest_data["humidity"]
previous_humidity = previous_data["humidity"]
delta_humidity = round((latest_humidity - previous_humidity),3)

latest_wind_speed = latest_data["wind_speed"]
previous_wind_speed = previous_data["wind_speed"]
delta_wind_speed = round((latest_wind_speed - previous_wind_speed),3)

col1, col2, col3 = st.columns([1,1,1])
with col1:
    st.subheader("💨 ค่าเฉลี่ย AQI (US & CN)") #"normal" (ค่าเริ่มต้น) "inverse" (สลับสีเขียว-แดง) "off" (ปิดการแสดงผล)
    st.metric(label="AQI (US)", value=f"{average_aqius:.3f}", delta=int(delta_aqius), delta_color="inverse")
    st.metric(label="AQI (CN)", value=f"{average_aqicn:.3f}", delta=int(delta_aqicn), delta_color="inverse")

with col2:
    st.subheader("🌡️ ค่าเฉลี่ยสภาพอากาศ")
    st.metric(label="Temperature (°C)", value=f"{average_temp:.3f}", delta=int(delta_temperature), delta_color="inverse")
    st.metric(label="Pressure (hPa)", value=f"{average_pressure:.3f}", delta=int(delta_pressure), delta_color="normal")

with col3:
    st.subheader("💨 ค่าเฉลี่ยความชื้น/ความเร็วลม")
    st.metric(label="Humidity (%)", value=f"{average_humidity:.3f}", delta=int(delta_humidity), delta_color="normal")
    st.metric(label="Wind Speed (m/s)", value=f"{average_wind_speed:.3f}", delta=int(delta_wind_speed), delta_color="normal")

# ✅ กราฟเปรียบเทียบ AQI ระหว่างภูมิภาค (ด้านล่าง col3)
st.subheader("📊 เปรียบเทียบ AQI ระหว่างภูมิภาค") 

# ✅ คำนวณค่าเฉลี่ย AQI ตาม Region
region_aqi_data = round(filtered_data.groupby("region")["aqius"].mean(),3).reset_index()
region_aqi_data = region_aqi_data.sort_values(by="aqius", ascending=False)

num_regions = len(region_aqi_data)

if num_regions > 5:
    _bargap = 0.3
elif 2 <= num_regions <= 5:
    _bargap = 0.5
else:
    _bargap = 0.8
    
# ✅ สร้างกราฟ Plotly Bar Chart
aq_bar_chart = px.bar(region_aqi_data,
                      x="region", y="aqius", color="aqius",
                      title="ค่า AQI เฉลี่ยของแต่ละภูมิภาค",
                      labels={"aqius": "ค่า AQI (US)"},
                      text_auto=True,
                      height=500,
                      width=200)

# ✅ ปรับขนาดแท่งของกราฟ
aq_bar_chart.update_layout(
    xaxis_title="ภูมิภาค",
    yaxis_title="ค่า AQI เฉลี่ย (US)",
    showlegend=False,
    bargap=_bargap,  # ✅ ลดความกว้างระหว่างแท่ง
    bargroupgap=0.1,  # ✅ ลดระยะห่างของกลุ่มแท่ง
    xaxis=dict(categoryorder="total descending")  # ✅ เรียงแท่งจากมากไปน้อย
)

# ✅ แสดงกราฟ
st.plotly_chart(aq_bar_chart, use_container_width=True)