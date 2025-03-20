import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from components.sidebar import hide_sidebar_nav, create_sidebar

# ✅ ซ่อน Sidebar Navigation
hide_sidebar_nav()

# ✅ สร้าง Sidebar Menu
create_sidebar()

# ตั้งค่าการเชื่อมต่อกับ PostgreSQL
db_config = {
    "dbname": "aqi_database",
    "user": "airflow",
    "password": "airflow",
    "host": "localhost",
    "port": "30524"
}

engine = create_engine(f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}")

# ดึงข้อมูลจาก Database
data = pd.read_sql("SELECT * FROM air_quality_raw", con=engine)

data.columns = data.columns.str.lower()  # แปลงชื่อคอลัมน์เป็นตัวพิมพ์เล็กทั้งหมด
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Sidebar Filters
st.sidebar.header("🔎 ตัวกรองข้อมูล")
selected_city = st.sidebar.selectbox("เลือกเมือง", options=["ทั้งหมด"] + list(data["city"].unique()))
selected_state = st.sidebar.selectbox("เลือกจังหวัด/รัฐ", options=["ทั้งหมด"] + list(data["state"].unique()))
selected_region = st.sidebar.selectbox("เลือกภูมิภาค", options=["ทั้งหมด"] + list(data["region"].unique()))

# กรองข้อมูลตามตัวเลือก
if selected_city != "ทั้งหมด":
    data = data[data["city"] == selected_city]
if selected_state != "ทั้งหมด":
    data = data[data["state"] == selected_state]
if selected_region != "ทั้งหมด":
    data = data[data["region"] == selected_region]

# แสดงแผนที่ Choropleth Map (ระดับเมือง/จังหวัด)
st.subheader("🗺 แผนที่คุณภาพอากาศ")
fig_map = px.scatter_mapbox(data, lat="latitude", lon="longitude", color="aqius",
                            size="aqicn", hover_data=["city", "state", "aqius"],
                            zoom=5, mapbox_style="carto-positron")
st.plotly_chart(fig_map)

# กราฟแท่งเปรียบเทียบค่า AQI ของแต่ละเมือง
st.subheader("📊 เปรียบเทียบ AQI ระหว่างเมือง")
aq_bar_chart = px.bar(data.groupby("city")["aqius"].mean().reset_index(),
                      x="city", y="aqius", color="aqius",
                      title="ค่า AQI เฉลี่ยของแต่ละเมือง",
                      labels={"aqius": "ค่า AQI (US)"}, height=500)
st.plotly_chart(aq_bar_chart)

# กราฟเส้นแนวโน้ม AQI และอุณหภูมิ (ใช้ Dual Y-axis)
st.subheader("📈 แนวโน้ม AQI และอุณหภูมิ")
fig = go.Figure()

fig.add_trace(go.Scatter(x=data["timestamp"], y=data["aqius"],
                         mode='lines', name='AQI (US)',
                         line=dict(color='red')))

fig.add_trace(go.Scatter(x=data["timestamp"], y=data["temperature"],
                         mode='lines', name='Temperature (°C)',
                         line=dict(color='blue'), yaxis='y2'))

fig.update_layout(
    title="แนวโน้ม AQI และอุณหภูมิ",
    xaxis_title="timestamp",
    yaxis=dict(title="AQI (US)", tickfont=dict(color="red")),
    yaxis2=dict(title="Temperature (°C)", tickfont=dict(color="blue"),
                overlaying='y', side='right')
)

st.plotly_chart(fig)
