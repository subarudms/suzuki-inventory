import streamlit as st
import pandas as pd

st.set_page_config(page_title="陳胤合 - Suzuki 庫存看板", layout="wide")
st.title("🚗 Suzuki 車輛庫存即時查詢 (差額計算版)")

@st.cache_data
def load_data():
    # 讀取資料並將空值填補為 0
    df = pd.read_csv("inventory.csv").fillna(0)
    
    # 強制轉換數字欄位
    num_cols = ["已配數量", "在庫數", "向金鈴提車", "領牌車"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # 計算差額
    if "已配數量" in df.columns and "在庫數" in df.columns:
        df["待到貨"] = df["已配數量"] - df["在庫數"]
    else:
        df["待到貨"] = 0
        
    return df

try:
    df = load_data()

    # --- 側邊欄 ---
    st.sidebar.header("🔍 篩選條件")
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("選擇車型", options=models, default=models)
    keyword = st.sidebar.text_input("搜尋顏色或排序代碼", "")

    # --- 資料過濾 ---
    mask = df["車型"].isin(search_model)
    if keyword:
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1))
    
    filtered_df = df[mask].copy()

    # --- 頂部看板 ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總計已配", f"{int(filtered_df['已配數量'].sum())} 台")
    c2.metric("目前在庫", f"{int(filtered_df['在庫數'].sum())} 台")
    c3.metric("待到貨", f"{int(filtered_df['待到貨'].sum())} 台")
    c4.metric("領牌車", f"{int(filtered_df['領牌車'].sum())} 台")

    # --- 表格呈現 ---
    st.subheader("📋 庫存明細與配車進度")
    
    # 自動偵測現有欄位，避免寫死欄位名稱導致報錯
    existing_cols = filtered_df.columns.tolist()
    # 這裡只顯示你想看的關鍵欄位
    target_cols = ["車型", "年份", "顏色", "已配數量", "在庫數", "待到貨", "向金鈴提車", "領牌車", "排序"]
    final_cols = [c for c in target_cols if c in existing_cols]

    # 顯示表格
    st.dataframe(
        filtered_df[final_cols],
        use_container_width=True, 
        hide_index=True
    )

    st.info("💡 「待到貨」 = 已配數量 - 在庫數。")

except Exception as e:
    st.error(f"系統運行錯誤")
    st.write(f"請檢查 CSV 標題是否正確。目前偵測到的標題為：{list(df.columns)}")
    st.write(f"詳細錯誤報告：{e}")
