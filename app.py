import streamlit as st
import pandas as pd
import os
import base64

# 1. 頁面基礎設定 (針對 iPhone 17 Pro Max 優化佈局)
st.set_page_config(
    page_title="SUZUKI 銷售助理系統",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 進階介面優化 CSS (加入 PDF 預覽容器樣式)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #003B85; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* 庫存看板卡片 */
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
    
    /* 目錄卡片樣式 */
    .car-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 10px;
        text-align: center;
        border: 1px solid #eee;
    }
    .car-name { color: #003B85; font-weight: bold; font-size: 1.2rem; }
    
    /* 按鈕樣式 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #003B85;
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #E30613;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. PDF 預覽功能函數
def display_pdf(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        # 嵌入 PDF 預覽，高度設為 800px 方便在手機滑動
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf" style="border:none; border-radius:10px;"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.error(f"找不到檔案：{file_path}")

# 4. 側邊欄選單
st.sidebar.title("🚀 功能選單")
menu = st.sidebar.radio("切換功能：", ["📊 庫存看板與明細", "📖 數位產品型錄"])

# 5. 邏輯：庫存看板與明細表
if menu == "📊 庫存看板與明細":
    st.title("專業庫存即時看板")
    
    # 摘要數字
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="metric-card"><p class="metric-label">總計在庫</p><p class="metric-value">33 台</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p class="metric-label">可用差額</p><p class="metric-value">12 台</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><p class="metric-label">已配車數</p><p class="metric-value">21 台</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><p class="metric-label">領牌總數</p><p class="metric-value">18 台</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 車型庫存詳細清單")
    
    # 讀取並顯示庫存 CSV
    if os.path.exists("inventory.csv"):
        try:
            inventory_df = pd.read_csv("inventory.csv")
            st.dataframe(inventory_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error("讀取 inventory.csv 失敗，請確認檔案格式。")
    else:
        st.warning("根目錄中找不到 inventory.csv")

# 6. 邏輯：數位產品型錄 (支援 App 內預覽)
elif menu == "📖 數位產品型錄":
    st.title("數位產品型錄")
    
    # 初始化 Session State 來追蹤當前選中的 PDF
    if 'selected_pdf' not in st.session_state:
        st.session_state.selected_pdf = None

    # 如果有選中 PDF，顯示預覽與返回按鈕
    if st.session_state.selected_pdf:
        if st.button("⬅️ 返回型錄列表"):
            st.session_state.selected_pdf = None
            st.rerun()
        
        st.subheader(f"正在閱讀：{st.session_state.selected_pdf}")
        display_pdf(st.session_state.selected_pdf)
    
    # 否則顯示卡片清單
    else:
        st.write("點擊「在線閱讀」即可直接在此開啟 PDF 目錄")
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
                st.markdown(f'<div class="car-card"><div class="car-name">{car["name"]}</div><p style="color:#888; font-size:0.8rem;">{car["desc"]}</p></div>', unsafe_allow_html=True)
                if st.button(f"👁️ 在線閱讀", key=f"btn_{car['name']}"):
                    st.session_state.selected_pdf = car['file']
                    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("iPhone 17 Pro Max 專業版 v3.0")
