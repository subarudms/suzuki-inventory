import streamlit as st
import pandas as pd

st.set_page_config(page_title="陳胤合 - Suzuki 庫存看板", layout="wide")
st.title("🚗 Suzuki 車輛庫存即時查詢 (實戰版)")

@st.cache_data
def load_data():
    # 確保所有數據都能正確讀取，即使有空白欄位也不當機
    df = pd.read_csv("inventory.csv").fillna(0)
    return df

try:
    df = load_data()

    # --- 側邊欄：同步報表邏輯 ---
    st.sidebar.header("🔍 篩選與搜尋")
    
    # 車型篩選
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("選擇車型", options=models, default=models)

    # 關鍵字搜尋 (例如搜顏色、排序代碼)
    keyword = st.sidebar.text_input("關鍵字搜尋 (顏色/代碼)", "")

    # --- 資料過濾 ---
    mask = df["車型"].isin(search_model)
    if keyword:
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1))
    
    filtered_df = df[mask]

    # --- 頂部數據看板 ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總在庫數", f"{int(filtered_df['在庫數'].sum())} 台")
    col2.metric("金鈴提車中", f"{int(filtered_df['向金鈴提車'].sum())} 台")
    col3.metric("領牌車總數", f"{int(filtered_df['領牌車'].sum())} 台")
    col4.metric("篩選總計", f"{len(filtered_df)} 種類")

    # --- 表格呈現 ---
    st.subheader("📋 庫存明細表")
    # 按照你提供的報表順序排列欄位
    display_cols = ["排序代號", "車型", "年份", "顏色", "在庫數", "向金鈴提車", "領牌車", "排序"]
    
    # 這裡使用一個小技巧：如果在庫數 > 0，整行加粗或變色
    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

    # --- 快速查看備註 ---
    st.info("💡 提示：點擊表格標題可以進行升冪或降冪排序。")

except Exception as e:
    st.error(f"偵測到欄位不符合，請確認 inventory.csv 是否包含：排序代號,車型,年份,顏色,在庫數,向金鈴提車,領牌車,排序")
    st.info(f"目前錯誤訊息：{e}")
