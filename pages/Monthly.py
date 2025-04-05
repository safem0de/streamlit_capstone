import platform
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from components.sidebar import *
from services.data_loader import *
from utils.helpers import *
import plotly.express as px

st.set_page_config(
    page_title="Monthly AQI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded" # "expanded", "collapsed", or "auto"
)

# ✅ สร้าง Sidebar Menu
create_sidebar()

# ตั้งค่าการเชื่อมต่อกับ PostgreSQL ถ้าไม่ได้ไปใช้ file backup
# data = pd.DataFrame
if connection_str("aqi_database")["status"] == "ok" and connection_str("aqi_datawarehouse")["status"] == "ok":
    conn_str_dwh = str(connection_str("aqi_datawarehouse")["data"])
    dim_location = fetch_data(conn_str_dwh, "SELECT * FROM dim_location")
    dim_time = fetch_data(conn_str_dwh, "SELECT * FROM dim_time")           # Scope for Weekly show
    fact_air = fetch_data(conn_str_dwh, "SELECT * FROM fact_air_quality")   # create view for simple
elif platform.system() == "Windows":
    print("📱 Running on Windows")
    dim_location = pd.read_csv("backup_data\\dim_location_202503292133.csv")
    dim_time = pd.read_csv("backup_data\\dim_time_202503292134.csv")
    fact_air = pd.read_csv("backup_data\\fact_air_quality_202503292134.csv")
else:
    dim_location = pd.read_csv("backup_data\\dim_location_202503292133.csv")
    dim_time = pd.read_csv("backup_data\\dim_time_202503292134.csv")
    fact_air = pd.read_csv("backup_data\\fact_air_quality_202503292134.csv")

st.title("Dashboard AQI Monthly 📊")

# Join Fact Table กับ Location Table
dwh_data = pd.merge(fact_air, dim_location, on="location_id", how="inner")
dwh_data = pd.merge(dwh_data, dim_time, on="time_id", how="inner")
dwh_data["datetime"] = pd.to_datetime(dwh_data["time_id"].astype(str), format="%Y%m%d%H")
dwh_data["date_str"] = dwh_data["time_id"].astype(str).str[:8]  # ตัดเฉพาะ YYYYMMDD
dwh_data["date"] = pd.to_datetime(dwh_data["date_str"], format="%Y%m%d").dt.date
dwh_data["year"] = dwh_data["datetime"].apply(lambda d: d.isocalendar()[0])
dwh_data["month_name"] = dwh_data["datetime"].dt.month_name()

# # สร้าง DataFrame สำหรับ month info
date_df = pd.DataFrame({"date": pd.date_range(start=dwh_data["date"].min(), end=dwh_data["date"].max())})
date_df["year"] = date_df["date"].apply(lambda d: d.isocalendar()[0])
# date_df["month_name"] = date_df["date"].dt.month_name()
# print(date_df.head(5))

# # group ตาม year + month
monthly_group = (
    date_df.groupby(["year"])["date"]
    .agg(["min", "max"])
    .reset_index()
)

monthly_group["label"] = monthly_group.apply(
    lambda row: f"{row['year']} : {row['min'].strftime('%b')} - {row['max'].strftime('%b %Y')}", axis=1
)
# print(monthly_group)

# Sidebar Filters
st.sidebar.header("🔎 ตัวกรองข้อมูล")

# 0. ให้เลือก label
all_labels = monthly_group["label"].tolist()
latest_label = monthly_group.sort_values(["year"], ascending=[False])["label"].iloc[0]

selected_month_label = st.sidebar.selectbox(
    "เลือกปี (Year)",
    all_labels,
    index=all_labels.index(latest_label)
)

# ✅ 1. เลือก Region
region_options = ["ทั้งหมด"] + sorted(dim_location["region"].dropna().unique())
selected_region = st.sidebar.selectbox("เลือกภูมิภาค", region_options)

# ✅ 2. State Dropdown (ถ้ายังไม่เลือก Region -> ปิด Dropdown)
state_placeholder = st.sidebar.empty()

if selected_region == "ทั้งหมด":
    selected_state = state_placeholder.selectbox("เลือกจังหวัด", ["โปรดเลือกภูมิภาคก่อน"], disabled=True)
else:
    state_options = ["ทั้งหมด"] + sorted(dim_location[dim_location["region"] == selected_region]["state"].dropna().unique())
    selected_state = state_placeholder.selectbox("เลือกจังหวัด", state_options)

# ✅ 3. City Dropdown (ถ้ายังไม่เลือก State -> ปิด Dropdown)
city_placeholder = st.sidebar.empty()

if selected_state == "ทั้งหมด" or selected_state == "โปรดเลือกภูมิภาคก่อน":
    selected_city = city_placeholder.selectbox("เลือกอำเภอ/เขต", ["โปรดเลือกจังหวัดก่อน"], disabled=True)
else:
    city_options = ["ทั้งหมด"] + sorted(dim_location[dim_location["state"] == selected_state]["city"].dropna().unique())
    selected_city = city_placeholder.selectbox("เลือกอำเภอ/เขต", city_options)

# ✅ แสดงค่าที่เลือก
st.sidebar.write(f"📆 Week: {selected_month_label}")
st.sidebar.write(f"🌍 Region: {selected_region}")
st.sidebar.write(f"🏙️ State: {selected_state}")
st.sidebar.write(f"🏘️ City: {selected_city}")


selected_row = monthly_group[monthly_group["label"] == selected_month_label].iloc[0]
selected_year = selected_row["year"]

monthly_data = dwh_data[
    (dwh_data["year"] == selected_year)
]


filtered_monthly = monthly_data.copy()
if selected_region != "ทั้งหมด":
    filtered_monthly = filtered_monthly[filtered_monthly["region"] == selected_region]
if selected_state != "ทั้งหมด" and selected_state != "โปรดเลือกภูมิภาคก่อน":
    filtered_monthly = filtered_monthly[filtered_monthly["state"] == selected_state]
if selected_city != "ทั้งหมด" and selected_city != "โปรดเลือกจังหวัดก่อน":
    filtered_monthly = filtered_monthly[filtered_monthly["city"] == selected_city]

filtered_monthly["month"] = pd.to_datetime(filtered_monthly["date"]).dt.month
filtered_monthly["month_name"] = pd.to_datetime(filtered_monthly["date"]).dt.month_name()

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

filtered_monthly["month_name"] = pd.Categorical(
    filtered_monthly["month_name"].str.strip(),
    categories=month_order,
    ordered=True
)

# ✅ เลือกเฉพาะคอลัมน์ที่เกี่ยวข้อง
aqi_line_data = filtered_monthly[["month_name", "city", "aqius", "aqicn"]].sort_values("month_name")
temp_line_data = filtered_monthly[["month_name", "city", "temperature"]].sort_values("month_name")
humid_line_data = filtered_monthly[["month_name", "city", "humidity"]].sort_values("month_name")

# ✅ ตัวช่วยชื่อสถานที่
chart_location = get_chart_location_label(selected_region, selected_state, selected_city)
# 🔁 Group ค่าเฉลี่ยรายเดือน
avg_aqi = aqi_line_data.groupby("month_name")[["aqius"]].mean().reset_index()
avg_temp = temp_line_data.groupby("month_name")[["temperature"]].mean().reset_index()
avg_humid = humid_line_data.groupby("month_name")[["humidity"]].mean().reset_index()

# ✅ สร้างกราฟ
fig_line = px.line(
    avg_aqi,
    x="month_name",
    y="aqius",
    title=f"AQI (US) เฉลี่ยรายเดือน — {chart_location} ({selected_month_label})",
    labels={"aqius": "ค่า AQI (US)", "month_name": "เดือน"},
    markers=True
)

fig_temp = px.line(
    avg_temp,
    x="month_name",
    y="temperature",
    title=f"อุณหภูมิ (°C) เฉลี่ยรายเดือน — {chart_location} ({selected_month_label})",
    labels={"temperature": "อุณหภูมิ (°C)", "month_name": "เดือน"},
    markers=True
)

fig_humid = px.line(
    avg_humid,
    x="month_name",
    y="humidity",
    title=f"ความชื้น (%) เฉลี่ยรายเดือน — {chart_location} ({selected_month_label})",
    labels={"humidity": "ความชื้น (%)", "month_name": "เดือน"},
    markers=True
)


# ✅ ปรับ layout เพิ่มเติม (optional)
fig_line.update_layout(
    xaxis_tickformat="%b", # %d = วันที่ (01–31), %b = ชื่อเดือนแบบย่อ (Jan–Dec / ม.ค.–ธ.ค.), %B = ชื่อเดือนเต็ม (January / March / ฯลฯ), %A = ชื่อวันเต็ม (Monday), %a = ชื่อวันย่อ (Mon)
    xaxis=dict(tickmode="linear"), # เพื่อจัดช่วงวันที่ให้แน่นอน
    yaxis_tickformat=".2f",
    hovermode="x unified"
)
fig_temp.update_layout(
    xaxis_tickformat="%b",
    xaxis=dict(tickmode="linear"),
    yaxis_tickformat=".2f",
    hovermode="x unified"
)
fig_humid.update_layout(
    xaxis_tickformat="%b",
    xaxis=dict(tickmode="linear"),
    yaxis_tickformat=".2f",
    hovermode="x unified"
)

# ✅ แสดงกราฟ
st.plotly_chart(fig_line, use_container_width=True)
st.plotly_chart(fig_temp, use_container_width=True)
st.plotly_chart(fig_humid, use_container_width=True)

# # ✅ Select columns and sort
monthly_view = (
    filtered_monthly
    .dropna(subset=["aqius", "aqicn", "temperature", "humidity"])
    .groupby(["month_name", "region", "state", "city"], observed=True)  # 👈 เพิ่ม observed=True ตรงนี้
    [["aqius", "aqicn", "temperature", "humidity"]]
    .mean()
    .reset_index()
    .sort_values(by=["month_name", "city"], ascending=[False, True])
)


# # ✅ Show table
with st.expander("📊 ตารางข้อมูล AQI รายเดือน"):
    st.dataframe(
        monthly_view.style.format({
            "aqius": "{:.3f}",
            "aqicn": "{:.3f}",
            "temperature" : "{:.3f}",
            "humidity" : "{:.3f}",
        }),
        use_container_width=True
    )

# คำนวณ AQI (US) เฉลี่ยสำหรับแต่ละจังหวัด
province_aqi = filtered_monthly.groupby("state")[["aqius", "aqicn"]].mean().reset_index()

# ปัดทศนิยม 3 ตำแหน่ง
province_aqi["aqius"] = province_aqi["aqius"].round(3)
province_aqi["aqicn"] = province_aqi["aqicn"].round(3)

# เรียงลำดับ AQI จากมากไปน้อย
top_10_best = province_aqi.sort_values(by="aqius", ascending=True).head(10)
top_10_worst = province_aqi.sort_values(by="aqius", ascending=False).head(10)

top_10_best["aqius_text"] = top_10_best["aqius"].apply(lambda x: f"{x:.3f}")
top_10_worst["aqius_text"] = top_10_worst["aqius"].apply(lambda x: f"{x:.3f}")

# Bar Chart สำหรับ Top 10 จังหวัดที่ AQI ดีที่สุด
fig_best = px.bar(
    top_10_best,
    x="state",
    y="aqius",
    title=f"Top 10 จังหวัด AQI ดีที่สุด (US) — เฉลี่ยรายสัปดาห์\nช่วง ({selected_month_label})",
    labels={"aqius": "ค่า AQI (US)", "state": "จังหวัด"},
    color="aqius",
    color_continuous_scale="Viridis",
    text="aqius_text"
)

fig_best.update_traces(texttemplate='%{text}', textposition='outside')
fig_best.update_layout(yaxis_tickformat=".3f", margin=dict(l=80, r=20, t=40, b=20))

# Bar Chart สำหรับ Top 10 จังหวัดที่ AQI แย่ที่สุด
fig_worst = px.bar(
    top_10_worst,
    x="state",
    y="aqius",
    title=f"Top 10 จังหวัด AQI แย่ที่สุด (US) — เฉลี่ยรายสัปดาห์\nช่วง ({selected_month_label})",
    labels={"aqius": "ค่า AQI (US)", "state": "จังหวัด"},
    color="aqius",
    color_continuous_scale="Reds",
    text="aqius_text"
)

fig_worst.update_traces(texttemplate='%{text}', textposition='outside')
fig_worst.update_layout(yaxis_tickformat=".3f", margin=dict(l=80, r=20, t=40, b=20))

# แสดงกราฟ
st.plotly_chart(fig_best, use_container_width=True)
show_responsive_table(top_10_best[["state", "aqius", "aqicn"]].style.format({"aqius": "{:.3f}", "aqicn": "{:.3f}"}),"📋 คลิกเพื่อดูตารางจังหวัดที่ AQI ดีที่สุด")
    
st.markdown("---")

st.plotly_chart(fig_worst, use_container_width=True)
show_responsive_table(top_10_worst[["state", "aqius", "aqicn"]].style.format({"aqius": "{:.3f}", "aqicn": "{:.3f}"}),"📋 คลิกเพื่อดูตารางจังหวัดที่ AQI แย่ที่สุด")

st.write("---")