import streamlit as st
import datetime
from datetime import timedelta
from streamlit_calendar import calendar

# 1. 修正網頁標題為 THSR
st.set_page_config(page_title="THSR 省錢計算器", page_icon="🚄", layout="centered")

# --- CSS 樣式美化 ---
st.markdown("""
<style>
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. 頂部標題 (移除破圖的 col，直接顯示文字，並改為 THSR) ---
st.markdown('### 🚄 THSR 省錢計算器')
st.markdown('<div style="color: gray; font-size: 14px; margin-bottom: 20px;">輕鬆點選上班日，自動算出最划算的高鐵票！</div>', unsafe_allow_html=True)

# --- 卡片 1：參數設定 ---
with st.expander("⚙️ 票價參數", expanded=False):
    c1, c2, c3 = st.columns(3)
    price_single = c1.number_input("單程票($)", value=125)
    price_multi = c2.number_input("回數票10次($)", value=1025)
    price_periodic = c3.number_input("定期票30天($)", value=3675)

# --- 啟動記憶體 (Session State) ---
today = datetime.date.today()

if "work_dates" not in st.session_state:
    initial_dates = []
    for i in range(30):
        temp_date = today + timedelta(days=i)
        if temp_date.weekday() < 5: 
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
        "buttonText": {
            "today": "Today"
        },
        "initialView": "dayGridMonth",
        "selectable": True,
        "timeZone": "local" 
    }
    
    state = calendar(
        events=events,
        options=options,
        key="interactive_calendar",
    )

    if state and "callback" in state:
        if state["callback"] == "dateClick":
            raw_date = state["dateClick"].get("date", "")
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
                st.rerun() 
                
        elif state["callback"] == "eventClick":
            clicked_event_id = state["eventClick"]["event"]["id"]
            if clicked_event_id in st.session_state.work_dates:
                st.session_state.work_dates.remove(clicked_event_id)
                st.rerun() 

    work_days = len(st.session_state.work_dates)

# --- 卡片 3：計算結果 ---
st.markdown("---")
with st.container():
    st.subheader("📊 計算結果")
    
    if work_days > 0:
        trips = work_days * 2
        
        price_per_ride = price_multi / 10
        cost_long_term = trips * price_per_ride 
        full_books = trips // 10
        remainder_trips = trips % 10
        cost_strict = (full_books * price_multi) + (remainder_trips * price_single)

        tab1, tab2 = st.tabs(["💼 長期通勤模式 (推薦)", "📅 單月結算模式 (不續搭)"])
        
        # ==========================================
        # 分頁 1：長期通勤模式
        # ==========================================
        with tab1:
            if cost_long_term >= price_periodic:
                st.success("🏆 **長期最佳：直接購買【定期票】最省！**")
                diff1 = cost_long_term - price_periodic
            else:
                st.info("🏆 **長期最佳：使用【回數票】最省！**")
                diff1 = price_periodic - cost_long_term
                
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="result-metric"><div class="result-label">上班天數</div><div class="result-value">{work_days} 天</div><div class="result-label">共 {trips} 趟</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="result-metric"><div class="result-label">方案A: 回數票成本</div><div class="result-value">${int(cost_long_term)}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="result-metric"><div class="result-label">方案B: 定期票成本</div><div class="result-value">${int(price_periodic)}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background-color: #3B82F6; color: white; border-radius: 5px; padding: 10px; text-align: center; margin-top: 15px; font-weight: bold;">
                💡 {'買定期票省下：' if (cost_long_term >= price_periodic) else '買回數票省下：'}**${int(abs(diff1))}** <br>
                <span style="font-size: 12px; font-weight: normal;">(註：以每趟均價 ${price_per_ride} 計算)</span>
            </div>
            """, unsafe_allow_html=True)

            if cost_long_term < price_periodic and remainder_trips > 0:
                st.markdown(f"""
                <div style="margin-top: 15px; padding: 15px; border-left: 4px solid #F59E0B; background-color: #FEF3C7; border-radius: 4px;">
                    <b>💡 專家接續買法建議：</b><br>
                    <span style="font-size: 14px; color: #555;">
                    前 {full_books * 10} 趟請先購買 <b>{full_books} 組回數票</b>。<br>
                    剩下的 <b>{remainder_trips} 趟絕對不要買單程票！</b> 請在第 {full_books * 10 + 1} 趟時，重新檢視未來一個月的班表：<br>
                    👉 若未來 30 天上班 ≥ 18天 (36趟)，請接續買<b>定期票</b>。<br>
                    👉 若未滿 18 天，請接續買<b>第 {full_books + 1} 組回數票</b>。
                    </span>
                </div>
                """, unsafe_allow_html=True)

        # ==========================================
        # 分頁 2：單月結算模式
        # ==========================================
        with tab2:
            if cost_strict >= price_periodic:
                st.success("🏆 **單月最佳：購買【定期票】最省！**")
                diff2 = cost_strict - price_periodic
            else:
                st.info("🏆 **單月最佳：混搭【回數票+單程票】最省！**")
                diff2 = price_periodic - cost_strict
                
            c4, c5, c6 = st.columns(3)
            c4.markdown(f'<div class="result-metric"><div class="result-label">上班天數</div><div class="result-value">{work_days} 天</div><div class="result-label">共 {trips} 趟</div></div>', unsafe_allow_html=True)
            c5.markdown(f'<div class="result-metric"><div class="result-label">方案A: 混搭總花費</div><div class="result-value">${int(cost_strict)}</div></div>', unsafe_allow_html=True)
            c6.markdown(f'<div class="result-metric"><div class="result-label">方案B: 定期票成本</div><div class="result-value">${int(price_periodic)}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background-color: #10B981; color: white; border-radius: 5px; padding: 10px; text-align: center; margin-top: 15px; font-weight: bold;">
                💡 {'定期票省下：' if (cost_strict >= price_periodic) else '混搭方案省下：'}**${int(abs(diff2))}** <br>
                <span style="font-size: 12px; font-weight: normal;">(買法：{full_books} 組回數票 + {remainder_trips} 張單程票)</span>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.warning("請在上方日曆點選您的上班日喔！")
