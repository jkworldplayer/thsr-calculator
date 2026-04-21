import streamlit as st
import datetime
from datetime import timedelta
from streamlit_calendar import calendar

# 設定網頁標題、手機圖示與版面配置
st.set_page_config(page_title="THSR 省錢計算器", page_icon="🚄", layout="centered")

# --- 1. CSS 樣式美化 ---
st.markdown("""
<style>
    /* 計算結果卡片的數據顯示樣式 (強制淺藍底、深色字，保持視覺重點) */
    .result-metric {
        background-color: #EEF4FE;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    .result-label {
        font-size: 12px;
        color: #555555 !important;
        margin-bottom: 5px;
    }
    .result-value {
        font-size: 18px;
        font-weight: 700;
        color: #111111 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 頂部標題 ---
col_head1, col_head2 = st.columns([8, 1])
with col_head1:
    st.markdown('### 🚄 THSR 省錢計算器')
    st.markdown('<div style="color: gray; font-size: 14px;">輕鬆點選上班日，自動算出最划算的高鐵票！</div>', unsafe_allow_html=True)
with col_head2:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/main/assets/images/logo.png", width=40)

st.markdown("---")

# --- 卡片 1：參數設定 ---
with st.expander("⚙️ 票價參數", expanded=True):
    # 分成三個欄位，讓單程票、回數票、定期票並排
    c1, c2, c3 = st.columns(3)
    price_single = c1.number_input("單程票($)", value=125)
    price_multi = c2.number_input("回數票10次($)", value=1025)
    price_periodic = c3.number_input("定期票30天($)", value=3675)

# --- 2. 啟動記憶體 (Session State) ---
today = datetime.date.today()

# 如果是第一次打開網頁，就把未來 30 天的平日存進「記憶體」裡
if "work_dates" not in st.session_state:
    initial_dates = []
    # 【修改點 3】將預設天數從 45 改為 30
    for i in range(30):
        temp_date = today + timedelta(days=i)
        if temp_date.weekday() < 5:  # 週一到週五
            initial_dates.append(temp_date.strftime("%Y-%m-%d"))
    st.session_state.work_dates = initial_dates

# --- 卡片 2：上班日選擇 (日曆) ---
with st.container():
    st.subheader("📅 上班日選擇")
    st.markdown("""
    <div style="font-size: 12px; color: gray; margin-bottom: 10px;">
        👉 <b>點擊空白日期</b>可新增，<b>點擊藍色標籤</b>可取消。
    </div>
    """, unsafe_allow_html=True)
    
    events = []
    for d in st.session_state.work_dates:
        events.append({
            "id": d,
            "title": "上班",
            "start": d,
            "color": "#3B82F6",
            "allDay": True
        })
        
    options = {
        "headerToolbar": {
            "left": "prev,next",
            "center": "title",
            "right": "today"
        },
        # 【修改點 1】強制修改按鈕文字為首字母大寫
        "buttonText": {
            "today": "Today"
        },
        "initialView": "dayGridMonth",
        "selectable": True,
        "timeZone": "local" # 嘗試強制日曆使用本地時區
    }
    
    state = calendar(
        events=events,
        options=options,
        key="interactive_calendar",
    )

    # --- [關鍵修復 2] 日曆點擊時區錯誤處理 ---
    if state and "callback" in state:
        if state["callback"] == "dateClick":
            raw_date = state["dateClick"].get("date", "")
            
            # 判斷是否帶有 UTC (Z) 標記，若有則手動加上台灣時區的 8 小時
            if "T" in raw_date and raw_date.endswith("Z"):
                try:
                    dt = datetime.datetime.strptime(raw_date[:19], "%Y-%m-%dT%H:%M:%S")
                    dt += timedelta(hours=8)
                    clicked_date = dt.strftime("%Y-%m-%d")
                except:
                    clicked_date = raw_date[:10]
            else:
                clicked_date = raw_date[:10]
            
            if clicked_date and clicked_date not in st.session_state.work_dates:
                st.session_state.work_dates.append(clicked_date)
                st.rerun() # 重新整理
                
        elif state["callback"] == "eventClick":
            clicked_event_id = state["eventClick"]["event"]["id"]
            if clicked_event_id in st.session_state.work_dates:
                st.session_state.work_dates.remove(clicked_event_id)
                st.rerun() # 重新整理

    work_days = len(st.session_state.work_dates)

# --- 卡片 3：計算結果 ---
st.markdown("---")
with st.container():
    st.subheader("📊 計算結果")
    
    if work_days > 0:
        trips = work_days * 2
        cost_single = trips * price_single
        price_per_ride = price_multi / 10
        cost_multi = trips * price_per_ride
        
        # 判斷最佳方案
        if cost_multi >= price_periodic:
            st.success("🏆 **最佳方案：購買【定期票】最省！**")
            diff = cost_multi - price_periodic
        else:
            st.info("🏆 **最佳方案：繼續買【回數票】最省！**")
            diff = price_periodic - cost_multi
            
        # 版面配置改為 3 欄
        c1, c2, c3 = st.columns(3)
        
        c1.markdown(f"""
        <div class="result-metric">
            <div class="result-label">上班天數</div>
            <div class="result-value">{work_days} 天</div>
            <div class="result-label">共 {trips} 趟</div>
        </div>
        """, unsafe_allow_html=True)
        
        c2.markdown(f"""
        <div class="result-metric">
            <div class="result-label">方案A: 回數票總額</div>
            <div class="result-value">${int(cost_multi)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        c3.markdown(f"""
        <div class="result-metric">
            <div class="result-label">方案B: 定期票總額</div>
            <div class="result-value">${int(price_periodic)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 顯示省下金額的藍色高亮標籤 (加入全程買單程票的資訊當作對照)
        st.markdown(f"""
        <div style="background-color: #3B82F6; color: white; border-radius: 5px; padding: 10px; text-align: center; margin-top: 15px; font-weight: bold;">
            💡 {'買定期票省下：' if (cost_multi >= price_periodic) else '買回數票省下：'}**${int(abs(diff))}** <br>
            <span style="font-size: 12px; font-weight: normal;">(註：若全買單程票需花費 ${int(cost_single)})</span>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.warning("請在上方日曆點選您的上班日喔！")
