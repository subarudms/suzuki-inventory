import streamlit as st
import pandas as pd
import base64
import requests
import datetime

# 1. 專業介面配置 - 強制展開目錄並優化手機端顯示
st.set_page_config(
    page_title="SUZUKI 雲端庫存系統",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded" # 預設展開左側選單
)

# 2. 讀取 Secrets
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO = st.secrets["REPO_NAME"]
except:
    st.warning("⚠️ 尚未偵測到 Secrets 設定，一鍵更新功能暫無法使用。")

# 3. 自定義 CSS - 優化目錄視覺與雙標籤排版
st.markdown("""
    <style>
    /* 確保側邊欄在手機端有足夠寬度與明顯背景 */
    [data-testid="stSidebar"] {
        background-color: #003366;
        min-width: 250px;
    }
    [data-testid="stSidebar"] .stMarkdown p { color: white; font-weight: bold; }
    
    .main { background-color: #f4f7f9; }
    
    /* 庫存卡片 */
    .inventory-card {
        background-color: white; padding: 18px; margin-bottom: 12px;
        border-radius: 15px; border: 1px solid #eef2f6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .card-title { font-size: 1.2rem; font-weight: 800; color: #003366; margin-bottom: 5px; }
    
    /* 雙標籤容器 */
    .tag-container { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
    .tag { padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; }
    .tag-available { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #2e7d32; }
    .tag-special { background-color: #e3f2fd; color: #1565c0; border: 1px solid #1565c0; }
    .tag-none { background-color: #f5f5f5; color: #9e9e9e; }
    
    /* 數據排版 */
    .data-grid { display: flex; flex-wrap: wrap; gap: 15px; border-top: 1px solid #f0f0f0; padding-top: 12px; }
    .data-item { flex: 1; min-width: 65px; }
    .data-label { color: #6c757d; font-size: 0.75rem; display: block; }
    .data-value { font-size: 1rem; font-weight: bold; color: #003366; }
    </style>
    """, unsafe_allow_html=True)

# 4. GitHub API 更新函數
def update_github(data_frame):
    url = f"https://api.github.com/repos/{REPO}/contents/inventory.csv"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        sha = res.json()['sha']
        csv_content = data_frame.to_csv(index=False).encode('utf-8-sig')
        encoded = base64.b64encode(csv_content).decode('utf-8')
        payload = {"message": f"管理員更新: {datetime.datetime.now()}", "content": encoded, "sha": sha}
        put_res = requests.put(url, json=payload, headers=headers)
        return put_res.status_code == 200
    return False

# 5. 資料處理
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

# --- 目錄導覽 (左側側邊欄) ---
with st.sidebar:
    st.markdown("### 🚗 SUZUKI 導覽選單")
    # 將模式選擇放在醒目的位置
    mode = st.radio("請切換模式：", ["🔍 業務查詢模式", "⚙️ 管理員編輯後台"], index=0)
    st.markdown("---")
    st.info("💡 提示：若目錄縮起，請點擊螢幕左上角的「>」圖示展開。")

# --- 主畫面內容 ---
if mode == "🔍 業務查詢模式":
    st.markdown("<h1 style='text-align:center; color:#003366; margin-top:-30px;'>即時庫存查詢</h1>", unsafe_allow_html=True)
    
    if not df.empty:
        # 統計資訊
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("在庫總數", f"{int(df['在庫數'].sum())}")
        c2.metric("可用差額", f"{int(df['可用/待到'].sum())}")
        c3.metric("領牌車數", f"{int(df['領牌車'].sum())}")
        c4.metric("提車中", f"{int(df['向金鈴提車'].sum())}")
        
        st.markdown("---")
        
        # 篩選區
        with st.expander("🔍 搜尋篩選條件", expanded=False):
            models = sorted(df["車型"].unique())
            sel_models = st.multiselect("車型過濾", models, default=models)
            keyword = st.text_input("關鍵字 (顏色、排序碼、年式)")
            
        f_df = df[df["車型"].isin(sel_models)]
        if keyword:
            f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1)]
        
        # 卡片列表
        for _, row in f_df.sort_values(by=["車型", "年份"], ascending=[True, False]).iterrows():
            # --- 雙標籤邏輯 ---
            has_stock = row['可用/待到'] > 0
            has_special = row['領牌車'] > 0
            
            tag_html = '<div class="tag-container">'
            if has_stock:
                tag_html += '<span class="tag tag-available">✅ 在庫現車</span>'
            if has_special:
                tag_html += '<span class="tag tag-special">🔵 領牌專案</span>'
            if not has_stock and not has_special:
                tag_html += '<span class="tag tag-none">❌ 需預訂</span>'
            tag_html += '</div>'
            
            st.markdown(f"""
                <div class="inventory-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div class="card-title">{row['年份']} {row['車型']}</div>
                        {tag_html}
                    </div>
                    <div class="card-subtitle">顏色：{row['顏色']} | 排序：{row['排序']}</div>
                    <div class="data-grid">
                        <div class="data-item"><span class="data-label">在庫</span><span class="data-value">{row['在庫數']}</span></div>
                        <div class="data-item"><span class="data-label">已配</span><span class="data-value">{row['已配數量']}</span></div>
                        <div class="data-item"><span class="data-label" style="color:#e11b22;">可用</span><span class="data-value" style="color:#e11b22;">{row['可用/待到']}</span></div>
                        <div class="data-item"><span class="data-label" style="color:#1565c0;">領牌車</span><span class="data-value" style="color:#1565c0;">{row['領牌車']}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("<h2 style='text-align:center; color:#e11b22;'>⚙️ 管理員數據後台</h2>", unsafe_allow_html=True)
    if st.text_input("管理員密碼", type="password") == "1234":
        st.write("### 📝 編輯資料表")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
        if st.button("🚀 立即同步至雲端 (一鍵更新)"):
            with st.spinner("同步中..."):
                if update_github(edited_df):
                    st.success("✅ 更新成功！")
                    st.cache_data.clear()
                else:
                    st.error("❌ 更新失敗，請檢查 Secrets。")
