import streamlit as st

def hide_sidebar_nav():
    """ฟังก์ชันซ่อน Sidebar Navigation"""
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    st.sidebar.page_link("app.py", label="Home")

    st.sidebar.markdown("### 📊 Dashboard")
    st.sidebar.page_link("pages/Daily.py", label="Daily")
    st.sidebar.page_link("pages/Weekly.py", label="Weekly")
    st.sidebar.page_link("pages/Monthly.py", label="Monthly")

    st.sidebar.markdown("### 🌍 Data Reports")
    st.sidebar.page_link("pages/Region.py", label="Region")
    st.sidebar.page_link("pages/_Test.py", label="Test")
    st.sidebar.page_link("pages/_Test2.py", label="Test2")

    st.sidebar.markdown("---")