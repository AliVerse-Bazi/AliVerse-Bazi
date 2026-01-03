import streamlit as st
import pandas as pd # <--- 關鍵修復：補回 pandas 套件
from lunar_python import Lunar, Solar
import altair as alt
import datetime
import time
import random

# --- 1. 網頁設定 ---
st.set_page_config(
    page_title="AliVerse 愛力宇宙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 定義解鎖密碼
UNLOCK_CODE = "ALI888"

# --- 2. CSS 樣式美化 (含 V13.0 炸裂光暈特效) ---
st.markdown("""
    <style>
    body { font-family: '微軟正黑體', sans-serif; }
    
    /* 隱藏 Streamlit 原生元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: white;
        padding: 40px 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: -50px;
    }
    .hero-title {
        font-size: 3em;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(to right, #ffd700, #ffecb3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
    }
    .hero-subtitle {
        font-size: 1.2em;
        color: #a0a0a0;
        margin-top: 10px;
        font-weight: 500;
    }
    .highlight { color: #ffd700; font-weight: bold; }

    /* 按鈕樣式 */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 4em;
        background: linear-gradient(to right, #FF4B4B, #FF2B2B);
        color: white;
        font-weight: bold;
        font-size: 20px;
        box-shadow: 0 6px 15px rgba(255, 75, 75, 0.3);
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 75, 75, 0.4);
    }
    
    /* 輸入框優化 */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label {
        font-size: 16px;
        font-weight: 600;
        color: #333;
    }
    @media (prefers-color-scheme: dark) {
        .stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label {
            color: #eee;
        }
    }
    
    /* 結果卡片 */
    .result-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }
    
    /* ASCII Art */
    .ascii-art {
        font-family: 'Courier New', Courier, monospace; 
        white-space: pre; 
        line-height: 1.0;
        font-size: 12px;
        color: #FFD700;
        overflow-x: auto;
        margin: 20px auto;
        text-align: center;
        width: 100%;
        display: flex;
        justify-content: center;
    }

    /* 車型規格表 */
    .spec-table {
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        text-align: left;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: '微軟正黑體', sans-serif;
    }
    .spec-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        border-bottom: 1px dashed rgba(255,255,255,0.2);
        padding-bottom: 8px;
    }
    .spec-label { color: #bbb; font-size: 0.9em; }
    .spec-value { font-weight: bold; color: #fff; text-align: right;}
    
    /* 傳統命理標籤 */
    .trad-badge {
        display: inline-block;
        background-color: #FFD700;
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* === V13.0 HUD 儀表板動畫特效 === */
    .hud-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: radial-gradient(circle, rgba(20,20,30,0.95) 0%, rgba(0,0,0,1) 100%);
        z-index: 99999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        color: #FFD700;
    }
    /* 網格背景 */
    .hud-grid {
        position: absolute;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(255, 215, 0, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 215, 0, 0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        opacity: 0.2;
        z-index: -1;
    }
    .speed-container {
        border: 2px solid rgba(255, 215, 0, 0.3);
        border-radius: 50%;
        width: 300px;
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background: rgba(0,0,0,0.8);
        box-shadow: 0 0 30px rgba(255, 75, 75, 0.2);
        transition: all 0.1s;
    }
    .speed-val {
        font-family: 'Courier New', monospace;
        font-size: 5.5em;
        font-weight: 800;
        line-height: 1;
        text-shadow: 0 0 15px currentColor; 
    }
    .speed-unit {
        font-size: 1.2em;
        color: #aaa;
        margin-top: 5px;
    }
    .rpm-bar {
        width: 80%;
        height: 10px;
        background: #333;
        margin-top: 15px;
        border-radius: 5px;
        overflow: hidden;
    }
    .rpm-fill {
        height: 100%;
        background: linear-gradient(90deg, #39FF14, #FFD700, #FF0000);
        transition: width 0.1s;
    }
    .hud-status {
        margin-top: 30px;
        font-size: 1.5em;
        letter-spacing: 2px;
        color: #fff;
        animation: flicker 0.2s infinite alternate;
    }
    @keyframes flicker {
        0% { opacity: 0.8; }
        100% { opacity: 1; text-shadow: 0 0 10px white; }
    }

    /* 解鎖任務區塊 */
    .lock-box {
        border: 2px dashed #FF4B4B;
        background-color: rgba(255, 75, 75, 0.05);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-top: 30px;
    }
    .lock-title {
        color: #FF4B4B; 
        font-size: 1.5em; 
        font-weight: bold; 
        margin-bottom: 10px;
    }
    .line-link {
        color: #FFD700;
        text-decoration: none;
        font-weight: bold;
        border-bottom: 1px solid #FFD700;
        transition: all 0.3s;
    }
    .line-link:hover {
        color: #fff;
        border-bottom: 1px solid #fff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 主視覺 Hero Banner ---
st.markdown("""
<div class="hero-container">
<h1 class="hero-title">AliVerse 愛力宇宙</h1>
<p class="hero-subtitle">科技命理・生命載具調校專家</p>
<div class="hero-intro">
歡迎來到 AliVerse 原廠檢測中心。<br>
在這裡，我們將透過您的出廠數據（八字），<br>
解密您的<span class="highlight">【核心引擎】</span>與<span class="highlight">【駕駛風格】</span>。<br>
</div>
</div>
""", unsafe_allow_html=True)


# --- 4. 輸入區域 ---
with st.container(border=True):
    st.markdown("### 🛠️ 建立您的駕駛檔案")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 姓名 / 代號", value="", placeholder="請輸入您的姓名")
    with col2:
        gender = st.radio("⚥ 性別規格", ["男", "女"], horizontal=True)
    
    st.write("") 
    
    st.markdown("<label style='font-size:16px; font-weight:600;'>📅 出廠日期 (國曆)</label>", unsafe_allow_html=True)
    d_col1, d_col2, d_col3 = st.columns([1.5, 1, 1]) 
    
    with d_col1:
        inp_year = st.number_input("年 (Year)", min_value=1900, max_value=2026, value=None, placeholder="yyyy", format="%d", step=1)
    with d_col2:
        inp_month = st.number_input("月 (Month)", min_value=1, max_value=12, value=None, placeholder="MM", format="%d", step=1)
    with d_col3:
        inp_day = st.number_input("日 (Day)", min_value=1, max_value=31, value=None, placeholder="DD", format="%d", step=1)
        
    st.write("")
    
    birth_hour = st.selectbox("🕰️ 啟動時辰", [
        "00:00 - 00:59 (早子)", "01:00 - 02:59 (丑)", "03:00 - 04:59 (寅)",
        "05:00 - 06:59 (卯)", "07:00 - 08:59 (辰)", "09:00 - 10:59 (巳)",
        "11:00 - 12:59 (午)", "13:00 - 14:59 (未)", "15:00 - 16:59 (申)",
        "17:00 - 18:59 (酉)", "19:00 - 20:59 (戌)", "21:00 - 22:59 (亥)",
        "23:00 - 23:59 (晚子)"
    ], index=None, placeholder="請點選出生時辰") 

    st.write("")
    # 初始化 session state
    if 'analyzed' not in st.session_state:
        st.session_state['analyzed'] = False
    
    submit_btn = st.button("🚀 啟動引擎 (開始分析)")

# --- 5. 運算與結果顯示區 ---
if submit_btn:
    st.session_state['analyzed'] = True

if st.session_state['analyzed']:
    # 檢查輸入
    if inp_year is None or inp_month is None or inp_day is None or birth_hour is None:
        st.error("⚠️ 資料不完整，請檢查輸入。")
        st.stop()

    try:
        birth_date = datetime.date(int(inp_year), int(inp_month), int(inp_day))
    except ValueError:
        st.error("⚠️ 日期格式錯誤。")
        st.stop()
    
    display_name = name if name.strip() else "貴賓"
    
    # === [後端運算區] 先算好，避免動畫跑完報錯 ===
    hour_map = {
        "00:00 - 00:59 (早子)": 0, "01:00 - 02:59 (丑)": 2, "03:00 - 04:59 (寅)": 4,
        "05:00 - 06:59 (卯)": 6, "07:00 - 08:59 (辰)": 8, "09:00 - 10:59 (巳)": 10,
        "11:00 - 12:59 (午)": 12, "13:00 - 14:59 (未)": 14, "15:00 - 16:59 (申)": 16,
        "17:00 - 18:59 (酉)": 18, "19:00 - 20:59 (戌)": 20, "21:00 - 22:59 (亥)": 22,
        "23:00 - 23:59 (晚子)": 23
    }
    h = hour_map.get(birth_hour, 12)
    
    # 排盤
    solar = Solar.fromYmdHms(birth_date.year, birth_date.month, birth_date.day, h, 0, 0)
    lunar = solar.getLunar()
    bazi = lunar.getEightChar()
    
    lunar_year = lunar.getYearInGanZhi()
    lunar_month = lunar.getMonthInChinese()
    lunar_day = lunar.getDayInChinese()
    zodiac = lunar.getYearShengXiao()

    wuxing_map = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
    producing_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    colors = {"木": "green", "火": "red", "土": "brown", "金": "#DAA520", "水": "blue"}
    
    year_gan, year_zhi = str(bazi.getYearGan()), str(bazi.getYearZhi())
    month_gan, month_zhi = str(bazi.getMonthGan()), str(bazi.getMonthZhi())
    day_gan, day_zhi = str(bazi.getDayGan()), str(bazi.getDayZhi())
    time_gan, time_zhi = str(bazi.getTimeGan()), str(bazi.getTimeZhi())
    
    pillars_data = [
        ("年柱 (根基)", year_gan, year_zhi),
        ("月柱 (事業)", month_gan, month_zhi),
        ("日柱 (本命)", day_gan, day_zhi),
        ("時柱 (晚年)", time_gan, time_zhi)
    ]
    
    day_master_wx = wuxing_map.get(day_gan) 
    resource_wx = [k for k, v in producing_map.items() if v == day_master_wx][0]
    elements_order = ["木", "火", "土", "金", "水"]
    idx = elements_order.index(day_master_wx)
    peer = elements_order[idx]
    resource = elements_order[idx-1]
    output = elements_order[(idx+1)%5]
    wealth = elements_order[(idx+2)%5]
    officer = elements_order[(idx+3)%5]
    
    weights = [(year_gan, 5), (year_zhi, 20), (month_gan, 5), (month_zhi, 35), (day_zhi, 20), (time_gan, 5), (time_zhi, 10)]
    score = 0
    for char, w in weights:
        char_wx = wuxing_map.get(char)
        if char_wx == day_master_wx or char_wx == resource_wx:
            score += w
            
    joyful_gods = [] 
    taboo_gods = []
    ascii_art = ""
    trad_term = ""
    
    if score >= 80:
        trad_term = "命理格局：從強格 (特殊專旺)"
        car_name = "🛡️ 陸地航母：重裝坦克"
        car_desc = "您的格局特殊，能量專一且強大，不再是普通的車，而是陸地霸主！從強格的特質是「越強越好」，順著氣勢能成大業。無視路障，適合開疆闢土，但個性可能較為固執強勢。"
        spec_cc = "6,000cc 柴油渦輪"
        spec_intake = "V12 雙渦輪增壓"
        spec_fuel = "高耗能 (爆發力強)"
        spec_mod = "勿改裝 (原廠即霸主)"
        bg_color = "#9C27B0"
        border_color = "#9C27B0"
        joyful_gods = [peer, resource] 
        taboo_gods = [wealth, officer]
        ascii_art = """
   ░░░░░░░░░░░░░░░░░
  ░░░░▄▄████▄▄░░░░░░
  ░░░██████████░░░░░
  ░▄▄████████████▄▄░
  █  AliVerse Tank █
  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀"""
        
    elif score >= 60:
        trad_term = "命理格局：身強 (能量充沛)"
        car_name = "🚜 V8 雙渦輪：全地形越野車"
        car_desc = "您是一台擁有怪力的 G-Class 等級越野車！板金厚實，馬力強大。您不怕路爛，只怕沒路跑導致引擎積碳。適合高強度的挑戰，不要把自己關在舒適圈的車庫裡。"
        spec_cc = "4,000cc V8"
        spec_intake = "雙渦輪增壓"
        spec_fuel = "1 公升跑 6 公里"
        spec_mod = "潛力極高 (可升高底盤)"
        bg_color = "rgba(46, 125, 50, 0.3)" 
        border_color = "#2E7D32"
        joyful_gods = [output, wealth, officer]
        taboo_gods = [peer, resource]
        ascii_art = """
      ____  
     /  | \_ 
    |___|___\_
    (o)----(o)
   [ SUV-4WD ]"""

    elif score >= 40:
        trad_term = "命理格局：中和 (身強偏平)"
        car_name = "🏎️ 自然進氣：豪華性能房車"
        car_desc = "您是一台平衡性極佳的 BMW 5系列或 E-Class！擁有 3.0 直列六缸的絲滑動力。進可攻、退可守，是道路上最可靠的夥伴。您不需要太誇張的改裝，只要維持良好狀態就能跑很久。"
        spec_cc = "3,000cc"
        spec_intake = "直列六缸 自然進氣 (NA)"
        spec_fuel = "1 公升跑 10 公里"
        spec_mod = "適合微調 (刷一階晶片)"
        bg_color = "rgba(33, 150, 243, 0.3)"
        border_color = "#2196F3"
        joyful_gods = [output, wealth, officer]
        taboo_gods = [peer, resource]
        ascii_art = """
      ______
     /  |   \_
    |___|_____\__
    (o)-----(o)
    [  SEDAN  ]"""
        
    elif score >= 20:
        trad_term = "命理格局：身弱 (心思細膩)"
        car_name = "🚘 經典敞篷：限量古董跑車"
        car_desc = "您是一台極具價值的經典敞篷車 (Vintage Roadster)！雖然排氣量不大，但工藝精密、氣質優雅。您不適合去泥巴地越野，也不適合飆高速。需要細心呵護、定期回原廠保養，開的是「品味」不是「速度」。"
        spec_cc = "2,000cc 精密引擎"
        spec_intake = "自然進氣"
        spec_fuel = "1 公升跑 12 公里"
        spec_mod = "不建議 (維持原廠)"
        bg_color = "rgba(198, 40, 40, 0.3)" 
        border_color = "#C62828"
        joyful_gods = [peer, resource]
        taboo_gods = [output, wealth, officer]
        ascii_art = """
       ___
     _/___\_
    [_______]
    (o)   (o)
   [ VINTAGE ]"""

    else:
        trad_term = "命理格局：從弱格 (棄命從勢)"
        car_name = "🛸 未來科技：磁浮概念車"
        car_desc = "您的格局特殊，本身能量極弱，但能完全順應環境大勢。這不是弱，而是一種極致的適應力。像變形金剛一樣，借力使力，順著大環境的氣流飛行。"
        spec_cc = "無 (反重力)"
        spec_intake = "磁浮驅動"
        spec_fuel = "無限續航"
        spec_mod = "系統自動更新"
        bg_color = "#9C27B0"
        border_color = "#9C27B0"
        joyful_gods = [output, wealth, officer] 
        taboo_gods = [peer, resource]
        ascii_art = """
      .---.
    _/__~__\_
   (_________)
    /       \ 
   [   UFO   ]"""
    
    advice_2026 = ""
    icon = ""
    border_2026 = ""
    if "火" in joyful_gods:
        advice_2026 = "恭喜！2026年是您的「高速公路衝刺段」。流年屬火，正好是您需要的燃油。油門踩下去，不用怕超速，這是您擴展事業、大顯身手的好時機！"
        icon = "🚀"
        border_2026 = "#FFD700"
    else:
        advice_2026 = "2026年路況較為壅塞，火氣太旺，引擎容易過熱。建議切換到「省油模式」，慢慢開、多保養。不要硬超車，安全抵達才是贏家。"
        icon = "🛡️"
        border_2026 = "#E0E0E0"
        
    # === [動畫特效區] V14.0 中文沉浸版 ===
    if submit_btn:
        animation_placeholder = st.empty()
        
        # 定義加速函式
        def show_hud(speed, status_text, text_style):
            percent = min(speed / 333 * 100, 100)
            animation_placeholder.markdown(f"""
            <div class="hud-overlay">
                <div class="hud-grid"></div>
                <div class="speed-container">
                    <div class="speed-val" style="{text_style}">{speed}</div>
                    <div class="speed-unit">km/h</div>
                    <div class="rpm-bar"><div class="rpm-fill" style="width: {percent}%;"></div></div>
                </div>
                <div class="hud-status">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

        # 1. 🟢 起步 (0-80) 螢光綠
        for s in range(0, 81, 5):
            show_hud(s, "系統暖機程序啟動...", "color: #39FF14; text-shadow: 0 0 15px #39FF14;")
            time.sleep(0.04)
            
        # 2. 🟡 加速 (81-180) 黃金光
        for s in range(81, 181, 10):
            show_hud(s, "渦輪增壓全開！🚀", "color: #FFD700; text-shadow: 0 0 20px #FFD700;")
            time.sleep(0.02)
            
        # 3. 🟠 高速 (181-280) 熔岩橘
        for s in range(181, 281, 15):
            show_hud(s, "動力極限輸出！⚠️", "color: #FF4500; text-shadow: 0 0 25px #FF4500;")
            time.sleep(0.01)

        # 4. 🔴 極速炸裂 (281-333) 地獄火紅 + 多層次光暈
        bloom_style = """
            color: #FF0000;
            text-shadow: 
                0 0 10px #ff0000,
                0 0 20px #ff0000,
                0 0 40px #ff0000,
                0 0 80px #ff0000;
            animation: flicker 0.1s infinite;
        """
        for s in range(281, 335, 20): # 超過一點到 333
            display_s = min(s, 333)
            show_hud(display_s, "氮氣噴射：靈魂超頻！💥", bloom_style)
            time.sleep(0.005)
            
        time.sleep(0.8) # 停留極速炸裂畫面
        animation_placeholder.empty()

    # --- 顯示區 (免費版) ---
    st.write("---")
    st.subheader("🏎️ 您的原廠車型鑑定")
    
    html_content = f"""<div style="padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); border: 2px solid {border_color}; background-color: {bg_color};">
    <div class="trad-badge">{trad_term}</div>
    <h2 style="margin-bottom: 10px;">{car_name}</h2>
    <div style="font-size: 1.5em; margin: 5px 0; font-weight:bold;">能量指數：{score}%</div>
    <div class="ascii-art">{ascii_art}</div>
    <p style="font-size: 1.1em; line-height: 1.6; text-align: left; margin-top:15px;"><b>📝 性能分析：</b><br>{car_desc}</p>
    <div class="spec-table">
        <div class="spec-row"><span class="spec-label">⚙️ 引擎規格</span> <span class="spec-value">{spec_cc}</span></div>
        <div class="spec-row"><span class="spec-label">💨 進氣方式</span> <span class="spec-value">{spec_intake}</span></div>
        <div class="spec-row"><span class="spec-label">⛽ 油耗表現</span> <span class="spec-value">{spec_fuel}</span></div>
        <div class="spec-row" style="border-bottom: none;"><span class="spec-label">🔧 改裝潛力</span> <span class="spec-value">{spec_mod}</span></div>
    </div>
</div>"""
    st.markdown(html_content, unsafe_allow_html=True)

    # === 上鎖區域 ===
    st.write("---")
    st.markdown("""
    <div class="lock-box">
        <div class="lock-title">🔒 權限鎖定：詳細運勢資料庫</div>
        <div class="lock-desc">
            想要查看 <b>2026流年運勢</b>、<b>八字能量圖表</b> 與 <b>幸運能量建議</b>？<br><br>
            1. <a href="https://lin.ee/3woTmES" target="_blank" class="line-link">👉 點此加入 LINE 官方帳號</a><br>
            2. 輸入關鍵字<b>『report』</b>獲取通關密碼<br>
            3. 在下方輸入密碼，立即解鎖分析
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c_lock1, c_lock2, c_lock3 = st.columns([1, 2, 1])
    with c_lock2:
        user_code = st.text_input("🔑 輸入解鎖碼", placeholder="在此輸入密碼...", label_visibility="collapsed")
    
    # === 解鎖後顯示區域 ===
    if user_code == UNLOCK_CODE:
        with st.spinner("🔄 正在驗證金鑰... 連線資料庫中..."):
            time.sleep(1.5)
        st.success("✅ 權限解鎖成功！")
        time.sleep(0.5)

        # 1. 農曆與八字
        st.header(f"📄 {display_name} 的原廠性能規格表")
        st.markdown(f"""
        <div style="background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; margin-bottom: 25px; border-left: 5px solid #FFD700; display: flex; align-items: center;">
            <div style="font-size: 2em; margin-right: 15px;">🗓️</div>
            <div>
                <div style="color: #a0a0a0; font-size: 0.9em;">對應農曆日期</div>
                <div style="font-size: 1.3em; font-weight: bold; color: #FFD700;">
                    {lunar_year}年 {lunar_month}月 {lunar_day} <span style="color: #fff; font-size: 0.8em; background-color: #333; padding: 2px 8px; border-radius: 10px; margin-left: 5px;">屬{zodiac}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(4)
        for i, (title, gan_char, zhi_char) in enumerate(pillars_data):
            gan_wx = wuxing_map.get(gan_char, "")
            zhi_wx = wuxing_map.get(zhi_char, "")
            with cols[i]:
                st.markdown(f"**{title}**")
                st.markdown(f"<h2 style='text-align: center; color: {colors.get(gan_wx, 'black')}'>{gan_char}</h2>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center; color: {colors.get(zhi_wx, 'black')}'>{zhi_char}</h2>", unsafe_allow_html=True)
                st.caption(f"{gan_wx} / {zhi_wx}")
                
        # 2. 五行圖表 (需要 pandas)
        st.subheader("📊 原廠零件庫存清單 (五行能量)")
        counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        all_chars = [p[1] for p in pillars_data] + [p[2] for p in pillars_data]
        total_chars = 8
        for char in all_chars:
            wx = wuxing_map.get(char)
            if wx in counts:
                counts[wx] += 1
        data = []
        for wx, count in counts.items():
            percentage = (count / total_chars) * 100
            label = f"{count} ({percentage:.0f}%)"
            data.append({"五行": wx, "數量": count, "標籤": label})
        df = pd.DataFrame(data)
        base = alt.Chart(df).encode(
            x=alt.X('五行', axis=alt.Axis(labelAngle=0, title="五行屬性")),
            y=alt.Y('數量', axis=alt.Axis(title="數量 (個)", titleAngle=0, titleY=-10)),
            color=alt.Color('五行', scale=alt.Scale(domain=['金', '木', '水', '火', '土'], range=['#FFD700', '#228B22', '#1E90FF', '#FF4500', '#8B4513']))
        )
        bars = base.mark_bar()
        text = base.mark_text(align='center', baseline='bottom', dy=-5, fontSize=14).encode(text='標籤')
        st.altair_chart((bars + text), use_container_width=True)

        # 3. 喜忌神
        st.subheader("💡 能量調節建議")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="result-card" style="border-left: 5px solid #4CAF50;">
                <h4 style="color: #4CAF50; margin:0;">⛽ 建議添加 (喜用)</h4>
                <p style="font-size: 1.2em; font-weight: bold; margin: 10px 0;">{'、'.join(joyful_gods)}</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="result-card" style="border-left: 5px solid #F44336;">
                <h4 style="color: #F44336; margin:0;">⛔ 避免積碳 (忌神)</h4>
                <p style="font-size: 1.2em; font-weight: bold; margin: 10px 0;">{'、'.join(taboo_gods)}</p>
            </div>
            """, unsafe_allow_html=True)

        # 4. 2026 運勢
        st.subheader("🔥 2026 (丙午年) 路況預報")
        st.markdown(f"""
        <div style="background-color: rgba(255, 69, 0, 0.1); padding: 20px; border-radius: 10px; border: 1px solid {border_2026};">
            <h4 style="color: #FF4500; margin-top: 0;">{icon} 2026 火馬年路況</h4>
            <p style="font-size: 1.1em; line-height: 1.6;">{advice_2026}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 5. 下載按鈕
        st.write("---")
        full_report = f"""
【AliVerse 愛力宇宙 - 完整車檢報告書】
------------------------------------
駕駛員：{display_name}
命理格局：{trad_term}
原廠車型：{car_name}
核心能量指數：{score}%
------------------------------------
【車型圖騰】
{ascii_art}
------------------------------------
【詳細規格表】
引擎：{spec_cc}
進氣：{spec_intake}
油耗：{spec_fuel}
改裝建議：{spec_mod}
------------------------------------
【性能深度分析】
{car_desc}
------------------------------------
【能量優化方案】
建議添加 (喜用神)：{'、'.join(joyful_gods)}
避免使用 (忌神)：{'、'.join(taboo_gods)}
------------------------------------
【2026 丙午年路況預報】
{advice_2026}
------------------------------------
感謝您的使用！
AliVerse 愛力宇宙 - 科技命理．生命載具調校專家
官方網站：https://aliverse-bazi.streamlit.app
"""
        st.download_button(
            label="📥 下載 PDF 報告",
            data=full_report.encode('utf-8-sig'),
            file_name=f"AliVerse_{display_name}_完整車檢報告.txt",
            mime="text/plain",
            type="primary"
        )

    elif user_code:
        st.error("⛔ 密碼錯誤，請確認 LINE 官方帳號的最新公告。")
