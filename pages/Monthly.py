import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st
import datetime, platform
from components.sidebar import *
from services.data_loader import *
from utils.helpers import *

st.set_page_config(
    page_title="Monthly AQI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded" # "expanded", "collapsed", or "auto"
)

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

st.title("Dashboard AQI Monthly 📊") 


