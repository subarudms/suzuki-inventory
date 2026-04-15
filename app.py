import streamlit as st
import pandas as pd

# 設定網頁標題與版面
st.set_page_config(page_title="陳胤合 - Suzuki 庫存看板", layout="wide")

# 強制讓內容在手機端也能即時更新
st.title("🚗 Suzuki 車輛庫存查詢 (修正版)")

@st.cache_data(ttl=60) # 設定快取每 60 秒失效一次，強迫讀取新資料
def load_data():
    try:
        # 讀取 CSV
        df = pd.read_csv("inventory.csv").fillna(0)
        
        # 確保年份為文字，其餘為數字
        df["年份"] = df["年份"].astype(str)
        num_cols = ["已配數量", "在庫數", "向金鈴提車", "領牌車"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # 計算待到貨 (差額)
        df["待到貨"] = df["已配數量"] - df["在庫數"]
        return df
    except Exception as e:
        st.error(f"讀取 CSV 失敗，請檢查格式。錯誤：{e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- 側邊欄 ---
    st.sidebar.header("🔍 篩選條件")
    
    # 車型篩選
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("選擇車型", options=models, default=models)
    
    # 年份篩選
    years = sorted(df["年份"].unique(), reverse=True)
    search_year = st.sidebar.multiselect("選擇年式", options=years, default=years)
    
    # 搜尋框
    keyword = st.sidebar.text_input("搜尋顏色/排序代碼", "")

    # --- 過濾資料 ---
    mask = (df["車型"].isin(search_model)) & (df["年份"].isin(search_year))
    if keyword:
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword, case=False)).any(axis=1))
    
    filtered_df = df[mask].copy()

    # --- 頂部摘要看板 ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總計已配", f"{int(filtered_df['已配數量'].sum())} 台")
    c2.metric("目前在庫", f"{int(filtered_df['在庫數'].sum())} 台")
    c3.metric("待到貨", f"{int(filtered_df['待到貨'].sum())} 台")
    c4.metric("領牌車", f"{int(filtered_df['領牌車'].sum())} 台")

    # --- 表格顯示 ---
    st.subheader("📋 庫存明細與進度")
    
    # 排序：車型 -> 年份 -> 顏色
    sorted_df = filtered_df.sort_values(by=["車型", "年份", "顏色"], ascending=[True, False, True])
    
    # 欄位順序對齊
    display_cols = ["車型", "年份", "顏色", "已配數量", "在庫數", "待到貨", "向金鈴提車", "領牌車", "排序"]
    
    # 樣式：在庫數 > 0 顯示淡藍色，待到貨 > 0 顯示淡橘色
    def style_rows(row):
        style = [''] * len(row)
        if row['在庫數'] > 0:
            style = ['background-color: #e3f2fd'] * len(row) # 淡藍
        elif row['待到貨'] > 0:
            style = ['background-color: #fff3e0'] * len(row) # 淡橘
        return style

    st.dataframe(
        sorted_df[display_cols].style.apply(style_rows, axis=1),
        use_container_width=True, 
        hide_index=True
    )
    
    st.info("💡 藍色表示有現車，橘色表示有配額但車未到。")

# 手動刷新按鈕 (針對手機版)
if st.button("🔄 手動刷新數據"):
    st.cache_data.clear()
    st.rerun()
