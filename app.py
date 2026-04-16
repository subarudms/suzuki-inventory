import streamlit as st
import pandas as pd
import os
import urllib.parse

# 1. 頁面基礎設定
st.set_page_config(
    page_title="SUZUKI 銷售助理系統",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 進階介面優化 CSS
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
        padding: 18px;
        border-radius: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        text-align: center;
        border: 1px solid #eee;
    }
    .car-name { color: #003B85; font-weight: bold; font-size: 1.3rem; margin-bottom: 4px; }
    
    /* 修正後的 PDF 按鈕 */
    .pdf-button {
        display: block;
        background-color: #003B85;
        color: white !important;
        text-decoration: none;
        padding: 12px;
        border-radius: 12px;
        font-weight: bold;
        margin-top: 10px;
        font-size: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .pdf-button:active { background-color: #E30613; transform: scale(0.98); }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄導覽
st.sidebar.title("🚀 功能選單")
menu = st.sidebar.radio("切換頁面：", ["📊 庫存即時看板", "📖 數位產品型錄"])

# GitHub 基本路徑 (請確保您的帳號與專案名正確)
# 使用 blob 連結並加上 ?raw=true 對手機開啟 PDF 較為穩定
base_url = "https://github.com/subarudms/suzuki-inventory/blob/main/"

# 4. 邏輯：庫存看板與明細表
if menu == "📊 庫存即時看板":
    st.title("專業庫存即時看板")
    
    # 摘要數字 (Metric Cards)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="metric-card"><p class="metric-label">總計在庫</p><p class="metric-value">33 台</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p class="metric-label">可用差額</p><p class="metric-value">12 台</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><p class="metric-label">已配車數</p><p class="metric-value">21 台</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p class="metric-label">領牌總數</p><p class="metric-value">18 台</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 車型庫存明細清單")
    
    # 讀取並顯示庫存 CSV
    if os.path.exists("inventory.csv"):
        try:
            inventory_df = pd.read_csv("inventory.csv")
            # 針對手機版顯示優化
            st.dataframe(
                inventory_df, 
                use_container_width=True, 
                hide_index=True
            )
        except Exception as e:
            st.error(f"資料讀取失敗，請檢查 CSV 格式。")
    else:
        st.warning("找不到庫存明細檔案 (inventory.csv)")

# 5. 邏輯：數位產品型錄
elif menu == "📖 數位產品型錄":
    st.title("數位產品型錄")
    st.info("💡 點擊下方按鈕將開啟 PDF 檔案。")

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
        # 進行網址編碼處理，確保中文字與空格能正確辨識
        encoded_file = urllib.parse.quote(car['file'])
        final_link = f"{base_url}{encoded_file}?raw=true"
        
        with cols[i % 2]:
            st.markdown(f"""
                <div class="car-card">
                    <div class="car-name">{car['name']}</div>
                    <div style="font-size: 0.8rem; color: #777;">{car['desc']}</div>
                    <a class="pdf-button" href="{final_link}" target="_blank">
                        📄 開啟目錄
                    </a>
                </div>
                """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("系統版本：v2.1 (優化版)")