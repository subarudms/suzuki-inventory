import streamlit as st
import pandas as pd
import datetime

# 1. 頁面專業配置 (設定 Logo 和佈局)
st.set_page_config(
    page_title="SUZUKI 車輛庫存儀表板",
    page_icon="🚗", # 可以換成 Suzuki Logo 的連結
    layout="wide",
    initial_sidebar_state="collapsed" # 手機端預設收起側邊欄，增加專業感
)

# 2. 自定義專業 CSS 樣式 (賦予 Suzuki 企業色彩)
st.markdown("""
    <style>
        /* 全域背景顏色 (淡灰色) */
        .main { background-color: #f8f9fa; }
        
        /* 專業標題樣式 */
        .main-title {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #003366; /* Suzuki 深藍色 */
            font-weight: 800;
            text-align: center;
            padding: 20px 0;
            border-bottom: 3px solid #e11b22; /* Suzuki 紅色 */
            margin-bottom: 30px;
        }
        
        /* 側邊欄樣式 */
        [data-testid="stSidebar"] {
            background-color: #003366;
            color: white;
        }
        [data-testid="stSidebar"] .stMarkdown h2 { color: white; }
        
        /* 數據卡片樣式 */
        div[data-testid="stMetric"] {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-left: 6px solid #e11b22; /* 左側紅色飾條 */
            transition: transform 0.2s;
        # 4. 讀取資料邏輯 (修正後的穩定版本)
@st.cache_data(ttl=120)
def load_data():
    try:
        # 讀取 CSV
        data = pd.read_csv("inventory.csv").fillna(0)
        
        # 數據清理：確保數值欄位為整數
        num_cols = ["在庫數", "向金鈴提車", "領牌車", "已配數量"]
        for col in num_cols:
            if col in data.columns:
                # 移除非數字字元並轉為整數
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        
        # 重新計算待到貨：在庫數 - 已配數量
        if "在庫數" in data.columns and "已配數量" in data.columns:
            data["待到貨/可用"] = data["在庫數"] - data["已配數量"]
        else:
            data["待到貨/可用"] = 0
            
        return data, None # 成功時傳回資料和無錯誤
    except Exception as e:
        return pd.DataFrame(), str(e) # 失敗時傳回空表和錯誤訊息

# 呼叫函數
df, error_msg = load_data()

        # 讀取 CSV
        df = pd.read_csv("inventory.csv").fillna(0)
        
        # 數據清理：確保數值欄位為整數
        num_cols = ["在庫數", "向金鈴提車", "領牌車", "排序"]
        for col in num_cols:
            if col in df.columns:
                # 移除非數字字元 (如排序代碼)
                df[col] = df[col].astype(str).str.extract('(\d+)').fillna(0).astype(int)
        
        # 【修改後的公式】：在庫數 扣 已配數量 (目前報表無已配數量，先假定 0)
        # 如果您有了「已配數量」欄位，請用這行：
        # df["可用差額"] = df["在庫數"] - df["已配數量"]
        
        return df
    except Exception as e:
        return pd.DataFrame(), e

df, error_msg = load_data()

if df.empty:
    st.error(f"⚠️ 資料讀取失敗。請確認 inventory.csv 是否已正確上傳且格式符合。")
    if error_msg:
        st.info(f"技術錯誤訊息：{error_msg}")
else:
    # 5. 專業側邊欄篩選
    st.sidebar.markdown("## 📊 庫存過濾器")
    
    # 車型篩選 (預設全選)
    models = sorted(df["車型"].unique())
    search_model = st.sidebar.multiselect("🚗 選擇車型", options=models, default=models)
    
    # 關鍵字搜尋 (例如搜顏色)
    keyword = st.sidebar.text_input("🔍 搜尋關鍵字 (顏色/代碼)", placeholder="例如: 叢林綠")

    # 資料過濾
    mask = df["車型"].isin(search_model)
    if keyword:
        # 強大搜尋：在所有欄位中搜尋關鍵字
        mask = mask & (df.astype(str).apply(lambda x: x.str.contains(keyword)).any(axis=1))
    
    f_df = df[mask].copy()

    # 6. 專業數據看板 (Metric Cards)
    st.markdown("### 📈 即時統計指標")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("當前總在庫", f"{f_df['在庫數'].sum()} 台", help="目前店內配車數")
    c2.metric("金鈴提車中", f"{f_df['向金鈴提車'].sum()} 台", help="向總代理提車之數量")
    c3.metric("領牌車總數", f"{f_df['領牌車'].sum()} 台", delta=int(f_df['領牌車'].sum()), delta_color="normal")
    c4.metric("篩選種類", f"{len(f_df)} 種")

    st.markdown("---")

    # 7. 表格呈現 (專業專業排序與格式)
    st.markdown("### 📋 詳細庫存清單 (115/04/14 版本)")
    
    # 重新定義欄位顯示順序
    target_cols = ["車型", "顏色", "在庫數", "向金鈴提車", "領牌車", "排序"]
    final_cols = [c for c in target_cols if c in f_df.columns]

    # 美化表格樣式：高亮顯示有現車的行
    def style_dataframe(row):
        return ['background-color: #e3f2fd; font-weight: bold' if row.在庫數 > 0 else 'color: #757575' for _ in row]

    st.dataframe(
        f_df[final_cols].sort_values(by=["車型", "在庫數"], ascending=[True, False]).style.apply(style_dataframe, axis=1), 
        use_container_width=True, 
        hide_index=True
    )

    # 8. 底部資訊列
    st.markdown("---")
    st.caption(f"最後同步時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 此系統僅供陳胤合內部銷售使用。")

