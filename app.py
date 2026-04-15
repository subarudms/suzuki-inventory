import streamlit as st
import pandas as pd
import datetime

# 1. 專業配置
st.set_page_config(page_title="SUZUKI 專業庫存", page_icon="🚗", layout="wide", initial_sidebar_state="collapsed")

# 2. 介面美化 CSS (這部分最容易漏掉結尾，請確保最後有 """)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-title {
        color: #003366; font-weight: 800; text-align: center;
        padding: 20px; border-bottom: 3px solid #e11b22; margin-bottom: 20px;
    }
    div[data-testid="stMetric"] {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-left: 5px solid #003366;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>SUZUKI 精準庫存管理系統</h1>", unsafe_allow_html=True)

# 3. 穩定讀取資料
@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv("inventory.csv").fillna(0)
        data["年份"] = data["年份"].astype(str)
        # 轉換數值
        for col in ["在庫數", "已配數量", "向金鈴提車", "領牌車"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        # 公式：在庫 - 已配
        if "在庫數" in data.columns and "已配數量" in data.columns:
            data["待到貨/可用"] = data["在庫數"] - data["已配數量"]
        return data, None
    except Exception as e:
        return pd.DataFrame(), str(e)

df, error_msg = load_data()

if not df.empty:
    # 4. 側邊欄篩選
    st.sidebar.header("📊 篩選過濾")
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("🚗 選擇車型", options=models, default=models)
    
    years = sorted(df["年份"].unique(), reverse=True)
    search_year = st.sidebar.multiselect("📅 選擇年式", options=years, default=years)
    
    keyword = st.sidebar.text_input("🔍 搜尋關鍵字", placeholder="顏色或排序碼")

    # 過濾邏輯
    mask = (df["車型"].isin(search_model)) & (df["年份"].isin(search_year))
    if keyword:
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1))
    
    f_df = df[mask].copy()

    # 5. 數據看板
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("目前在庫", f"{int(f_df['在庫數'].sum())} 台")
    c2.metric("已配數量", f"{int(f_df['已配數量'].sum())} 台")
    avail = int(f_df['待到貨/可用'].sum())
    c3.metric("待到貨/可用", f"{avail} 台")
    c4.metric("領牌車", f"{int(f_df['領牌車'].sum())} 台")

    st.markdown("---")

    # 6. 表格呈現
    st.write("### 📋 庫存詳細清單")
    target_cols = ["車型", "年份", "顏色", "在庫數", "已配數量", "待到貨/可用", "向金鈴提車", "領牌車", "排序"]
    final_cols = [c for c in target_cols if c in f_df.columns]
    
    sorted_df = f_df.sort_values(by=["車型", "年份", "顏色"], ascending=[True, False, True])

    def style_row(row):
        return ['background-color: #e3f2fd; font-weight: bold' if row.在庫數 > 0 else 'color: #9e9e9e' for _ in row]

    st.dataframe(sorted_df[final_cols].style.apply(style_row, axis=1), use_container_width=True, hide_index=True)
    st.caption(f"數據更新於: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

else:
    st.error("資料讀取失敗，請確認 inventory.csv 標題是否正確。")
    if error_msg: st.info(f"錯誤細節: {error_msg}")
