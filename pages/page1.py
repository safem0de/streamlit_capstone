import streamlit as st
import pandas as pd
import numpy as np

st.title("Dashboard ตัวอย่าง 📊")

value = st.number_input("ใส่ตัวเลข", min_value=0, max_value=100, value=50)
st.write(f"คุณใส่ค่า: {value}")

if st.button("สร้างกราฟ"):
    df = pd.DataFrame(np.random.randn(20, 3), columns=["A", "B", "C"])
    st.bar_chart(df)
