import streamlit as st

def hide_sidebar_nav():
    """ฟังก์ชันซ่อน Sidebar Navigation"""
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    hide_sidebar_nav()
    st.sidebar.page_link("app.py", label="Home")

    st.sidebar.markdown("### 🕔 Time")
    st.sidebar.page_link("pages/Daily.py", label="Daily (รายวัน)")
    st.sidebar.page_link("pages/Weekly.py", label="Weekly (รายสัปดาห์)")
    st.sidebar.page_link("pages/Monthly.py", label="Monthly (รายเดือน)")

    st.sidebar.markdown("### 🌍 Location")
    st.sidebar.page_link("pages/City.py", label="Region/State/City")

    st.sidebar.markdown("### 📈 Data Quality Report")
    st.sidebar.page_link("pages/DataQuality.py", label="Data Qaulity Report (คุณภาพข้อมูล)")

    st.sidebar.markdown("---")