import streamlit as st
import pandas as pd
import os
import urllib.parse

# 1. 頁面基礎設定
st.set_page_config(
    page_title="SUZUKI 行動銷售助理",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 針對手機優化的 CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #003B85; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* 庫存摘要卡片 */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 6px solid #E30613;
        margin-bottom: 10px;
        text-align: center;
    }
    .metric-label { color: #666; font-size: 0.85rem; margin-bottom: 2px; }
    .metric-value { color: #333; font-size: 1.8rem; font-weight: bold; margin: 0; }
    
    /* 型錄卡片樣式 */
    .car-card {
        background-color: white;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        text-align: center;
        border: 1px solid #eee;
    }
    .car-name { color: #003B85; font-weight: bold; font-size: 1.3rem; margin-bottom: 5px; }
    
    /* 專業按鈕樣式 */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #003B85;
        color: white;
        border: none;
        padding: 12px;
        font-weight: bold;
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄選單
st.sidebar.title("🚀 功能選單")
menu = st.sidebar.radio("切換頁面：", ["📊 庫存看板", "📖 數位產品型錄"])

# GitHub 原始檔案基礎路徑 (確保能抓到您的檔案)
GITHUB_USER = "subarudms"
REPO_NAME = "suzuki-inventory"
BASE_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/"

# 4. 邏輯：庫存看板
if menu == "📊 庫存看板":
    st.title("專業庫存即時看板")
    
    # 摘要數據
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="metric-card"><p class="metric-label">總計在庫</p><p class="metric-value">33 台</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p class="metric-label">可用差額</p><p class="metric-value">12 台</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><p class="metric-label">已配車數</p><p class="metric-value">21 台</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p class="metric-label">領牌總數</p><p class="metric-value">18 台</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 車型庫存詳細清單")
    
    if os.path.exists("inventory.csv"):
        try:
            df = pd.read_csv("inventory.csv")
            st.dataframe(df, use_container_width=True, hide_index=True)
        except:
            st.error("讀取明細失敗。")
    else:
        st.warning("找不到 inventory.csv")

# 5. 邏輯：數位產品型錄 (解決 iPhone 觀看問題)
elif menu == "📖 數位產品型錄":
    # 使用 Session State 記錄選中的車款
    if 'car_choice' not in st.session_state:
        st.session_state.car_choice = None

    if st.session_state.car_choice:
        # 顯示返回按鈕
        if st.button("⬅️ 返回型錄列表"):
            st.session_state.car_choice = None
            st.rerun()
        
        car = st.session_state.car_choice
        st.subheader(f"正在閱讀：{car['name']}")
        
        # 建立 PDF 連結 (GitHub Raw 連結)
        encoded_file = urllib.parse.quote(car['file'])
        pdf_url = f"{BASE_RAW_URL}{encoded_file}"
        
        # 使用 Google PDF Viewer 嵌入，這是解決 iOS 只能看第一頁的最強方案
        viewer_url = f"https://docs.google.com/viewer?url={pdf_url}&embedded=true"
        
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px;">
                <a href="{pdf_url}" target="_blank" style="color: #003B85; text-decoration: none; font-size: 0.9rem;">
                    💡 如果畫面跑不出來，請點此開啟全螢幕原檔
                </a>
            </div>
            <iframe src="{viewer_url}" width="100%" height="700px" style="border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"></iframe>
        """, unsafe_allow_html=True)
        
    else:
        st.title("數位產品型錄")
        st.write("請選擇欲向客戶展示的車型：")

        cars = [
            {"name": "SWIFT", "desc": "城市經典 輕油電", "file": "Swift.pdf"},
            {"name": "JIMNY", "desc": "本格越野精神", "file": "Jimny.pdf"},
            {"name": "VITARA", "desc": "強悍越野實力", "file": "Vitara.pdf"},
            {"name": "S-CROSS", "desc": "大膽自信 SUV", "file": "S-Cross 目錄.pdf"},
            {"name": "e VITARA", "desc": "首款純電 SUV", "file": "E Vitara.pdf"},
            {"name": "CARRY", "desc": "拼大生意首選", "file": "Carry.pdf"},
        ]

        cols = st.columns(2)
        for i, car in enumerate(cars):
            with cols[i % 2]:
                st.markdown(f"""
                    <div class="car-card">
                        <div class="car-name">{car['name']}</div>
                        <div style="font-size: 0.8rem; color: #888; margin-bottom: 10px;">{car['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"查看型錄", key=f"btn_{car['name']}"):
                    st.session_state.car_choice = car
                    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("iPhone 17 Pro Max 專業優化版")