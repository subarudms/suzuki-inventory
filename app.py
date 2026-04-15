import streamlit as st
import pandas as pd

st.set_page_config(page_title="順利通 - Suzuki 庫存看板", layout="wide")
st.title("🚗 Suzuki 車輛庫存查詢 (年式細分版)")

@st.cache_data
def load_data():
    df = pd.read_csv("inventory.csv").fillna(0)
    
    # 確保年份被視為文字，避免 2025 變成 2,025
    df["年份"] = df["年份"].astype(str)
    
    num_cols = ["已配數量", "在庫數", "向金鈴提車", "領牌車"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # 計算待到貨
    if "已配數量" in df.columns and "在庫數" in df.columns:
        df["待到貨"] = df["已配數量"] - df["在庫數"]
    else:
        df["待到貨"] = 0
        
    return df

try:
    df = load_data()

    # --- 側邊欄 ---
    st.sidebar.header("🔍 篩選與年份對照")
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("選擇車型", options=models, default=models)
    
    # 新增年份篩選，讓你可以只看正26或只看正25
    years = sorted(df["年份"].unique(), reverse=True)
    search_year = st.sidebar.multiselect("選擇年式", options=years, default=years)
    
    keyword = st.sidebar.text_input("搜尋顏色或備註", "")

    # --- 資料過濾 ---
    mask = (df["車型"].isin(search_model)) & (df["年份"].isin(search_year))
    if keyword:
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1))
    
    filtered_df = df[mask].copy()

    # --- 頂部看板 ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總計已配", f"{int(filtered_df['已配數量'].sum())} 台")
    c2.metric("目前在庫", f"{int(filtered_df['在庫數'].sum())} 台")
    c3.metric("待到貨(差額)", f"{int(filtered_df['待到貨'].sum())} 台")
    c4.metric("領牌車", f"{int(filtered_df['領牌車'].sum())} 台")

    # --- 表格呈現 ---
    st.subheader("📋 庫存明細 (依車型與年式排序)")
    
    # 設定排序邏輯：先排車型，再排年份(由新到舊)，再排顏色
    sorted_df = filtered_df.sort_values(by=["車型", "年份", "顏色"], ascending=[True, False, True])
    
    target_cols = ["車型", "年份", "顏色", "已配數量", "在庫數", "待到貨", "向金鈴提車", "領牌車", "排序"]
    final_cols = [c for c in target_cols if c in sorted_df.columns]

    # 使用樣式美化：如果是在庫數 > 0 的車輛，加上淡藍色背景
    def highlight_stock(s):
        return ['background-color: #e1f5fe' if s.在庫數 > 0 else '' for _ in s]

    st.dataframe(
        sorted_df[final_cols].style.apply(highlight_stock, axis=1),
        use_container_width=True, 
        hide_index=True
    )

    st.info("💡 提示：同車型不同年式已分列顯示。藍色背景代表「目前有現車在庫」。")

except Exception as e:
    st.error(f"系統運行錯誤，請檢查 CSV 標題與格式。")
    st.write(f"詳細錯誤報告：{e}")
