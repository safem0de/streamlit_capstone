import platform
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from components.sidebar import hide_sidebar_nav, create_sidebar

# ✅ ซ่อน Sidebar Navigation
hide_sidebar_nav()

# ✅ สร้าง Sidebar Menu
create_sidebar()

# # ตั้งค่าการเชื่อมต่อกับ PostgreSQL
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
if platform.system() == "Windows":
    print("🪟 Running on Windows")
    data = pd.read_csv("backup_data\\air_quality_raw_202503202336.csv")
else:
    data = pd.read_csv("backup_data/air_quality_raw_202503202336.csv")

data.columns = data.columns.str.lower()  # แปลงชื่อคอลัมน์เป็นตัวพิมพ์เล็กทั้งหมด
data['timestamp'] = pd.to_datetime(data['timestamp'])

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