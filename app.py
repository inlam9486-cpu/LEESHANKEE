import streamlit as st
import pandas as pd
import time

# 1. 頁面設定
st.set_page_config(page_title="全港小學導師報更管理系統", layout="wide")

# --- 側邊欄：管理選單 ---
st.sidebar.header("🏫 系統管理")

# 增加一個手動刷新按鈕，點擊後會清除所有快取
if st.sidebar.button("🔄 立即同步最新資料"):
    st.cache_data.clear()
    st.rerun()

mode = st.sidebar.radio("模式選擇", ["固定學校", "手動輸入新月份 ID"])

if mode == "固定學校":
    school = st.sidebar.selectbox("切換學校", ["惇裕小學", "培恩小學", "李兆基小學", "寶覺小學"])
    config = {
        "惇裕小學": {"id": "1uqDMMCinyvsSdXAYE1Dh0EZ36qVvrzhKftNHf_-vw7w", "gid": "997998162"},
        "培恩小學": {"id": "1TuoX1adH7QGDNsaAO6VJ_J6UaGtH6os50xuGb5v-JgA", "gid": "577988807"},
        "李兆基小學": {"id": "1eT1sIKVmb2YsCYA42kYi6d9hbAO4O0ZhRpHUw3lt78U", "gid": "904662371"},
        "寶覺小學": {"id": "1Ka7H_xZKPOfv73ze8pzwqcWQ6KVDfKh_CT9XYtWAevQ", "gid": "1758950517"}
    }
    SHEET_ID = config[school]["id"]
    GID = config[school]["gid"]
    st.title(f"🏫 {school} - 報更即時看板")
else:
    SHEET_ID = st.sidebar.text_input("輸入 Sheet ID")
    GID = st.sidebar.text_input("輸入 GID", value="0")
    st.title("📅 自定義月份報更看板")

# --- 強制更新邏輯 ---
# 在網址加入隨機時間戳，繞過 Google 的伺服器緩存
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}&cache_bust={int(time.time())}"

@st.cache_data(ttl=5) # 快取時間縮短至 5 秒
def fetch_data(url):
    # 這裡加入一個隨機參數確保每次請求都是新鮮的
    return pd.read_csv(url)

if SHEET_ID:
    try:
        df = fetch_data(csv_url)
        
        # 智慧欄位偵測
        name_col = next((c for c in df.columns if '姓名' in c or 'name' in c.lower()), df.columns[1])
        phone_col = next((c for c in df.columns if '電話' in c or 'Phone' in c), df.columns[2])
        date_cols = [c for c in df.columns if any(x in c for x in ['/', '2026', '月', '('])]

        # 側邊欄搜尋
        st.sidebar.markdown("---")
        tutors = df[name_col].dropna().unique()
        sel_tutor = st.sidebar.selectbox("🔍 搜尋導師", tutors)

        # 顯示最後更新時間
        st.caption(f"最後同步時間：{time.strftime('%H:%M:%S')}")

        tab1, tab2 = st.tabs(["🗓️ 每日概覽", "👤 個人統計"])
        # ... (後續 tab1, tab2 的顯示邏輯保持不變) ...
        with tab1:
            if date_cols:
                target = st.selectbox("選擇日期", date_cols)
                daily = df[df[target].notna()][[name_col, phone_col, target]]
                daily.columns = ['導師姓名', '電話', '報更內容']
                st.success(f"{target} 共有 {len(daily)} 位導師")
                st.dataframe(daily, use_container_width=True)
            
        with tab2:
            st.subheader(f"{sel_tutor} 的報更詳情")
            t_data = df[df[name_col] == sel_tutor]
            schedule = [{"日期": d, "內容": t_data[d].values[0]} for d in date_cols if pd.notna(t_data[d].values[0])]
            if schedule:
                st.metric("本月總天數", len(schedule))
                st.table(pd.DataFrame(schedule))

    except Exception as e:
        st.error("🚨 無法取得最新資料")
        st.write("請檢查：")
        st.write("1. 試算表權限是否為『知道連結的人即可檢視』。")
        st.write("2. 是否已在試算表執行『檔案 > 共用 > 發佈到網路』。")
