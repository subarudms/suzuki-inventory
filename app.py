import streamlit as st
import pandas as pd

# 設定網頁標題
st.set_page_config(page_title="陳胤合 - 車輛庫存查詢器", layout="wide")
st.title("🚗 車輛庫存即時查詢系統")

# 讀取資料 (從 GitHub 上的 csv 讀取)
@st.cache_data
def load_data():
    return pd.read_csv("inventory.csv")

df = load_data()

# --- 側邊欄過濾器 ---
st.sidebar.header("篩選條件")
search_model = st.sidebar.multiselect("選擇車型", options=df["車型"].unique(), default=list(df["車型"].unique()))
search_status = st.sidebar.multiselect("庫存狀態", options=df["狀態"].unique(), default=list(df["狀態"].unique()))

# --- 執行篩選 ---
mask = (df["車型"].isin(search_model)) & (df["狀態"].isin(search_status))
filtered_df = df[mask]

# --- 顯示結果 ---
st.metric("符合條件車輛", len(filtered_df))

# 根據狀態上色 (簡單範例)
def color_status(val):
    color = 'green' if val == '現車' else 'red' if val == '已交車' else 'orange'
    return f'color: {color}'

st.dataframe(filtered_df.style.map(color_status, subset=['狀態']), use_container_width=True)

# --- 快速報價功能 ---
if not filtered_df.empty:
    st.divider()
    selected_car = st.selectbox("選擇車型以產生分享文字", filtered_df["車型"] + " - " + filtered_df["顏色"])
    if st.button("生成 LINE 分享文字"):
        row = filtered_df.iloc[0] # 這裡可以根據 selectbox 選擇
        share_text = f"【庫存回報】\n車型：{row['車型']}\n年式：{row['年份']}\n顏色：{row['顏色']}\n狀態：{row['狀態']}\n目前位置：{row['位置']}"
        st.code(share_text)
        st.success("請長按上方文字複製到 LINE！")
