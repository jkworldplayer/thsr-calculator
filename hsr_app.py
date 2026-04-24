import streamlit as st
import datetime
from datetime import timedelta
from streamlit_calendar import calendar

# 設定網頁標題
st.set_page_config(page_title="THSR 省錢計算器", page_icon="🚄", layout="centered")

# --- 台灣國定假日資料庫 (2024-2026) ---
def get_taiwan_holidays():
    return [
        # 2024 假日
        "2024-01-01", "2024-02-08", "2024-02-09", "2024-02-10", "2024-02-11", "2024-02-12", "2024-02-13", "2024-02-14",
        "2024-02-28", "2024-04-04", "2024-04-05", "2024-06-10", "2024-09-17", "2024-10-10",
        # 2025 假日
        "2025-01-01", "2025-01-27", "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31", "2025-02-01", "2025-02-02",
        "2025-02-28", "2025-04-03", "2025-04-04", "2025-05-01", "2025-05-31", "2025-10-06", "2025-10-10",
        # 2026 假日
        "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20", "2026-02-21", "2026-02-22",
        "2026-02-28", "2026-04-02", "2026-04-03", "2026-05-01", "2026-06-19", "2026-09-25", "2026-10-10"
    ]

# --- CSS 樣式美化 ---
st.markdown("""
<style>
    .timeline-card { border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; margin-bottom: 12px; background-color: #FFFFFF; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .timeline-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px dashed #E5E7EB; padding-bottom: 8px; }
    .timeline-title { font-weight: 700; font-size: 16px; color: #1F2937; }
    .badge-blue { background-color: #DBEAFE; color: #1D4ED8; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
    .badge-green { background-color: #D1FAE5; color: #059669; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
    .badge-gray { background-color: #F3F4F6; color: #4B5563; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown('### 🚄 THSR 月票排班管家')

# --- 卡片 1：參數設定 ---
with st.expander("⚙️ 參數與起始日設定", expanded=False):
    c1, c2, c3 = st.columns(3)
    price_single = c1.number_input("單程票($)", value=125)
    price_multi = c2.number_input("回數票10次($)", value=1025)
    price_periodic = c3.number_input("定期票30天($)", value=3675)
    
    st.markdown("---")
    c4, c5 = st.columns([2, 1])
    today = datetime.date.today()
    start_date = c4.date_input("推算起始日", value=today)
    
    if c5.button("🔄 重新生成半年平日"):
        new_dates = []
        for i in range(180):
            d = start_date + timedelta(days=i)
            if d.weekday() < 5: new_dates.append(d.strftime("%Y-%m-%d"))
        st.session_state.work_dates = new_dates
        st.rerun()

# --- 啟動記憶體 ---
if "work_dates" not in st.session_state:
    st.session_state.work_dates = []

# --- 卡片 2：日曆與快速操作 ---
with st.container():
    st.subheader("📅 點擊日期設定排班")
    
    # --- 新增快速操作按鈕區 ---
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1.5])
    
    if btn_col1.button("🗑️ 一鍵清除"):
        st.session_state.work_dates = []
        st.rerun()
        
    if btn_col2.button("🎌 標記假日休假"):
        holidays = get_taiwan_holidays()
        # 移除與國定假日重疊的上班日
        st.session_state.work_dates = [d for d in st.session_state.work_dates if d not in holidays]
        st.success("已自動移除國定假日！")
        st.rerun()

    st.markdown("""<div style="font-size: 12px; color: gray; margin-bottom: 10px;">👉 <b>點擊空白日期</b>可新增，<b>點擊標籤</b>可取消。</div>""", unsafe_allow_html=True)
    
    events = [{"id": d, "title": "上班", "start": d, "color": "#3B82F6", "allDay": True} 
              for d in st.session_state.work_dates if d >= start_date.strftime("%Y-%m-%d")]
        
    options = {
        "headerToolbar": {"left": "prev,next", "center": "title", "right": "today"},
        "buttonText": {"today": "Today"},
        "initialView": "dayGridMonth",
        "selectable": True,
        "timeZone": "local" 
    }
    
    state = calendar(events=events, options=options, key="thsr_calendar")

    if state and "callback" in state:
        if state["callback"] == "dateClick":
            raw_date = state["dateClick"].get("date", "")
            # 時區偏移修復邏輯
            if "T" in raw_date and raw_date.endswith("Z"):
                dt = datetime.datetime.strptime(raw_date[:19], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=8)
                clicked_date = dt.strftime("%Y-%m-%d")
            else:
                clicked_date = raw_date[:10]
            
            if clicked_date >= start_date.strftime("%Y-%m-%d"):
                if clicked_date not in st.session_state.work_dates:
                    st.session_state.work_dates.append(clicked_date)
                    st.rerun() 
        elif state["callback"] == "eventClick":
            clicked_id = state["eventClick"]["event"]["id"]
            if clicked_id in st.session_state.work_dates:
                st.session_state.work_dates.remove(clicked_id)
                st.rerun() 

# --- 卡片 3：報表計算 ---
st.markdown("---")
with st.container():
    st.subheader("📊 期數推算報表")
    
    # ⚠️ 這裡修復了型別錯誤：確保 start_date 被轉換為文字來做比較
    valid_dates = sorted([datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in st.session_state.work_dates if d >= start_date.strftime("%Y-%m-%d")])
    
    if valid_dates:
        tab1, tab2 = st.tabs(["💼 長期滾動推算 (推薦)", "📅 單月結算 (不續搭)"])
        
        with tab1:
            history = []
            i = 0
            total_cost = 0
            while i < len(valid_dates):
                current_day = valid_dates[i]
                window_end = current_day + timedelta(days=29)
                trips_in_window = sum(2 for d in valid_dates[i:] if d <= window_end)
                
                if trips_in_window >= 36:
                    history.append({"period": len(history)+1, "type": "定期票", "start": current_day, "end": window_end, "days": trips_in_window//2, "cost": price_periodic, "color": "badge-green"})
                    total_cost += price_periodic
                    while i < len(valid_dates) and valid_dates[i] <= window_end: i += 1
                else:
                    multi_expiry = current_day + timedelta(days=44)
                    trips_used = 0
                    last_day = current_day
                    while i < len(valid_dates) and trips_used < 10 and valid_dates[i] <= multi_expiry:
                        trips_used += 2
                        last_day = valid_dates[i]
                        i += 1
                    history.append({"period": len(history)+1, "type": "回數票", "start": current_day, "end": last_day, "days": trips_used//2, "cost": price_multi, "color": "badge-blue"})
                    total_cost += price_multi

            st.markdown(f'預估總成本：<span style="color: #E11D48; font-size: 18px; font-weight: bold;">${total_cost}</span>', unsafe_allow_html=True)
            for item in history:
                st.markdown(f"""<div class="timeline-card"><div class="timeline-header"><span class="timeline-title">第 {item['period']} 期：{item['type']}</span><span class="{item['color']}">💰 ${item['cost']}</span></div><div style="font-size:15px;">📅 {item['start'].strftime('%Y/%m/%d')} ~ {item['end'].strftime('%m/%d')}</div><div style="color:gray; font-size:13px;">涵蓋：{item['days']} 天 ({item['days']*2} 趟)</div></div>""", unsafe_allow_html=True)

        with tab2:
            first_day = valid_dates[0]
            month_end = first_day + timedelta(days=29)
            trips_month = sum(2 for d in valid_dates if d <= month_end)
            cost_strict = (trips_month // 10 * price_multi) + (trips_month % 10 * price_single)
            
            best = "直接買定期票" if cost_strict >= price_periodic else f"買回數票+單程票"
            st.markdown(f"""<div class="timeline-card"><div class="timeline-header"><span class="timeline-title">單月結算</span><span class="badge-gray">${min(cost_strict, price_periodic)}</span></div><div>💡 結論：<b>{best}</b></div><div style="color:gray; font-size:13px; margin-top:5px;">混搭成本：${int(cost_strict)} | 定期票：${int(price_periodic)}</div></div>""", unsafe_allow_html=True)
    else:
        st.info("目前沒有排班喔！")
