import folium
import pandas as pd
import platform
from sqlalchemy import create_engine
import streamlit as st
from streamlit_folium import folium_static
from components.sidebar import hide_sidebar_nav, create_sidebar
from services.data_loader import connection_str, fetch_data
from streamlit.components.v1 import html

# ตั้งค่าเริ่มต้นของแอป (รวมถึง Title และ Favicon)
st.set_page_config(
    page_title="Homepage",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded" # "expanded", "collapsed", or "auto"
)

# ✅ ซ่อน Sidebar Menu ด้านบน
hide_sidebar_nav()

# ✅ สร้าง Sidebar Menu
create_sidebar()

data = pd.DataFrame
if connection_str("aqi_database")["status"] == "ok":
    conn_str = str(connection_str("aqi_database")["data"])
    print(conn_str)
    data = fetch_data(conn_str, str("SELECT * FROM vw_air_quality_latest"))
elif platform.system() == "Windows":
    print("Running on Windows")
    data = pd.read_csv("backup_data\\air_quality_raw_202503202336.csv")
else:
    print("Running on Mac or Linux")
    data = pd.read_csv("backup_data/air_quality_raw_202503202336.csv")

# สร้างแผนที่
# map_center = [13.7563, 100.5018]
map_center = [12.5, 100.5]
m = folium.Map(location=map_center, zoom_start=6.1)

data.columns = data.columns.str.lower()
print(data.head())

data['timestamp'] = pd.to_datetime(data['timestamp'])

# ✅ ดึงข้อมูลล่าสุดสำหรับแต่ละ location (lat, lon)
latest_data = (
    data.sort_values(by="timestamp", ascending=False)
        .dropna(subset=["latitude", "longitude", "aqius"])
        .drop_duplicates(subset=["latitude", "longitude"])
)

# ✅ เลือกเฉพาะคอลัมน์ที่ต้องการแสดง
location_data = latest_data[["city", "latitude", "longitude", "aqius", "timestamp"]]
print(location_data.head())
print(len(location_data))

# เพิ่ม marker
# folium.Marker([13.7563, 100.5018], popup="Bangkok AQI: 75", icon=folium.Icon(color="red")).add_to(m)
for _, row in location_data.iterrows():
    city = row["city"]
    lat = row["latitude"]
    lon = row["longitude"]
    aqi = row["aqius"]

    # กำหนดสีตามระดับ AQI (เพิ่มเติมได้)
    if aqi <= 50:
        color = "green"
    elif aqi <= 100:
        color = "orange"
    else:
        color = "red"

    folium.Marker(
        location=[lon, lat],
        popup=f"{city}<br>AQI: {aqi}",
        icon=folium.Icon(color=color)
    ).add_to(m)

# แสดงแผนที่ใน Streamlit
st.title("Air Quality Map - By 67130503(NW)")
# folium_static(m)
html(m.get_root().render(), height=900)
