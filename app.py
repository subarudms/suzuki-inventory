import streamlit as st
import pandas as pd
import os

# 1. 設定頁面基礎配置 (iPhone 17 Pro Max 優化)
st.set_page_config(
    page_title="SUZUKI 銷售助理系統",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 加入自定義 CSS 樣式
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #003B85; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* 庫存卡片樣式 */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 5px solid #E30613;
        margin-bottom: 10px;
        text-align: center;
    }
    
    /* 型錄卡片樣式 */
    .car-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        text-align: center;
        border: 1px solid #eee;
    }
    .car-name { color: #003B85; font-weight: bold; font-size: 1.2rem; margin-bottom: 5px; }
    .pdf-button {
        display: block;
        background-color: #003B85;
        color: white !important;
        text-decoration: none;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
        margin-top: 8px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄導覽選單
st.sidebar.title("銷售助理選單")
menu = st.sidebar.radio("請選擇功能：", ["📊 庫存看板與明細", "📖 數位產品型錄"])

# 4. 功能邏輯：庫存即時看板與明細
if menu == "📊 庫存看板與明細":
    st.title("專業庫存即時看板")
    
    # 顯示摘要數據
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="metric-card"><p style="margin:0;color:#666;font-size:0.8rem;">總計在庫</p><h2 style="margin:0;color:#333;">33 台</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p style="margin:0;color:#666;font-size:0.8rem;">可用差額</p><h2 style="margin:0;color:#333;">12 台</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><p style="margin:0;color:#666;font-size:0.8rem;">已配車數</p><h2 style="margin:0;color:#333;">21 台</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p style="margin:0;color:#666;font-size:0.8rem;">領牌總數</p><h2 style="margin:0;color:#333;">18 台</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 車型庫存明細表")
    
    # 讀取庫存 CSV 檔案
    if os.path.exists("inventory.csv"):
        try:
            df = pd.read_csv("inventory.csv")
            # 針對手機優化：自動調整欄位寬度
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"讀取明細時出錯: {e}")
    else:
        st.warning("找不到 inventory.csv 檔案，請確認檔案已上傳至根目錄。")

# 5. 功能邏輯：數位產品型錄
elif menu == "📖 數位產品型錄":
    st.title("數位產品型錄索引")
    st.write("點擊下方按鈕開啟 PDF 目錄")

    cars = [
        {"name": "SWIFT", "desc": "城市經典 輕油電", "file": "Swift.pdf"},
        {"name": "JIMNY", "desc": "本格越野精神", "file": "Jimny.pdf"},
        {"name": "VITARA", "desc": "強悍越野實力", "file": "Vitara.pdf"},
        {"name": "S-CROSS", "desc": "大膽自信 SUV", "file": "S-Cross%20%E7%9B%AE%E9%8C%84.pdf"},
        {"name": "e VITARA", "desc": "首款純電 SUV", "file": "E%20Vitara.pdf"},
        {"name": "CARRY", "desc": "拼大生意首選", "file": "Carry.pdf"},
    ]

    cols = st.columns(2)
    base_url = "https://raw.githubusercontent.com/subarudms/suzuki-inventory/main/"

    for i, car in enumerate(cars):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="car-card">
                    <div class="car-name">{car['name']}</div>
                    <div style="font-size: 0.75rem; color: #888;">{car['desc']}</div>
                    <a class="pdf-button" href="{base_url}{car['file']}" target="_blank">
                        📄 開啟型錄
                    </a>
                </div>
                """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info("📱 iPhone 17 Pro Max 介面優化版")