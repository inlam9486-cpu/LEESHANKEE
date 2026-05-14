import streamlit as st
import pandas as pd
import re

# 1. 頁面設定
st.set_page_config(page_title="全港小學導師報更管理系統", layout="wide")

# --- 側邊欄：管理模式 ---
st.sidebar.header("🏫 學校與資料管理")
mode = st.sidebar.radio("選擇模式", ["固定學校快捷鍵", "貼上新月份網址"])

if mode == "固定學校快捷鍵":
    school = st.sidebar.selectbox("請選擇學校", ["惇裕小學", "培恩小學", "李兆基小學", "寶覺小學"])
    
    # 這裡保留你原本設定好的 ID
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
    display_title = f"🏫 {school} - 報更即時看板"

else:
    # --- 自動解析網址模式 ---
    st.sidebar.info("💡 每月更新時，只需在此貼上新的 Google 試算表網址。")
    input_url = st.sidebar.text_input("請貼上新的回應表網址：", placeholder="https://docs.google.com/spreadsheets/d/...")
    
    if input_url:
        try:
            # 使用正則表達式自動提取 ID 和 GID
            SHEET_ID = re.search(r"/d/([^/]+)", input_url).group(1)
            gid_match = re.search(r"gid=(\d+)", input_url)
            GID = gid_match.group(1) if gid_match else "0"
            display_title = "📅 自定義月份報更看板"
        except:
            st.sidebar.error("❌ 網址格式解析失敗，請確保是正確的 Google 試算表網址。")
            st.stop()
    else:
        st.warning("👈 請在左側欄位貼上本月的新網址。")
        st.stop()

# --- 核心邏輯 ---
st.title(display_title)
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60) # 每分鐘自動檢查一次更新
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(csv_url)
    
    # 智慧識別欄位
    name_col = next((col for col in df.columns if '姓名' in col or 'name' in col.lower()), df.columns[1])
    phone_col = next((col for col in df.columns if '電話' in col or 'Phone' in col), df.columns[2])
    # 找包含日期格式或 2026 字樣的欄位
    date_columns = [col for col in df.columns if any(x in col for x in ['/', '2026', '月', '('])]

    # 側邊欄：導師管理
    st.sidebar.markdown("---")
    all_tutors = df[name_col].dropna().unique()
    selected_tutor = st.sidebar.selectbox("🔍 搜尋導師紀錄", all_tutors)

    tab1, tab2 = st.tabs(["🗓️ 每日報更概覽", "👤 導師個人統計"])

    with tab1:
        if date_columns:
            target_date = st.selectbox("選擇日期", date_columns)
            daily_attending = df[df[target_date].notna()][[name_col, phone_col, target_date]]
            daily_attending.columns = ['導師姓名', '電話', '報更時段/備註']
            
            if not daily_attending.empty:
                st.success(f"{target_date} 共有 {len(daily_attending)} 位導師報更")
                st.dataframe(daily_attending, use_container_width=True)
            else:
                st.info("當天暫時沒有導師報更。")
        else:
            st.warning("⚠️ 找不到日期欄位，請檢查試算表標題。")

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
            st.warning("該導師尚未有報更紀錄。")

except Exception as e:
    st.error("🚨 讀取失敗：可能是權限未開啟或網址有誤。")
    st.info("請確保該試算表的權限設為「知道連結的人即可檢視」。")
