import streamlit as st
import pandas as pd
import base64
import requests
import datetime

# 1. 專業介面配置
st.set_page_config(
    page_title="SUZUKI 雲端庫存系統",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 讀取 Secrets
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO = st.secrets["REPO_NAME"]
except:
    st.warning("⚠️ Secrets 未設定")

# 3. CSS 樣式
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    [data-testid="stSidebar"] { min-width: 280px !important; background-color: #003366; }
    .stRadio [data-testid="stWidgetLabel"] { font-size: 1.2rem !important; color: white !important; font-weight: bold !important; }
    .stRadio div[role="radiogroup"] { background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 12px; }
    
    .inventory-card {
        background-color: white; padding: 18px; margin-bottom: 12px;
        border-radius: 15px; border: 1px solid #eef2f6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px; }
    .card-title { font-size: 1.15rem; font-weight: 800; color: #003366; flex: 1; padding-right: 10px; }
    
    .tag-container { display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }
    .tag { padding: 3px 8px; border-radius: 15px; font-size: 0.7rem; font-weight: bold; white-space: nowrap; border: 1px solid transparent; }
    .tag-available { background-color: #e8f5e9; color: #2e7d32; border-color: #2e7d32; }
    .tag-special { background-color: #e3f2fd; color: #1565c0; border-color: #1565c0; }
    .tag-none { background-color: #f5f5f5; color: #9e9e9e; }
    
    .data-grid { display: flex; gap: 8px; border-top: 1px solid #f0f0f0; padding-top: 10px; margin-top: 10px; flex-wrap: wrap; }
    .data-item { flex: 1; min-width: 60px; text-align: center; }
    .label { color: #6c757d; font-size: 0.65rem; display: block; margin-bottom: 2px; }
    .val { font-size: 0.95rem; font-weight: bold; color: #003366; }
    </style>
    """, unsafe_allow_html=True)

# 4. GitHub 更新函數
def update_github(data_frame):
    url = f"https://api.github.com/repos/{REPO}/contents/inventory.csv"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        sha = res.json()['sha']
        csv_content = data_frame.to_csv(index=False).encode('utf-8-sig')
        encoded = base64.b64encode(csv_content).decode('utf-8')
        payload = {"message": f"Update: {datetime.datetime.now()}", "content": encoded, "sha": sha}
        return requests.put(url, json=payload, headers=headers).status_code == 200
    return False

# 5. 資料讀取
@st.cache_data(ttl=1)
def load_data():
    try:
        data = pd.read_csv("inventory.csv").fillna(0)
        if "年份" in data.columns:
            data["年份"] = data["年份"].astype(str).str.replace(".0", "", regex=False)
        num_cols = ["在庫數", "已配數量", "向金鈴提車", "領牌車"]
        for col in num_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        data["可用"] = data["在庫數"] - data["已配數量"]
        return data
    except: return pd.DataFrame()

df = load_data()

# --- 側邊欄 ---
with st.sidebar:
    st.markdown("## 🚗 選單控制")
    mode = st.radio("功能切換", ["🔍 業務查詢模式", "⚙️ 管理員後台"])
    st.markdown("---")

# --- 主畫面 ---
if mode == "🔍 業務查詢模式":
    st.markdown("<h2 style='text-align:center; color:#003366;'>SUZUKI 庫存查詢</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        # --- [修復重點] 自動讀取跳轉參數邏輯 ---
        query_params = st.query_params
        # 同時兼容 q 或 model 參數
        url_query = query_params.get("q") or query_params.get("model")
        
        models = sorted(df["車型"].unique().tolist())
        
        # 決定預設選中的車型清單
        default_selection = models 
        is_expanded = True # 預設展開搜尋列
        
        if url_query:
            search_target = str(url_query).upper().strip()
            # 強化模糊比對邏輯
            matched = [m for m in models if search_target in str(m).upper() or str(m).upper() in search_target]
            
            # 如果完全沒匹配到，嘗試只抓第一個單字進行保險比對 (例如 VITARA S 只抓 VITARA)
            if not matched:
                first_word = search_target.split(' ')[0]
                matched = [m for m in models if first_word in str(m).upper()]

            if matched:
                default_selection = matched
                is_expanded = False # 有匹配到就自動收起搜尋列，直接看結果
        
        # 搜尋篩選介面
        with st.expander("🔍 搜尋篩選", expanded=is_expanded):
            sel_m = st.multiselect("車型篩選", models, default=default_selection)
            key = st.text_input("搜尋關鍵字 (顏色/排序碼/年式)")
        
        # 執行資料過濾
        f_df = df[df["車型"].isin(sel_m)]
        if key: 
            f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(key, case=False)).any(axis=1)]

        # 顯示渲染卡片
        for _, row in f_df.sort_values(by=["車型", "年份"], ascending=[True, False]).iterrows():
            tags = '<div class="tag-container">'
            if row['可用'] > 0: tags += '<span class="tag tag-available">✅ 在庫現車</span>'
            if row['領牌車'] > 0: tags += '<span class="tag tag-special">🔵 領牌專案</span>'
            if row['可用'] <= 0 and row['領牌車'] <= 0: tags += '<span class="tag tag-none">❌ 需預訂</span>'
            tags += '</div>'
            
            st.markdown(f"""
                <div class="inventory-card">
                    <div class="card-header">
                        <div class="card-title">{row['年份']} {row['車型']}</div>
                        {tags}
                    </div>
                    <div style="color:#6c757d; font-size:0.85rem;">顏色：{row['顏色']} | 排序：{row['排序']}</div>
                    <div class="data-grid">
                        <div class="data-item"><span class="label">在庫</span><span class="val">{row['在庫數']}</span></div>
                        <div class="data-item"><span class="label">已配</span><span class="val">{row['已配數量']}</span></div>
                        <div class="data-item"><span class="label" style="color:#e11b22;">可用</span><span class="val" style="color:#e11b22;">{row['可用']}</span></div>
                        <div class="data-item"><span class="label">領牌</span><span class="val">{row['領牌車']}</span></div>
                        <div class="data-item"><span class="label" style="color:#ffa500;">提車中</span><span class="val" style="color:#ffa500;">{row['向金鈴提車']}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.markdown("## ⚙️ 管理員後台")
    if st.text_input("輸入管理密碼", type="password") == "1234":
        ed_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
        if st.button("🚀 立即同步更新至 GitHub"):
            with st.spinner("同步中..."):
                if update_github(ed_df):
                    st.success("更新成功！")
                    st.cache_data.clear()
                    st.rerun()
                else: st.error("更新失敗")
