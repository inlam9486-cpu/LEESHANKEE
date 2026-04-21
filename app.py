import streamlit as st
import pandas as pd

# 1. 頁面設定
st.set_page_config(page_title="李兆基小學 5月報更管理", layout="wide")
st.title("🏫 李兆基小學 - 導師報更看板")

# 在側邊欄增加學校選擇
school = st.sidebar.selectbox("切換學校", ["惇裕小學", "李兆基小學", "寶覺小學", "培恩小學"])

if school == "惇裕小學":
    SHEET_ID = "1uqDMMCinyvsSdXAYE1Dh0EZ36qVvrzhKftNHf_-vw7w"
    GID = "997998162"
elif school == "培恩小學":
    SHEET_ID = "1TuoX1adH7QGDNsaAO6VJ_J6UaGtH6os50xuGb5v-JgA"
    GID = "577988807"
elif school == "李兆基小學":
    SHEET_ID = "1eT1sIKVmb2YsCYA42kYi6d9hbAO4O0ZhRpHUw3lt78U"
    GID = "904662371"
elif school == "寶覺小學":
    SHEET_ID = "1Ka7H_xZKPOfv73ze8pzwqcWQ6KVDfKh_CT9XYtWAevQ"
    GID = "1758950517"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    return df

try:
    df = load_data()
    
    # 自動識別欄位
    name_col = next((col for col in df.columns if '姓名' in col or 'name' in col.lower()), df.columns[1])
    phone_col = next((col for col in df.columns if '電話' in col or 'Phone' in col), df.columns[2])
    date_columns = [col for col in df.columns if '2026' in col]

    # --- 側邊欄：導師搜尋 ---
    st.sidebar.header("管理功能")
    all_tutors = df[name_col].dropna().unique()
    selected_tutor = st.sidebar.selectbox("🔍 搜尋導師紀錄", all_tutors)

    # --- 主畫面 ---
    tab1, tab2 = st.tabs(["🗓️ 每日報更概覽", "👤 導師個人統計"])

    with tab1:
        st.subheader("選擇日期查看當天導師")
        target_date = st.selectbox("請選擇日期", date_columns)
        daily_attending = df[df[target_date].notna()][[name_col, phone_col, target_date]]
        daily_attending.columns = ['導師姓名', '電話', '報更時段/備註']
        
        if not daily_attending.empty:
            st.success(f"{target_date} 共有 {len(daily_attending)} 位導師")
            st.dataframe(daily_attending, use_container_width=True)
        else:
            st.info("當天暫時沒有導師報更。")

    with tab2:
        st.subheader(f"{selected_tutor} 的報更詳情")
        tutor_row = df[df[name_col] == selected_tutor]
        tutor_schedule = []
        for date in date_columns:
            status = tutor_row[date].values[0]
            if pd.notna(status):
                tutor_schedule.append({"日期": date, "內容/時段": status})
        
        if tutor_schedule:
            st.metric("本月總報更天數", len(tutor_schedule))
            st.table(pd.DataFrame(tutor_schedule))
        else:
            st.warning("該導師本月尚未有報更紀錄。")

except Exception as e:
    st.error("讀取試算表失敗，請確保 Google 試算表權限已設為「知道連結的人即可檢視」。")
