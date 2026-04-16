import streamlit as st
import pandas as pd
import datetime

# 1. 專業配置
st.set_page_config(
    page_title="SUZUKI 專業庫存管理",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 自定義專業 CSS
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    [data-testid="stSidebar"] { background-color: #003366; color: white; }
    div[data-testid="stMetric"] {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-left: 6px solid #e11b22;
    }
    .inventory-card {
        background-color: white; padding: 18px; margin-bottom: 12px;
        border-radius: 15px; border: 1px solid #eef2f6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .card-title { font-size: 1.2rem; font-weight: 800; color: #003366; }
    .card-subtitle { color: #6c757d; font-size: 0.9rem; margin-bottom: 10px; }
    .tag { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
    .tag-available { background-color: #e8f5e9; color: #2e7d32; }
    .tag-none { background-color: #ffebee; color: #c62828; }
    .tag-special { background-color: #e3f2fd; color: #1565c0; }
    </style>
    """, unsafe_allow_html=True)

# 3. 穩定讀取資料
@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv("inventory.csv").fillna(0)
        data["年份"] = data["年份"].astype(str)
        # 數值轉換
        for col in ["在庫數", "已配數量", "向金鈴提車", "領牌車"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        # 公式：在庫 - 已配
        data["可用/待到"] = data["在庫數"] - data["已配數量"]
        return data
    except:
        return pd.DataFrame()

df = load_data()

# --- 側邊欄模式切換 ---
st.sidebar.markdown("### 🛠️ 系統選單")
mode = st.sidebar.radio("模式選擇", ["🔍 業務查詢模式", "⚙️ 管理員後台"])

if mode == "🔍 業務查詢模式":
    # 標題與 Logo
    st.markdown("""
        <div style="text-align: center; margin-bottom: 25px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/1/12/Suzuki_logo_2.svg" width="80">
            <h1 style="color: #003366; margin-top: 10px;">專業庫存即時看板</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # 頂部統計看板
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("當前總在庫", f"{int(df['在庫數'].sum())} 台")
        c2.metric("已配車數", f"{int(df['已配數量'].sum())} 台")
        c3.metric("可用差額", f"{int(df['可用/待到'].sum())} 台")
        c4.metric("領牌車", f"{int(df['領牌車'].sum())} 台")

    st.markdown("---")
    
    # 篩選區
    with st.expander("🔍 搜尋與篩選", expanded=False):
        all_models = sorted(df["車型"].unique()) if not df.empty else []
        selected_models = st.multiselect("選擇車型", options=all_models, default=all_models)
        keyword = st.text_input("關鍵字搜尋 (顏色/排序碼)")

    # 顯示卡片列表
    if not df.empty:
        f_df = df[df["車型"].isin(selected_models)]
        if keyword:
            f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1)]
        
        sorted_df = f_df.sort_values(by=["車型", "年份"], ascending=[True, False])
        
        for _, row in sorted_df.iterrows():
            # 判斷狀態標籤
            if row['在庫數'] > row['已配數量']:
                tag = '<span class="tag tag-available">✅ 有現車</span>'
            elif row['領牌車'] > 0:
                tag = '<span class="tag tag-special">🔵 領牌車</span>'
            else:
                tag = '<span class="tag tag-none">❌ 暫無可用</span>'
            
            st.markdown(f"""
                <div class="inventory-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div class="card-title">{row['年份']} {row['車型']}</div>
                        {tag}
                    </div>
                    <div class="card-subtitle">車色：{row['顏色']} | 排序碼：{row['排序']}</div>
                    <div style="display: flex; gap: 20px; margin-top: 10px; border-top: 1px solid #f0f0f0; padding-top: 10px;">
                        <div><small>在庫</small><br><b>{row['在庫數']}</b></div>
                        <div><small>已配</small><br><b>{row['已配數量']}</b></div>
                        <div style="color: #e11b22;"><small>可用</small><br><b>{row['可用/待到']}</b></div>
                        <div><small>提車中</small><br><b>{row['向金鈴提車']}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.caption(f"數據版本: 115/04/14 | 最後更新: {datetime.datetime.now().strftime('%H:%M')}")

else:
    # --- 管理員模式 (暫時使用下載/上傳方案) ---
    st.markdown("<h2 style='color: #e11b22;'>⚙️ 管理員數據維護</h2>", unsafe_allow_html=True)
    pwd = st.text_input("管理密碼", type="password")
    
    if pwd == "1234":
        st.write("### 📝 快速編輯資料")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        # 下載按鈕
        csv = edited_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="💾 下載最新 inventory.csv",
            data=csv,
            file_name='inventory.csv',
            mime='text/csv',
        )
        st.info("💡 手機操作：下載後請上傳至 GitHub 以完成更新。")
