import streamlit as st
import pandas as pd
import datetime

# 1. 專業配置
st.set_page_config(page_title="SUZUKI 專業庫存管理", page_icon="🚗", layout="wide")

# 2. 讀取資料
@st.cache_data(ttl=1) # 這裡縮短 TTL，讓更新更快反應
def load_data():
    try:
        data = pd.read_csv("inventory.csv").fillna(0)
        data["年份"] = data["年份"].astype(str)
        return data
    except:
        return pd.DataFrame()

df = load_data()

# --- 側邊欄導覽 ---
st.sidebar.title("🛠️ 選單")
mode = st.sidebar.radio("切換模式", ["🔍 庫存查詢", "⚙️ 管理員後台"])

if mode == "🔍 庫存查詢":
    st.markdown("<h1 style='text-align: center; color: #003366;'>SUZUKI 即時庫存查詢</h1>", unsafe_allow_html=True)
    
    # (保留原本的篩選與顯示邏輯...)
    # 這裡顯示你原本美化過的表格與看板
    st.write("### 📊 目前在庫概覽")
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    # --- 管理員後台 ---
    st.markdown("<h1 style='text-align: center; color: #e11b22;'>⚙️ 管理員後台</h1>", unsafe_allow_html=True)
    
    password = st.text_input("輸入管理密碼", type="password")
    
    if password == "1234": # 你可以自己改密碼
        st.success("身分驗證成功！您現在可以編輯資料。")
        
        st.write("### 📝 快速編輯庫存")
        st.info("直接點擊下方儲存格即可修改數值，修改完後請點擊下方『下載更新檔』並覆蓋 GitHub 檔案。")
        
        # 使用 Data Editor 功能
        edited_df = st.data_editor(
            df, 
            num_rows="dynamic", # 允許你新增整行車型 (按表格下方的 + 號)
            use_container_width=True,
            hide_index=True
        )
        
        # 生成 CSV 下載按鈕
        csv = edited_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="💾 下載最新 inventory.csv",
            data=csv,
            file_name='inventory.csv',
            mime='text/csv',
        )
        
        st.warning("手機操作提示：下載後，請開啟 GitHub 網頁版，將此檔案上傳 (Upload file) 即可完成更新。")

    elif password != "":
        st.error("密碼錯誤，請重新輸入。")
