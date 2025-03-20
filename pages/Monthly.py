import streamlit as st
import pandas as pd
import numpy as np
import streamlit as st
import datetime
from components.sidebar import hide_sidebar_nav, create_sidebar

# ✅ ซ่อน Sidebar Navigation
hide_sidebar_nav()

# ✅ สร้าง Sidebar Menu
create_sidebar()

st.title("Select Month and Year")
st.write("\n")  

# Get the current year and month
current_year = datetime.date.today().year
current_month = datetime.date.today().month

# Month selection
months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
          7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

selected_month = st.selectbox("Select Month", list(months.values()), index=current_month-1)

# Year selection
selected_year = st.number_input("Select Year", min_value=2000, max_value=2100, value=current_year, step=1)

# Show selected month and year
st.write(f"Selected: {selected_month} {selected_year}")
