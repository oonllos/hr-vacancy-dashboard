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
    # --- แก้ไขตรงนี้: เปลี่ยนชื่อไฟล์เป็น data.csv ---
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
        # ถ้าอ่านแล้ว Error ภาษาต่างดาว ให้ลองอ่านแบบ TIS-620 (สำหรับไฟล์ภาษาไทยเก่าๆ)
        try:
            df = pd.read_csv(file_name, encoding='tis-620')
            if 'วันที่แจ้ง' in df.columns:
                df['วันที่แจ้ง'] = pd.to_datetime(df['วันที่แจ้ง'], errors='coerce')
            return df
        except:
            return pd.DataFrame()
    except FileNotFoundError:
        st.error(f"ไม่พบไฟล์ {file_name} กรุณาเปลี่ยนชื่อไฟล์ CSV ของคุณเป็น data.csv แล้วอัปโหลดไว้คู่กับ app.py")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 2. Sidebar สำหรับ Filter
    st.sidebar.header("🔍 ตัวเลือกการกรอง (Filter)")
    
    # เช็คว่ามีคอลัมน์ที่ต้องการหรือไม่เพื่อป้องกัน Error
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

    if 'Sta_Area HR' in df.columns:
        status_options = ['All'] + sorted(df['Sta_Area HR'].dropna().unique().tolist())
        selected_status = st.sidebar.selectbox('เลือกสถานะ (Status):', status_options
