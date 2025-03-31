import platform
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.sidebar import *
from services.data_loader import *
from utils.helpers import *

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
else:
    data = pd.read_csv("backup_data/air_quality_raw_202503202336.csv")

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