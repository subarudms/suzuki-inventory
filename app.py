import streamlit as st
import pandas as pd
import base64
import requests
import datetime

# 1. 專業介面配置 (修改此處)
st.set_page_config(
    page_title="SUZUKI 雲端庫存系統",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded" # 改為 expanded，選單會預設打開
)

# 2. 讀取 Secrets 設定 (GitHub 一鍵更新核心)
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO = st.secrets["REPO_NAME"]
except:
    st.warning("⚠️ 尚未偵測到 Secrets 設定。請在 Streamlit 控制台設定 GITHUB_TOKEN 與 REPO_NAME。")

# 3. 自定義專業 CSS
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
    </style>
    """, unsafe_allow_html=True)

# 4. GitHub 自動更新函數
def update_github(data_frame):
    url = f"https://api.github.com/repos/{REPO}/contents/inventory.csv"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        sha = res.json()['sha']
        csv_content = data_frame.to_csv(index=False).encode('utf-8-sig')
        encoded = base64.b64encode(csv_content).decode('utf-8')
        
        payload = {
            "message": f"庫存更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": encoded,
            "sha": sha
        }
        put_res = requests.put(url, json=payload, headers=headers)
        return put_res.status_code == 200
    return False

# 5. 數據讀取
@st.cache_data(ttl=1)
def load_data():
    try:
        data = pd.read_csv("inventory.csv").fillna(0)
        data["年份"] = data["年份"].astype(str)
        num_cols = ["在庫數", "已配數量", "向金鈴提車", "領牌車"]
        for col in num_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        data["可用/待到"] = data["在庫數"] - data["已配數量"]
        return data
    except:
        return pd.DataFrame()

df = load_data()

# --- 側邊欄 ---
st.sidebar.markdown("### 🛠️ SUZUKI 雲端系統")
mode = st.sidebar.radio("請選擇操作模式", ["🔍 業務查詢模式", "⚙️ 管理員編輯後台"])

if mode == "🔍 業務查詢模式":
    st.markdown("<div style='text-align:center;'><h1 style='color:#003366; font-size:2.5rem;'>SUZUKI</h1><p>專業庫存即時看板</p></div>", unsafe_allow_html=True)
    
    if not df.empty:
        # 指標看板
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("總計在庫", f"{int(df['在庫數'].sum())} 台")
        c2.metric("已配車數", f"{int(df['已配數量'].sum())} 台")
        c3.metric("可用差額", f"{int(df['可用/待到'].sum())} 台")
        c4.metric("領牌總數", f"{int(df['領牌車'].sum())} 台")
        
        st.markdown("---")
        
        # 篩選
        with st.expander("🔍 搜尋與篩選條件"):
            models = sorted(df["車型"].unique())
            selected = st.multiselect("篩選車型", models, default=models)
            keyword = st.text_input("搜尋顏色、年份或排序碼")
        
        f_df = df[df["車型"].isin(selected)]
        if keyword:
            f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1)]
        
        # 顯示卡片
        for _, row in f_df.sort_values(by=["車型", "年份"], ascending=[True, False]).iterrows():
            if row['領牌車'] > 0:
                tag = '<span class="tag tag-special">🔵 領牌車專案</span>'
            elif row['可用/待到'] > 0:
                tag = '<span class="tag tag-available">✅ 有現車</span>'
            else:
                tag = '<span class="tag tag-none">❌ 需預訂</span>'
            
            st.markdown(f"""
                <div class="inventory-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div class="card-title">{row['年份']} {row['車型']}</div>
                        {tag}
                    </div>
                    <div class="card-subtitle">顏色：{row['顏色']} | 排序：{row['排序']}</div>
                    <div style="display:flex; flex-wrap:wrap; gap:15px; margin-top:10px; border-top:1px solid #f0f0f0; padding-top:10px;">
                        <div style="flex:1;"><span class="data-label">在庫</span><br><span class="data-value">{row['在庫數']}</span></div>
                        <div style="flex:1;"><span class="data-label">已配</span><br><span class="data-value">{row['已配數量']}</span></div>
                        <div style="flex:1;"><span class="data-label" style="color:#e11b22;">可用</span><br><span class="data-value" style="color:#e11b22;">{row['可用/待到']}</span></div>
                        <div style="flex:1;"><span class="data-label">領牌</span><br><span class="data-value">{row['領牌車']}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("<h2 style='text-align:center; color:#e11b22;'>⚙️ 管理員數據後台</h2>", unsafe_allow_html=True)
    if st.text_input("驗證管理密碼", type="password") == "1234":
        st.write("### 📝 編輯庫存資料")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
        
        if st.button("🚀 立即同步至雲端 (一鍵更新)"):
            with st.spinner("同步中..."):
                if update_github(edited_df):
                    st.success("✅ 更新成功！GitHub 檔案已同步。")
                    st.cache_data.clear()
                else:
                    st.error("❌ 更新失敗，請檢查 Secrets 設定。")
