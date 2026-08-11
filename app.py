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
        background-color: white; padding: 18px; margin-bottom: 15px;
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

# 4. GitHub 自動更新函數
def update_github(data_frame):
    url = f"https://api.github.com/repos/{REPO}/contents/inventory.csv"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        sha = res.json()['sha']
        
        # 清理欄位並重算可用庫存
        save_df = data_frame.copy()
        save_df["可用"] = save_df["在庫數"].astype(int) - save_df["已配數量"].astype(int)
        save_df = save_df.drop(columns=['可用'], errors='ignore')
        
        csv_content = save_df.to_csv(index=False).encode('utf-8-sig')
        encoded = base64.b64encode(csv_content).decode('utf-8')
        payload = {"message": f"Update: {datetime.datetime.now()}", "content": encoded, "sha": sha}
        return requests.put(url, json=payload, headers=headers).status_code == 200
    return False

# 5. 資料讀取 (自動過濾空白無效列)
@st.cache_data(ttl=1)
def load_data():
    try:
        data = pd.read_csv("inventory.csv")
        
        if "車型" in data.columns:
            data = data[data["車型"].notna()]
            data = data[data["車型"].astype(str).str.strip() != "0"]
            data = data[data["車型"].astype(str).str.strip() != ""]
            
        data = data.fillna(0)
        
        if "年份" in data.columns:
            data["年份"] = data["年份"].astype(str).str.replace(".0", "", regex=False)
            
        num_cols = ["在庫數", "已配數量", "向金鈴提車", "領牌車"]
        for col in num_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
                
        data["可用"] = data["在庫數"] - data["已配數量"]
        return data.reset_index(drop=True)
    except: 
        return pd.DataFrame()

df = load_data()

# 初始化 session_state 儲存動態資料
if 'admin_df' not in st.session_state or st.session_state.admin_df.empty:
    st.session_state.admin_df = df.copy()

# --- 側邊欄 ---
with st.sidebar:
    st.markdown("## 🚗 選單控制")
    mode = st.radio("功能切換", ["🔍 業務查詢模式", "⚙️ 直覺式管理後台"])
    st.markdown("---")

# --- 主畫面 1：業務查詢模式 ---
if mode == "🔍 業務查詢模式":
    st.markdown("<h2 style='text-align:center; color:#003366;'>SUZUKI 庫存查詢</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        try:
            url_params = st.query_params.to_dict()
            url_model = url_params.get("model") or url_params.get("q")
        except:
            url_model = None
        
        models = sorted(df["車型"].unique())
        matched_models = []
        if url_model:
            search_key = str(url_model).upper().strip()
            matched_models = [m for m in models if search_key in str(m).upper()]

        with st.expander("🔍 搜尋篩選", expanded=(not url_model)):
            default_sel = matched_models if url_model and matched_models else models
            sel_m = st.multiselect("車型篩選", models, default=default_sel)
            key = st.text_input("搜尋關鍵字 (顏色/排序碼/年式)")
        
        f_df = df[df["車型"].isin(sel_m)]
        if key: 
            f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(key)).any(axis=1)]

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

# --- 主畫面 2：直覺式管理後台 (名稱修改 + 刪除車型功能) ---
else:
    st.markdown("<h2 style='text-align:center; color:#e11b22;'>⚙️ 直覺式庫存管理後台</h2>", unsafe_allow_html=True)
    
    if st.text_input("驗證管理密碼", type="password") == "1234":
        
        # 置頂同步按鈕
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            st.info("💡 提示：修改名稱、顏色、數量或點擊刪除後，請點擊右側「一鍵同步」更新至雲端。")
        with col_btn2:
            if st.button("🚀 一鍵同步更新至雲端", type="primary", use_container_width=True):
                with st.spinner("同步中..."):
                    if update_github(st.session_state.admin_df):
                        st.success("✅ 更新成功！")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ 更新失敗，請檢查金鑰或網路。")

        st.markdown("---")
        
        # 【新增車型專區】
        with st.expander("➕ 點擊此處新增全新車型/顏色", expanded=False):
            st.markdown("##### 填寫新車型資訊")
            col_a, col_b, col_c = st.columns(3)
            add_model = col_a.text_input("車型名稱 (例如 VITARA S ALLGRIP)", "", key="add_m")
            add_color = col_b.text_input("顏色 (例如 白)", "", key="add_c")
            add_year = col_c.text_input("年份 (例如 正26)", "正26", key="add_y")
            
            col_d, col_e, col_f, col_g, col_h = st.columns(5)
            add_sort = col_d.text_input("排序碼 / 狀態", "預留", key="add_s")
            add_stock = col_e.number_input("在庫數", min_value=0, value=0, key="add_st")
            add_assigned = col_f.number_input("已配數量", min_value=0, value=0, key="add_as")
            add_special = col_g.number_input("領牌車", min_value=0, value=0, key="add_sp")
            add_pull = col_h.number_input("提車中", min_value=0, value=0, key="add_p")
            
            if st.button("➕ 確認新增此筆車型資料", use_container_width=True):
                if add_model and add_color:
                    new_row = {
                        "車型": add_model.strip(),
                        "顏色": add_color.strip(),
                        "年份": add_year.strip(),
                        "排序": add_sort.strip(),
                        "在庫數": int(add_stock),
                        "已配數量": int(add_assigned),
                        "領牌車": int(add_special),
                        "向金鈴提車": int(add_pull),
                        "可用": int(add_stock) - int(add_assigned)
                    }
                    new_df = pd.DataFrame([new_row])
                    st.session_state.admin_df = pd.concat([new_df, st.session_state.admin_df], ignore_index=True)
                    st.success(f"已新增【{add_year} {add_model} ({add_color})】，請點擊頂部「一鍵同步更新至雲端」！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請至少填寫「車型名稱」與「顏色」。")

        st.markdown("---")
        
        # 後台搜尋過濾
        search_admin = st.text_input("🔍 快速尋找欲修改的車型/顏色/排序碼", "")
        
        edit_df = st.session_state.admin_df.copy()
        if search_admin:
            filtered_indices = edit_df[edit_df.astype(str).apply(lambda x: x.str.contains(search_admin, case=False)).any(axis=1)].index
        else:
            filtered_indices = edit_df.index

        # 編輯卡片列表
        for idx in filtered_indices:
            row = edit_df.loc[idx]
            
            with st.container():
                # 標題與【刪除按鈕】
                col_title, col_del = st.columns([3, 1])
                with col_title:
                    st.markdown(f"#### 🚗 車型項目卡片")
                with col_del:
                    if st.button("🗑️ 刪除這台車", key=f"del_{idx}"):
                        st.session_state.admin_df = st.session_state.admin_df.drop(index=idx).reset_index(drop=True)
                        st.warning("已移除該筆條目，請務必點擊頂部「一鍵同步更新至雲端」生效！")
                        st.rerun()
                
                # 第一排：自由修改【車型名稱 / 顏色 / 年份 / 排序碼】
                ca, cb, cc, cd = st.columns([2, 1, 1, 2])
                new_model = ca.text_input("車型名稱 (可改名)", value=str(row["車型"]), key=f"model_{idx}")
                new_color = cb.text_input("顏色", value=str(row["顏色"]), key=f"color_{idx}")
                new_year = cc.text_input("年份", value=str(row["年份"]), key=f"year_{idx}")
                new_sort = cd.text_input("排序 / 狀態備註", value=str(row["排序"]), key=f"sort_{idx}")
                
                # 第二排：數字微調 (+ / - 按鈕)
                c1, c2, c3, c4 = st.columns(4)
                new_stock = c1.number_input("在庫數", min_value=0, value=int(row["在庫數"]), key=f"stock_{idx}")
                new_assigned = c2.number_input("已配數量", min_value=0, value=int(row["已配數量"]), key=f"assign_{idx}")
                new_special = c3.number_input("領牌車", min_value=0, value=int(row["領牌車"]), key=f"special_{idx}")
                new_pull = c4.number_input("提車中", min_value=0, value=int(row["向金鈴提車"]), key=f"pull_{idx}")
                
                # 即時更新暫存
                st.session_state.admin_df.loc[idx, "車型"] = new_model.strip()
                st.session_state.admin_df.loc[idx, "顏色"] = new_color.strip()
                st.session_state.admin_df.loc[idx, "年份"] = new_year.strip()
                st.session_state.admin_df.loc[idx, "排序"] = new_sort.strip()
                st.session_state.admin_df.loc[idx, "在庫數"] = new_stock
                st.session_state.admin_df.loc[idx, "已配數量"] = new_assigned
                st.session_state.admin_df.loc[idx, "領牌車"] = new_special
                st.session_state.admin_df.loc[idx, "向金鈴提車"] = new_pull
                
                st.markdown("---")
