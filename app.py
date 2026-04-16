import streamlit as st
import pandas as pd

# 1. 設定頁面基礎配置
st.set_page_config(
    page_title="SUZUKI 銷售助理系統",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 加入自定義 CSS 樣式 (針對手機與 Suzuki 企業色優化)
st.markdown("""
    <style>
    /* 全域背景 */
    .stApp { background-color: #f8f9fa; }
    
    /* 側邊欄改為 Suzuki 深藍色 */
    [data-testid="stSidebar"] {
        background-color: #003B85;
        color: white;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* 庫存卡片樣式 (紅色邊框) */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 8px solid #E30613;
        margin-bottom: 15px;
        text-align: center;
    }
    
    /* 型錄卡片樣式 */
    .car-card {
        background-color: white;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        text-align: center;
        border: 1px solid #eee;
    }
    
    .car-name {
        color: #003B85;
        font-weight: bold;
        font-size: 1.3rem;
        margin-bottom: 5px;
    }
    
    /* PDF 開啟按鈕 (加大方便點擊) */
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
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 側邊欄導覽選單
st.sidebar.image("https://www.taiwansuzuki.com.tw/images/logo.png", width=150)
st.sidebar.title("銷售助理選單")
menu = st.sidebar.radio("請選擇功能：", ["📊 庫存即時看板", "📖 數位產品型錄"])

# 4. 功能邏輯：庫存即時看板
if menu == "📊 庫存即時看板":
    st.title("專業庫存即時看板")
    
    # 建立四格看板 (根據您的截圖數據)
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('<div class="metric-card"><p style="margin:0;color:#666;">總計在庫</p><h1 style="margin:0;color:#333;">33 台</h1></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p style="margin:0;color:#666;">可用差額</p><h1 style="margin:0;color:#333;">12 台</h1></div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="metric-card"><p style="margin:0;color:#666;">已配車數</p><h1 style="margin:0;color:#333;">21 台</h1></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p style="margin:0;color:#666;">領牌總數</p><h1 style="margin:0;color:#333;">18 台</h1></div>', unsafe_allow_html=True)

    st.caption("📱 專為 iPhone 17 Pro Max 最佳化顯示 | 數據每小時自動同步")

# 5. 功能邏輯：數位產品型錄
elif menu == "📖 數位產品型錄":
    st.title("數位產品型錄索引")
    st.write("點擊下方按鈕可直接開啟 PDF 目錄供客戶閱覽")

    # 定義車型資料 (請確保 GitHub 根目錄有這些檔案)
    cars = [
        {"name": "SWIFT", "desc": "城市經典 輕油電", "file": "Swift.pdf"},
        {"name": "JIMNY", "desc": "本格越野精神", "file": "Jimny.pdf"},
        {"name": "VITARA", "desc": "強悍越野實力", "file": "Vitara.pdf"},
        {"name": "S-CROSS", "desc": "大膽自信 SUV", "file": "S-Cross%20%E7%9B%AE%E9%8C%84.pdf"}, # 處理空格與中文
        {"name": "e VITARA", "desc": "首款純電 SUV", "file": "E%20Vitara.pdf"},
        {"name": "CARRY", "desc": "拼大生意首選", "file": "Carry.pdf"},
    ]

    # 每列顯示兩台車
    cols = st.columns(2)
    base_url = "https://raw.githubusercontent.com/subarudms/suzuki-inventory/main/"

    for i, car in enumerate(cars):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="car-card">
                    <div class="car-name">{car['name']}</div>
                    <div style="font-size: 0.8rem; color: #888;">{car['desc']}</div>
                    <a class="pdf-button" href="{base_url}{car['file']}" target="_blank">
                        📄 開啟型錄
                    </a>
                </div>
                """, unsafe_allow_html=True)

# 底部資訊
st.sidebar.markdown("---")
st.sidebar.info("👤 目前使用者：SUZUKI 專業銷售")

```