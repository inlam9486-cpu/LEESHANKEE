import streamlit as st
import pandas as pd
import time

# 1. 頁面設定
st.set_page_config(page_title="全港小學導師報更管理系統", layout="wide")

# --- 側邊欄：管理選單 ---
st.sidebar.header("🏫 系統管理")
mode = st.sidebar.radio("模式選擇", ["固定學校", "手動輸入新月份 ID"])

if mode == "固定學校":
    school = st.sidebar.selectbox("切換學校", ["惇裕小學", "培恩小學", "李兆基小學", "寶覺小學"])
    # 根據你的 User Summary 資料預設 ID
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
    st.sidebar.warning("請從 Google 試算表網址中複製 ID")
    SHEET_ID = st.sidebar.text_input("輸入 Sheet ID (網址中 /d/ 後的那串文字)")
    GID = st.sidebar.text_input("輸入 GID (網址最後 gid= 後的數字)", value="0")
    st.title("📅 自定義月份報更看板")

# --- 自動讀取邏輯 ---
# 這裡使用 export 模式並加上 t={time.time()} 來強制 Google 提供最新資料
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}&t={int(time.time())}"

@st.cache_data(ttl=10) # 每 10 秒就失效，實現近乎實時的自動更新
def fetch_data(url):
    return pd.read_csv(url)

if SHEET_ID:
    try:
        df = fetch_data(csv_url)
        
        # 智慧欄位偵測 (適應不同學校的表單標題)
        name_col = next((c for c in df.columns if '姓名' in c or 'name' in c.lower()), df.columns[1])
        phone_col = next((c for c in df.columns if '電話' in c or 'Phone' in c), df.columns[2])
        date_cols = [c for c in df.columns if any(x in c for x in ['/', '2026', '月', '('])]

        # 側邊欄：搜尋
        st.sidebar.markdown("---")
        tutors = df[name_col].dropna().unique()
        sel_tutor = st.sidebar.selectbox("🔍 搜尋導師", tutors)

        tab1, tab2 = st.tabs(["🗓️ 每日概覽", "👤 個人統計"])

        with tab1:
            if date_cols:
                target = st.selectbox("選擇日期", date_cols)
                # 篩選當天有填資料的人
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
        st.error("🚨 系統自動讀取失敗")
        st.info("請檢查該試算表是否已開啟『知道連結的人即可檢視』。")
        if st.button("手動重新嘗試連線"):
            st.cache_data.clear()
            st.rerun()
