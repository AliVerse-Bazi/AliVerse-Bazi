import streamlit as st
import pandas as pd
from lunar_python import Lunar, Solar
import altair as alt
import datetime

# --- 1. 網頁設定 ---
st.set_page_config(
    page_title="AliVerse 愛力宇宙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS 樣式美化 (強力隱藏浮水印版) ---
st.markdown("""
    <style>
    /* 全局字體 */
    body { font-family: '微軟正黑體', sans-serif; }

    /* --- 強力隱藏 Streamlit 預設元件 --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stDecoration"] {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    
    /* Hero Banner 樣式 */
    .hero-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: white;
        padding: 40px 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
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
    .hero-intro {
        margin-top: 30px;
        font-size: 1.1em;
        line-height: 1.8;
        color: #e0e0e0;
        text-align: left;
        display: inline-block;
        max-width: 800px;
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
    
    /* 輸入框標題優化 */
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
    
    /* 結果卡片樣式 */
    .result-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }
    
    /* ASCII Art 樣式 (車型圖騰) */
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

    /* 車型規格表樣式 */
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
    </style>
    """, unsafe_allow_html=True)

# --- 3. 主視覺 Hero Banner ---
st.markdown("""
<div class="hero-container">
<h1 class="hero-title">AliVerse 愛力宇宙</h1>
<p class="hero-subtitle">科技命理・生命載具調校專家</p>
<div class="hero-intro">
人生，就像駕駛一台結構精密的載具。<br>
AliVerse 的核心價值，在於透過數據，協助您<span class="highlight">【迅速且直覺】</span>地掌握這台載具的<span class="highlight">【原廠配備】</span>。<br><br>
我們深信，理解數據是為了獲得智慧。<br>
當您看清並接受自己的優勢與特質，便能在人生的道路上<span class="highlight">【坦然前行】</span>；<br>
當您深刻了解自己，便能對他人產生更多的<span class="highlight">【理解與同理】</span>。<br><br>
我們期盼每個人都能藉此<span class="highlight">【綻放出獨一無二的光芒】</span>，<br>
在<span class="highlight">【愛自己】</span>的同時也能給予他人更多<span class="highlight">【關懷】</span>，<br>
讓我們一起<span class="highlight">【照亮整個愛力的宇宙】</span>。
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
        inp_year = st.number_input("年 (Year)", min_value=1900, max_value=2026, value=None, placeholder="例如 1979", format="%d", step=1)
    with d_col2:
        inp_month = st.number_input("月 (Month)", min_value=1, max_value=12, value=None, placeholder="月份", format="%d", step=1)
    with d_col3:
        inp_day = st.number_input("日 (Day)", min_value=1, max_value=31, value=None, placeholder="日期", format="%d", step=1)
        
    st.write("")
    
    birth_hour = st.selectbox("🕰️ 啟動時辰", [
        "00:00 - 00:59 (早子)", "01:00 - 02:59 (丑)", "03:00 - 04:59 (寅)",
        "05:00 - 06:59 (卯)", "07:00 - 08:59 (辰)", "09:00 - 10:59 (巳)",
        "11:00 - 12:59 (午)", "13:00 - 14:59 (未)", "15:00 - 16:59 (申)",
        "17:00 - 18:59 (酉)", "19:00 - 20:59 (戌)", "21:00 - 22:59 (亥)",
        "23:00 - 23:59 (晚子)"
    ], index=None, placeholder="請點選出生時辰") 

    st.write("")
    submit_btn = st.button("🚀 啟動性能分析")

# --- 5. 運算與結果顯示區 ---
if submit_btn:
    # 檢查輸入
    if inp_year is None or inp_month is None or inp_day is None:
        st.error("⚠️ 資料不完整：請輸入完整的出生【年、月、日】數字。")
        st.stop()
    if birth_hour is None:
        st.error("⚠️ 資料不完整：請選擇【出生時辰】。")
        st.stop()

    try:
        birth_date = datetime.date(int(inp_year), int(inp_month), int(inp_day))
    except ValueError:
        st.error(f"⚠️ 日期錯誤：{int(inp_month)}月沒有{int(inp_day)}號喔！請重新檢查。")
        st.stop()
    
    display_name = name if name.strip() else "貴賓"
    
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
    
    st.write("---")
    
    # 1. 標題與農曆
    st.header(f"📄 {display_name} 的原廠性能規格表")
    lunar_year = lunar.getYearInGanZhi()
    lunar_month = lunar.getMonthInChinese()
    lunar_day = lunar.getDayInChinese()
    zodiac = lunar.getYearShengXiao()
    
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
    
    wuxing_map = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
    colors = {"木": "green", "火": "red", "土": "brown", "金": "#DAA520", "水": "blue"}
    producing_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    
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
    cols = st.columns(4)
    for i, (title, gan_char, zhi_char) in enumerate(pillars_data):
        gan_wx = wuxing_map.get(gan_char, "")
        zhi_wx = wuxing_map.get(zhi_char, "")
        with cols[i]:
            st.markdown(f"**{title}**")
            st.markdown(f"<h2 style='text-align: center; color: {colors.get(gan_wx, 'black')}'>{gan_char}</h2>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center; color: {colors.get(zhi_wx, 'black')}'>{zhi_char}</h2>", unsafe_allow_html=True)
            st.caption(f"{gan_wx} / {zhi_wx}")
    
    st.write("---")
    
    # --- 核心運算：車型判斷 ---
    st.subheader("🏎️ 您的原廠車型鑑定")
    
    day_master_wx = wuxing_map.get(day_gan) 
    resource_wx = [k for k, v in producing_map.items() if v == day_master_wx][0]
    
    elements_order = ["木", "火", "土", "金", "水"]
    idx = elements_order.index(day_master_wx)
    
    peer = elements_order[idx]
    resource = elements_order[idx-1]
    output = elements_order[(idx+1)%5]
    wealth = elements_order[(idx+2)%5]
    officer = elements_order[(idx+3)%5]
    
    weights = [
        (year_gan, 5), (year_zhi, 20),
        (month_gan, 5), (month_zhi, 35),
        (day_zhi, 20),
        (time_gan, 5), (time_zhi, 10)
    ]
    score = 0
    for char, w in weights:
        char_wx = wuxing_map.get(char)
        if char_wx == day_master_wx or char_wx == resource_wx:
            score += w
            
    joyful_gods = [] 
    taboo_gods = []
    ascii_art = ""
    trad_term = ""
    
    # --- 車型定義 (確保 ASCII 與 HTML 正常) ---
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

    # 顯示車型卡片 (使用 f-string 組合 HTML)
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
    
    # 喜忌神
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="result-card" style="border-left: 5px solid #4CAF50;">
            <h4 style="color: #4CAF50; margin:0;">⛽ 建議添加燃油 (喜用)</h4>
            <p style="font-size: 1.2em; font-weight: bold; margin: 10px 0;">{'、'.join(joyful_gods)}</p>
            <p style="font-size: 0.9em; color: #aaa;">這是您的優質汽油，多加這款油，車子跑更順。</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="result-card" style="border-left: 5px solid #F44336;">
            <h4 style="color: #F44336; margin:0;">⛔ 容易導致積碳 (忌神)</h4>
            <p style="font-size: 1.2em; font-weight: bold; margin: 10px 0;">{'、'.join(taboo_gods)}</p>
            <p style="font-size: 0.9em; color: #aaa;">這款油品容易傷引擎，請盡量避免。</p>
        </div>
        """, unsafe_allow_html=True)

    # 2026 運勢
    st.subheader("🔥 2026 (丙午年) 路況預報")
    advice_2026 = ""
    if "火" in joyful_gods:
        advice_2026 = "恭喜！2026年是您的「高速公路衝刺段」。流年屬火，正好是您需要的燃油。油門踩下去，不用怕超速，這是您擴展事業、大顯身手的好時機！"
        icon = "🚀"
        border_2026 = "#FFD700"
    else:
        advice_2026 = "2026年路況較為壅塞，火氣太旺，引擎容易過熱。建議切換到「省油模式」，慢慢開、多保養。不要硬超車，安全抵達才是贏家。"
        icon = "🛡️"
        border_2026 = "#E0E0E0"
        
    st.markdown(f"""
    <div style="background-color: rgba(255, 69, 0, 0.1); padding: 20px; border-radius: 10px; border: 1px solid {border_2026};">
        <h4 style="color: #FF4500; margin-top: 0;">{icon} 2026 火馬年路況</h4>
        <p style="font-size: 1.1em; line-height: 1.6;">{advice_2026}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")

    # 五行圖表
    st.subheader("📊 原廠零件庫存清單")
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
    st.caption("說明：統計您命盤中金木水火土各類「零件」的庫存數量與比例。")
    
    st.write("---")
    
    # --- 分享區塊 (移除導購) ---
    st.subheader("📤 邀請朋友一起來尬車")
    
    share_text = f"""🚀 剛剛在 AliVerse 測了我的生命載具！

👤 駕駛代號：{display_name}
{trad_term}
🏎️ 原廠車型：{car_name}
⚙️ 引擎規格：{spec_cc}
🔥 2026路況：{advice_2026[:20]}...

你的原廠設定是坦克還是跑車？
👇 點擊連結，立刻進廠鑑定：
https://aliverse-bazi.streamlit.app"""

    st.info("👇 複製下方文字，分享到 Line 或 IG，看看誰的車最猛！")
    st.code(share_text, language="text")
    
    # 下載內容 (UTF-8 BOM 修復版)
    report_content = f"""
【AliVerse 愛力宇宙 - 原廠車型鑑定報告】
------------------------------------
駕駛：{display_name}
{trad_term}
車型：{car_name}
能量：{score}%
------------------------------------
【車型圖騰】
{ascii_art}
------------------------------------
【詳細規格表】
引擎：{spec_cc}
進氣：{spec_intake}
油耗：{spec_fuel}
改裝：{spec_mod}
------------------------------------
【性能分析】
{car_desc}
------------------------------------
【油品建議】
建議添加 (喜用)：{'、'.join(joyful_gods)}
避免使用 (忌神)：{'、'.join(taboo_gods)}
------------------------------------
【2026 路況預報】
{advice_2026}
------------------------------------
AliVerse 愛力宇宙
https://aliverse-bazi.streamlit.app
"""
    
    st.download_button(
        label="📥 下載完整車檢報告 (txt)",
        data=report_content.encode('utf-8-sig'),
        file_name=f"AliVerse_{display_name}_車檢報告.txt",
        mime="text/plain"
    )
