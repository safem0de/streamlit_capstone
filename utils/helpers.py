import datetime
import streamlit as st

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