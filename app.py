import streamlit as st
import pandas as pd

# 設定網頁標題
st.set_page_config(page_title="順利通 - Suzuki 庫存看板", layout="wide")
st.title("🚗 Suzuki 車輛庫存查詢 (可用差額版)")

# 讀取資料邏輯
@st.cache_data(ttl=60) # 設定快取時間為 60 秒，讓手機端更容易看到更新
def load_data():
    try:
        # 讀取 CSV
        df = pd.read_csv("inventory.csv").fillna(0)
        
        # 確保年份為文字，數值欄位為整數
        df["年份"] = df["年份"].astype(str)
        num_cols = ["已配數量", "在庫數", "向金鈴提車", "領牌車"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # 【修改後的公式】：在庫數 扣 已配數量
        if "在庫數" in df.columns and "已配數量" in df.columns:
            df["待到貨/可用"] = df["在庫數"] - df["已配數量"]
        else:
            df["待到貨/可用"] = 0
            
        return df
    except Exception as e:
        st.error(f"CSV 讀取失敗: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- 側邊欄 ---
    st.sidebar.header("🔍 篩選與年份")
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("選擇車型", options=models, default=models)
    
    years = sorted(df["年份"].unique(), reverse=True)
    search_year = st.sidebar.multiselect("選擇年式", options=years, default=years)
    
    keyword = st.sidebar.text_input("搜尋顏色或排序碼", "")

    # --- 資料過濾 ---
    mask = (df["車型"].isin(search_model)) & (df["年份"].isin(search_year))
    if keyword:
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1))
    
    filtered_df = df[mask].copy()

    # --- 頂部看板 ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總計已配", f"{int(filtered_df['已配數量'].sum())} 台")
    c2.metric("目前在庫", f"{int(filtered_df['在庫數'].sum())} 台")
    # 差額看板
    diff_total = int(filtered_df['待到貨/可用'].sum())
    c3.metric("待到貨/可用", f"{diff_total} 台", delta=diff_total, delta_color="normal")
    c4.metric("領牌車", f"{int(filtered_df['領牌車'].sum())} 台")

    # --- 表格呈現 ---
    st.subheader("📋 庫存明細 (依年式與車型排序)")
    
    # 排序邏輯
    sorted_df = filtered_df.sort_values(by=["車型", "年份", "顏色"], ascending=[True, False, True])
    
    # 顯示欄位
    target_cols = ["車型", "年份", "顏色", "在庫數", "已配數量", "待到貨/可用", "向金鈴提車", "領牌車", "排序"]
    final_cols = [c for c in target_cols if c in sorted_df.columns]

    # 美化表格：在庫數大於 0 的顯示藍色背景
    def highlight_rows(s):
        return ['background-color: #e3f2fd' if s.在庫數 > 0 else '' for _ in s]

    st.dataframe(
        sorted_df[final_cols].style.apply(highlight_rows, axis=1),
        use_container_width=True, 
        hide_index=True
    )

    st.info("💡 公式：[待到貨/可用] = 在庫數 - 已配數量。")
else:
    st.warning("目前沒有資料，請確認 GitHub 上的 inventory.csv 是否已上傳。")
