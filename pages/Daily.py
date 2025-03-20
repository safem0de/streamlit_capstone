import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from components.sidebar import hide_sidebar_nav, create_sidebar

st.set_page_config(
    page_title="Daily AQI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed" # "expanded", "collapsed", or "auto"
)

# ✅ ซ่อน Sidebar Navigation
hide_sidebar_nav()

# ✅ สร้าง Sidebar Menu
create_sidebar()

st.title("Dashboard AQI Daily 📊")

col1, col2, col3 = st.columns([1,1,1])

with col1:
    selected_date = st.date_input("Select a date:", date.today())
    # st.write("Content in column 1")

with col2:
    st.header("Column 2")
    st.write("Content in column 2")

with col3:
    st.header("Column 3")
    st.write("Content in column 3")


if st.button("สร้างกราฟ"):
    df = pd.DataFrame(np.random.randn(20, 3), columns=["A", "B", "C"])
    st.bar_chart(df)