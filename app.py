import streamlit as st
from services.data_loader import load_user_data

# ตั้งค่าเริ่มต้นของแอป (รวมถึง Title และ Favicon)
st.set_page_config(
    page_title="Homepage",
    page_icon="🏠",
    layout="wide"
)

# ซ่อน Sidebar Navigation (ที่มี "app", "page1" โดยอัตโนมัติ)
st.markdown("""
    <style>
        section[data-testid="stSidebarNav"] {display: none;},
        @font-face {
            font-family: 'Source Sans Pro';
            src: none;  /* ปิดการโหลดฟอนต์ */
        }
    </style>
""", unsafe_allow_html=True)

# เปลี่ยนชื่อ App เป็น Homepage
st.title("🏠 Homepage - Streamlit Clean Architecture 🚀")

# โหลดข้อมูล
users = load_user_data()
st.write(users)