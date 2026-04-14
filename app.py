import streamlit as st
import pandas as pd

st.set_page_config(page_title="陳胤合 - 車輛庫存查詢器", layout="wide")
st.title("🚗 Suzuki 車輛庫存查詢(數量統計版)")

@st.cache_data
def load_data():
    # 確保年份與數量讀取正確
    df = pd.read_csv("inventory.csv", dtype={'年份': str, '數量': int})
    return df

df = load_data()

# --- 側邊欄：篩選器 ---
st.sidebar.header("🔍 篩選條件")

# 1. 車型篩選
all_models = sorted(df["車型"].unique())
search_model = st.sidebar.multiselect("選擇車型", options=all_models, default=all_models)

# 2. 年份篩選
all_years = sorted(df["年份"].unique(), reverse=True)
search_year = st.sidebar.multiselect("出廠年份", options=all_years, default=all_years)

# 3. 顏色搜尋
color_keyword = st.sidebar.text_input("搜尋特定顏色", "")

# --- 執行過濾 ---
mask = (df["車型"].isin(search_model)) & (df["年份"].isin(search_year))
if color_keyword:
    mask = mask & (df["顏色"].str.contains(color_keyword))

filtered_df = df[mask]

# --- 顯示數據摘要 ---
total_stock = filtered_df["數量"].sum()
st.metric("當前篩選總台數", f"{total_stock} 台")

# --- 排序與呈現 ---
# 按車型排序，年份從新到舊
display_df = filtered_df.sort_values(by=["車型", "年份"], ascending=[True, False])

# 重新定義欄位順序，讓「數量」排在醒目的地方
cols = ["車型", "年份", "顏色", "數量", "狀態", "位置", "建議售價"]
display_df = display_df[cols]

# 顯示表格
st.subheader("📋 庫存數量清單")
st.dataframe(
    display_df, 
    use_container_width=True, 
    hide_index=True
)

# --- 醒目提醒 (低庫存警告) ---
low_stock = display_df[display_df["數量"] <= 1]
if not low_stock.empty:
    st.warning("⚠️ 以下車款庫存僅剩 1 台或以下，請留意：")
    for _, row in low_stock.iterrows():
        st.write(f"• {row['年份']} {row['車型']} ({row['顏色']})")
