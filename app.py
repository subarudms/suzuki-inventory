import streamlit as st
import pandas as pd

# 1. 專業外觀配置
st.set_page_config(
    page_title="順利通 - Suzuki 庫存專業版",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed" # 手機開啟時預設收起側邊欄，更像 App
)

# 2. 自定義 CSS (美化介面)
st.markdown("""
    <style>
    /* 全域背景顏色 */
    .main { background-color: #f8f9fa; }
    
    /* 頂部標題美化 */
    .main-title {
        font-family: 'Inter', sans-serif;
        color: #003366; /* Suzuki 深藍色 */
        font-weight: 800;
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #e11b22; /* Suzuki 紅色 */
    }
    
    /* 指標卡片美化 */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #003366;
    }
    
    /* 側邊欄美化 */
    .sidebar .sidebar-content { background-color: #003366; color: white; }
    
    /* 表格字體 */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>SUZUKI 專業庫存管理</h1>", unsafe_allow_html=True)

# 3. 讀取資料
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv("inventory.csv").fillna(0)
        df["年份"] = df["年份"].astype(str)
        num_cols = ["已配數量", "在庫數", "向金鈴提車", "領牌車"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # 公式：在庫數 扣 已配數量
        df["待到貨/可用"] = df["在庫數"] - df["已配數量"]
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 4. 側邊欄篩選 (精簡版)
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/1/12/Suzuki_logo_2.svg", width=100)
    st.sidebar.markdown("---")
    
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("🚗 選擇車型", options=models, default=models)
    
    years = sorted(df["年份"].unique(), reverse=True)
    search_year = st.sidebar.multiselect("📅 選擇年式", options=years, default=years)
    
    keyword = st.sidebar.text_input("🔍 搜尋顏色或排序碼", placeholder="例如: 叢林綠")

    # 資料過濾
    mask = (df["車型"].isin(search_model)) & (df["年份"].isin(search_year))
    if keyword:
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1))
    
    f_df = df[mask].copy()

    # 5. 數據指標區 (視覺化卡片)
    st.write("### 📊 即時數據概覽")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("目前在庫", f"{int(f_df['在庫數'].sum())} 台")
    c2.metric("已配數量", f"{int(f_df['已配數量'].sum())} 台")
    
    # 針對可用差額給予顏色提示
    avail = int(f_df['待到貨/可用'].sum())
    c3.metric("待到貨/可用", f"{avail} 台", delta=avail, delta_color="normal")
    c4.metric("領牌車", f"{int(f_df['領牌車'].sum())} 台")

    st.markdown("---")

    # 6. 表格呈現 (專業版排序)
    st.write("### 📋 庫存詳細清單")
    
    sorted_df = f_df.sort_values(by=["車型", "年份", "顏色"], ascending=[True, False, True])
    
    # 重新調整顯示欄位，隱藏不必要的欄位讓手機版更好看
    target_cols = ["車型", "年份", "顏色", "在庫數", "已配數量", "待到貨/可用", "排序"]
    final_cols = [c for c in target_cols if c in sorted_df.columns]

    # 表格美化邏輯：有現車就亮藍色，沒現車就灰色
    def style_table(row):
        return ['background-color: #e3f2fd; font-weight: bold' if row.在庫數 > 0 else 'color: #9e9e9e' for _ in row]

    st.dataframe(
        sorted_df[final_cols].style.apply(style_table, axis=1),
        use_container_width=True, 
        hide_index=True
    )

    # 底部專業資訊
    st.caption(f"最後同步時間: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | 數據版本: 115/04/14")

else:
    st.error("⚠️ 找不到庫存資料，請檢查 GitHub 上的 inventory.csv 檔案。")
