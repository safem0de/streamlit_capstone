import folium
import streamlit as st
from streamlit_folium import folium_static

# ตั้งค่าเริ่มต้นของแอป (รวมถึง Title และ Favicon)
st.set_page_config(
    page_title="Homepage",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
    <style>
        section[data-testid="stSidebarNav"] {display: none;},
        @font-face {
            font-family: 'Source Sans Pro';
            src: none;  /* ปิดการโหลดฟอนต์ */
        }
    </style>
""", unsafe_allow_html=True)

# สร้างแผนที่
map_center = [13.7563, 100.5018]
m = folium.Map(location=map_center, zoom_start=6)

# เพิ่ม marker
folium.Marker([13.7563, 100.5018], popup="Bangkok AQI: 75", icon=folium.Icon(color="red")).add_to(m)

# แสดงแผนที่ใน Streamlit
st.title("Air Quality Map")
folium_static(m)
