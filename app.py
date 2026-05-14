import streamlit as st
import pandas as pd
import time

# 1. 頁面設定
st.set_page_config(page_title="全港小學導師報更管理系統", layout="wide")

# --- 側邊欄：管理選單 ---
st.sidebar.header("🏫 系統管理")

# 強制重新讀取按鈕
if st.sidebar.button("🔄 立即同步最新資料"):
    st.cache_data.clear()
    st.rerun()

# 選擇學校
school = st.sidebar.selectbox("請選擇學校", ["李兆基小學", "培恩小學", "寶覺小學", "惇裕小學"])

# 2. 學校資料庫 (根據你提供的所有最新連結修正)
config = {
    "李兆基小學": {
        "id": "1APH8BvGbsLcGO-bLgt9xtjStV6vvrFJsZYJ_7GGT--E", 
        "gid": "834994642"
    },
    "培恩小學": {
        "id": "18eAOSQJDRgmK3zgCXGXAwp62tCjDoENbmaAKVE4TmCE", 
        "gid": "840129368"
    },
    "寶覺小學": {
        "id": "18eAOSQJDRgmK3zgCXGXAwp62tCjDoENbmaAKVE4TmCE", 
        "gid": "840129368"
    },
    "惇裕小學": {
        "id": "1uqDMMCinyvsSdXAYE1Dh0EZ36qVvrzhKftNHf_-vw7w", 
        "gid": "997998162"
    }
}

SHEET_ID = config[school]["id"]
GID = config[school]["gid"]

st.title(f"🏫 {school} - 報更即時看板")

# 使用隨機參數 cache_bust 強制 Google 更新資料
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}&t={int(time.time())}"

@st.cache_data(ttl=5)
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(csv_url)
    
    # 智慧識別欄位
    name_col = next((c for c in df.columns if '姓名' in c or 'name' in c.lower()), df.columns[1])
    phone_col = next((c for c in df.columns if '電話' in c or 'Phone' in c), df.columns[2])
    # 找包含日期格式的欄位
    date_cols = [c for c in df.columns if any(x in c for x in ['/', '2026', '月', '('])]

    # 側邊欄：搜尋
    st.sidebar.markdown("---")
    tutors = df[name_col].dropna().unique()
    sel_tutor = st.sidebar.selectbox("🔍 搜尋導師", tutors)
    st.caption(f"數據最後同步：{time.strftime('%H:%M:%S')}")

    tab1, tab2 = st.tabs(["🗓️ 每日概覽", "👤 個人統計"])

    with tab1:
        if date_cols:
            target = st.selectbox("選擇日期", date_cols)
            # 只顯示該日期有填寫內容的人
            daily = df[df[target].notna()][[name_col, phone_col, target]]
            daily.columns = ['導師姓名', '電話', '報更內容']
            st.success(f"{target} 共有 {len(daily)} 位導師報更")
            st.dataframe(daily, use_container_width=True)
        else:
            st.warning("此表單中暫時找不到日期欄位。")

    with tab2:
        st.subheader(f"{sel_tutor} 的報更詳情")
        t_data = df[df[name_col] == sel_tutor]
        schedule = []
        for d in date_cols:
            if d in t_data.columns:
                val = t_data[d].values[0]
                if pd.notna(val):
                    schedule.append({"日期": d, "內容": val})
        
        if schedule:
            st.metric("本月總報更天數", len(schedule))
            st.table(pd.DataFrame(schedule))
        else:
            st.info("該導師本月尚未報更紀錄。")

except Exception as e:
    st.error("🚨 讀取資料失敗")
    st.info("請檢查：\n1. 該試算表是否已開啟『知道連結的人即可檢視』權限。\n2. 網址是否有變動。")
