import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Vacancy Dashboard 2026", layout="wide")

# หัวข้อหลัก
st.title("📊 HR Vacancy Dashboard 2026")
st.markdown("Dashboard แสดงภาพรวมตำแหน่งงานว่างจากไฟล์ข้อมูล")

# 1. โหลดข้อมูล
@st.cache_data
def load_data():
    # --- ตรวจสอบชื่อไฟล์ให้ตรงกับใน GitHub ของคุณ ---
    file_name = 'data.csv' 
    # ------------------------------------------
    try:
        # ลองอ่านแบบ UTF-8 ก่อน (มาตรฐาน)
        df = pd.read_csv(file_name)
        
        # แปลงวันที่ถ้ามีคอลัมน์วันที่
        if 'วันที่แจ้ง' in df.columns:
             df['วันที่แจ้ง'] = pd.to_datetime(df['วันที่แจ้ง'], errors='coerce')
        return df
    except UnicodeDecodeError:
        # ถ้าอ่านแล้ว Error ภาษาต่างดาว ให้ลองอ่านแบบ TIS-620
        try:
            df = pd.read_csv(file_name, encoding='tis-620')
            if 'วันที่แจ้ง' in df.columns:
                df['วันที่แจ้ง'] = pd.to_datetime(df['วันที่แจ้ง'], errors='coerce')
            return df
        except:
            return pd.DataFrame()
    except FileNotFoundError:
        st.error(f"ไม่พบไฟล์ {file_name} กรุณาตรวจสอบว่าชื่อไฟล์ใน GitHub ตรงกับ '{file_name}' หรือไม่")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 2. Sidebar สำหรับ Filter
    st.sidebar.header("🔍 ตัวเลือกการกรอง (Filter)")
    
    # เช็คว่ามีคอลัมน์ที่ต้องการหรือไม่
    if 'Area' in df.columns:
        area_options = ['All'] + sorted(df['Area'].dropna().unique().tolist())
        selected_area = st.sidebar.selectbox('เลือก Area:', area_options)
    else:
        selected_area = 'All'
    
    if 'Recruiter' in df.columns:
        recruiter_options = ['All'] + sorted(df['Recruiter'].dropna().unique().tolist())
        selected_recruiter = st.sidebar.selectbox('เลือก Recruiter:', recruiter_options)
    else:
        selected_recruiter = 'All'

    # --- จุดที่เคย Error แก้ไขแล้ว ---
    if 'Sta_Area HR' in df.columns:
        status_options = ['All'] + sorted(df['Sta_Area HR'].dropna().unique().tolist())
        selected_status = st.sidebar.selectbox('เลือกสถานะ (Status):', status_options)
    else:
        selected_status = 'All'
    # -----------------------------

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
    
    if 'ST Name' in filtered_df.columns:
        col2.metric("จำนวนสาขา (Stores)", f"{filtered_df['ST Name'].nunique()} สาขา")
    
    if 'Sta_Area HR' in filtered_df.columns:
        col3.metric("จำนวนตำแหน่งว่าง (Vacant Only)", f"{len(filtered_df[filtered_df['Sta_Area HR']=='Vacant'])} ตำแหน่ง")

    st.markdown("---")

    # 4. สร้างกราฟ (Charts)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        if 'Sta_Area HR' in filtered_df.columns:
            st.subheader("📌 จำนวนตำแหน่งงานแยกตามสถานะ (Status)")
            fig_status = px.pie(filtered_df, names='Sta_Area HR', title='สัดส่วนสถานะ (Status Distribution)', hole=0.4)
            st.plotly_chart(fig_status, use_container_width=True)

    with col_chart2:
        if 'Recruiter' in filtered_df.columns:
            st.subheader("👤 จำนวนงานที่ดูแลโดย Recruiter")
            recruit_count = filtered_df['Recruiter'].value_counts().reset_index()
            recruit_count.columns = ['Recruiter', 'Count']
            fig_recruit = px.bar(recruit_count, x='Recruiter', y='Count', color='Recruiter', text='Count', title='Workload per Recruiter')
            st.plotly_chart(fig_recruit, use_container_width=True)

    # กราฟแท่งแนวนอน Top 10 Positions
    if 'Position' in filtered_df.columns:
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
    st.warning("ยังไม่พบข้อมูล: กรุณาตรวจสอบว่าอัปโหลดไฟล์ data.csv แล้วหรือยัง")
