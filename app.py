import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Vacancy Dashboard 2026", layout="wide")

# หัวข้อหลัก
st.title("📊 HR Vacancy Dashboard 2026")
st.markdown("Dashboard แสดงภาพรวมตำแหน่งงานว่างจากไฟล์ ALL_AREA")

# 1. โหลดข้อมูล
@st.cache_data
def load_data():
    file_name = 'Vacancy File-Store&Area Hr 2026.xlsx - ALL_AREA.csv'
    try:
        df = pd.read_csv(file_name)
        # แปลงวันที่ถ้ามีคอลัมน์วันที่
        if 'วันที่แจ้ง' in df.columns:
             df['วันที่แจ้ง'] = pd.to_datetime(df['วันที่แจ้ง'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error(f"ไม่พบไฟล์ {file_name} กรุณาวางไฟล์ไว้โฟลเดอร์เดียวกับโปรแกรม")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 2. Sidebar สำหรับ Filter
    st.sidebar.header("🔍 ตัวเลือกการกรอง (Filter)")
    
    # Filter: Area
    area_options = ['All'] + sorted(df['Area'].unique().tolist())
    selected_area = st.sidebar.selectbox('เลือก Area:', area_options)
    
    # Filter: Recruiter
    recruiter_options = ['All'] + sorted(df['Recruiter'].unique().tolist())
    selected_recruiter = st.sidebar.selectbox('เลือก Recruiter:', recruiter_options)

    # Filter: Status
    status_options = ['All'] + sorted(df['Sta_Area HR'].unique().tolist())
    selected_status = st.sidebar.selectbox('เลือกสถานะ (Status):', status_options)

    # การกรองข้อมูล
    filtered_df = df.copy()
    if selected_area != 'All':
        filtered_df = filtered_df[filtered_df['Area'] == selected_area]
    if selected_recruiter != 'All':
        filtered_df = filtered_df[filtered_df['Recruiter'] == selected_recruiter]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Sta_Area HR'] == selected_status]

    # 3. แสดง Metrics หลัก (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนตำแหน่งงานทั้งหมด (Total)", f"{len(filtered_df)} ตำแหน่ง")
    col2.metric("จำนวนสาขา (Stores)", f"{filtered_df['ST Name'].nunique()} สาขา")
    col3.metric("จำนวนตำแหน่งว่าง (Vacant Only)", f"{len(filtered_df[filtered_df['Sta_Area HR']=='Vacant'])} ตำแหน่ง")

    st.markdown("---")

    # 4. สร้างกราฟ (Charts)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📌 จำนวนตำแหน่งงานแยกตามสถานะ (Status)")
        fig_status = px.pie(filtered_df, names='Sta_Area HR', title='สัดส่วนสถานะ (Status Distribution)', hole=0.4)
        st.plotly_chart(fig_status, use_container_width=True)

    with col_chart2:
        st.subheader("👤 จำนวนงานที่ดูแลโดย Recruiter")
        recruit_count = filtered_df['Recruiter'].value_counts().reset_index()
        recruit_count.columns = ['Recruiter', 'Count']
        fig_recruit = px.bar(recruit_count, x='Recruiter', y='Count', color='Recruiter', text='Count', title='Workload per Recruiter')
        st.plotly_chart(fig_recruit, use_container_width=True)

    # กราฟแท่งแนวนอน Top 10 Positions
    st.subheader("🏆 Top 10 ตำแหน่งที่เปิดรับมากที่สุด")
    pos_count = filtered_df['Position'].value_counts().head(10).reset_index()
    pos_count.columns = ['Position', 'Count']
    fig_pos = px.bar(pos_count, x='Count', y='Position', orientation='h', title='Top 10 Positions', color='Count', text='Count')
    fig_pos.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_pos, use_container_width=True)

    # 5. แสดงข้อมูลตาราง
    st.markdown("---")
    st.subheader("📋 รายละเอียดข้อมูล (Data View)")
    st.dataframe(filtered_df)

else:
    st.warning("กรุณาตรวจสอบชื่อไฟล์ CSV ให้ถูกต้อง")
