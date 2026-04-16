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
    .card-subtitle { color: #6c757d; font-size: 0.9rem; margin-bottom: 8px; }
    .tag { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; }
    .tag-available { background-color: #e8f5e9; color: #2e7d32; }
    .tag-none { background-color: #f5f5f5; color: #9e9e9e; }
    .tag-special { background-color: #e3f2fd; color: #1565c0; border: 1px solid #1565c0; }
    .data-label { color: #6c757d; font-size: 0.75rem; }
    .data-value { font-size: 1rem; font-weight: bold; color: #003366; }
    .data-highlight { color: #e11b22; }
    </style>
    """, unsafe_allow_html=True)

# 3. 穩定讀取資料
@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv("inventory.csv").fillna(0)
        data["年份"] = data["年份"].astype(str)
        # 強制將所有數值欄位轉為整數
        num_cols = ["在庫數", "已配數量", "向金鈴提車", "領牌車"]
        for col in num_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        
        # 公式：在庫 - 已配
        data["可用/待到"] = data["在庫數"] - data["已配數量"]
        return data
    except Exception as e:
        st.error(f"讀取錯誤: {e}")
        return pd.DataFrame()

df = load_data()

# --- 側邊欄 ---
st.sidebar.markdown("### 🛠️ 系統選單")
mode = st.sidebar.radio("模式選擇", ["🔍 業務查詢模式", "⚙️ 管理員後台"])

if mode == "🔍 業務查詢模式":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 25px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/1/12/Suzuki_logo_2.svg" width="80">
            <h1 style="color: #003366; margin-top: 10px;">專業庫存即時看板</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if not df.empty:
        # 統計看板
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("總計在庫", f"{int(df['在庫數'].sum())} 台")
        c2.metric("已配車數", f"{int(df['已配數量'].sum())} 台")
        c3.metric("可用差額", f"{int(df['可用/待到'].sum())} 台")
        c4.metric("領牌總數", f"{int(df['領牌車'].sum())} 台")

        st.markdown("---")
        
        # 篩選區
        with st.expander("🔍 搜尋與篩選條件"):
            all_models = sorted(df["車型"].unique())
            selected_models = st.multiselect("選擇車型", options=all_models, default=all_models)
            keyword = st.text_input("搜尋顏色、排序碼或年式")

        # 資料過濾
        f_df = df[df["車型"].isin(selected_models)]
        if keyword:
            f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1)]
        
        sorted_df = f_df.sort_values(by=["車型", "年份"], ascending=[True, False])
        
        # 卡片呈現
        for _, row in sorted_df.iterrows():
            # 狀態標籤邏輯
            if row['領牌車'] > 0:
                tag = '<span class="tag tag-special">🔵 領牌車專案</span>'
            elif row['在庫數'] > row['已配數量']:
                tag = '<span class="tag tag-available">✅ 現車在庫</span>'
            else:
                tag = '<span class="tag tag-none">❌ 暫無可用</span>'
            
            st.markdown(f"""
                <div class="inventory-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div class="card-title">{row['年份']} {row['車型']}</div>
                        {tag}
                    </div>
                    <div class="card-subtitle">顏色：{row['顏色']} | 排序：{row['排序']}</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 10px; border-top: 1px solid #f0f0f0; padding-top: 12px;">
                        <div style="flex: 1; min-width: 60px;"><span class="data-label">在庫</span><br><span class="data-value">{row['在庫數']}</span></div>
                        <div style="flex: 1; min-width: 60px;"><span class="data-label">已配</span><br><span class="data-value">{row['已配數量']}</span></div>
                        <div style="flex: 1; min-width: 60px;"><span class="data-label">可用</span><br><span class="data-value data-highlight">{row['可用/待到']}</span></div>
                        <div style="flex: 1; min-width: 60px;"><span class="data-label">領牌車</span><br><span class="data-value" style="color:#1565c0;">{row['領牌車']}</span></div>
                        <div style="flex: 1; min-width: 60px;"><span class="data-label">提車中</span><br><span class="data-value">{row['向金鈴提車']}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.caption(f"最後更新時間: {datetime.datetime.now().strftime('%H:%M:%S')}")

else:
    # 管理員模式
    st.markdown("<h2 style='color: #e11b22;'>⚙️ 管理員後台</h2>", unsafe_allow_html=True)
    pwd = st.text_input("輸入管理密碼", type="password")
    if pwd == "1234":
        st.write("### 📝 直接編輯下方表格")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
        csv = edited_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="💾 下載最新庫存檔案", data=csv, file_name='inventory.csv', mime='text/csv')
