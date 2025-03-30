import datetime
import streamlit as st
import pandas as pd
from streamlit_javascript import st_javascript

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def make_responsive(text:str, rem:float = 1.3):
    st.markdown(
        f"""
        <div style="
            font-size: {rem}rem;
            font-weight: 600;
            word-wrap: break-word;
            white-space: normal;
            line-height: 1.4;
            ">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

def show_responsive_table(df, title="📋 ดูข้อมูล", ):
    """
    แสดงตารางใน st.expander แบบ responsive:
    - ถ้าหน้าจอกว้าง ใช้ columns จัดกลาง
    - ถ้าหน้าจอเล็ก แสดงเต็มจอ
    - รองรับ styling function ที่ส่งเข้ามา (เช่น df_style)

    Args:
        df (pd.DataFrame): ข้อมูลที่จะแสดง
        title (str): ชื่อหัวข้อของ expander
        style_fn (function, optional): ฟังก์ชันจัด style สำหรับตาราง เช่น df_style(df)
    """
    screen_width = st_javascript("window.innerWidth", key=f"screen_width_{title}") or 1200
    is_mobile = screen_width < 768

    with st.expander(title):
        if is_mobile:
            st.dataframe(df, use_container_width=True)
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.dataframe(df, use_container_width=True)
