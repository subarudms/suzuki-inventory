import streamlit as st
import pandas as pd

st.set_page_config(page_title="陳胤合 - Suzuki 庫存看板", layout="wide")
st.title("🚗 Suzuki 車輛庫存即時查詢 (差額計算版)")

@st.cache_data
def load_data():
    # 讀取資料並將空值填補為 0
    df = pd.read_csv("inventory.csv").fillna(0)
    
    # 強制轉換數字欄位，避免運算錯誤
    num_cols = ["已配數量", "在庫數", "向金鈴提車", "領牌車"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # 【核心邏輯】：計算待到貨/差額 (已配數量 - 在庫數)
    if "已配數量" in df.columns and "在庫數" in df.columns:
        df["待到貨/差額"] = df["已配數量"] - df["在庫數"]
    
    return df

try:
    df = load_data()

    # --- 側邊欄：搜尋與過濾 ---
    st.sidebar.header("🔍 篩選條件")
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("選擇車型", options=models, default=models)
    
    keyword = st.sidebar.text_input("搜尋顏色或排序代碼", "")

    # --- 資料過濾 ---
    mask = df["車型"].isin(search_model)
    if keyword:
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1))
    
    filtered_df = df[mask]

    # --- 頂部看板 ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總計已配", f"{filtered_df['已配數量'].sum()} 台")
    c2.metric("目前在庫", f"{filtered_df['在庫數'].sum()} 台")
    c3.metric("待到/差額", f"{filtered_df['待到貨/差額'].sum()} 台", delta_color="inverse")
    c4.metric("領牌車", f"{filtered_df['領牌車'].sum()} 台")

    # --- 表格呈現 ---
    st.subheader("📋 庫存明細與配車進度")
    
    # 定義顯示順序
    display_cols = ["車型", "年份", "顏色", "已配數量", "在庫數", "待到貨/差額", "向金鈴提車", "領牌車", "排序"]
    
    # 增加上色邏輯：如果差額 > 0 (代表還有車沒到)，用黃色提醒
    def highlight_diff(row):
        return ['background-color: #fff3cd' if row['待到貨/差額'] > 0 else '' for _ in row]

    st.dataframe(
        filtered_df[display_cols].style.apply(highlight_diff, axis=1),
        use_container_width=True, 
        hide_index=True
    )

    st.info("💡 「待到貨/差額」 = 已配數量 - 在庫數。數值為 0 代表配車已全部入庫。")

except Exception as e:
    st.error(f"資料欄位對應失敗，請檢查 CSV。")
    st.write(f"錯誤訊息：{e}")
