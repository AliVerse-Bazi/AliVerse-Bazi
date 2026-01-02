import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from lunar_python import Solar

# --- 頁面設定 ---
st.set_page_config(page_title="專業八字排盤", layout="wide", page_icon="🔮")

# --- 自定義 CSS (維持您的專業暗色風格) ---
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        color: #FFD700;
        margin-bottom: 5px;
    }
    .sub-info {
        text-align: center;
        font-size: 1.2em;
        color: #E0E0E0;
        margin-bottom: 20px;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    .highlight-box {
        background-color: #333;
        border: 1px solid #FFD700;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .pillar-box {
        text-align: center;
        border: 1px solid #444;
        padding: 10px;
        border-radius: 5px;
        background-color: #222;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. 五行查詢表 ---
def get_wuxing(char):
    gan_map = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", 
               "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
    zhi_map = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", 
               "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", 
               "戌": "土", "亥": "水"}
    return gan_map.get(char, zhi_map.get(char, "?"))

# --- 2. 生生相剋關係 (用於身強身弱簡易判斷) ---
def get_shen_qiang(day_master_wuxing, wuxing_counts):
    # 定義生我者(印)、同我者(比劫)
    relationships = {
        "木": {"support": ["水", "木"]},
        "火": {"support": ["木", "火"]},
        "土": {"support": ["火", "土"]},
        "金": {"support": ["土", "金"]},
        "水": {"support": ["金", "水"]}
    }
    
    if day_master_wuxing not in relationships:
        return "無法判斷"
        
    support_elements = relationships[day_master_wuxing]["support"]
    
    # 計算得分：支持我的五行總數
    score = 0
    for elem in support_elements:
        score += wuxing_counts.get(elem, 0)
    
    # 簡易判斷：8個字中，若有4個(含)以上支持我，視為身強，反之身弱
    # (註：這只是簡易算法，未考慮月令旺衰的加權)
    if score >= 4:
        return "身強"
    else:
        return "身弱"

# --- 3. 時辰轉換 ---
def get_hour_from_label(label):
    mapping = {
        "早子": 0, "丑": 2, "寅": 4, "卯": 6, "辰": 8, "巳": 10,
        "午": 12, "未": 14, "申": 16, "酉": 18, "戌": 20, "亥": 22, "晚子": 23
    }
    for k, v in mapping.items():
        if k in label: return v
    return 12

# --- 側邊欄輸入區 ---
with st.sidebar:
    st.header("📝 輸入資料")
    name = st.text_input("姓名", placeholder="請輸入你的姓名", value="顏鼎晏")
    gender = st.radio("性別", ("男", "女"), label_visibility="collapsed")
    birth_date = st.date_input("出生日期", value=date(1979, 9, 12))
    
    time_options = [
        "00:00 - 00:59 (早子)", "01:00 - 02:59 (丑)", "03:00 - 04:59 (寅)", 
        "05:00 - 06:59 (卯)", "07:00 - 08:59 (辰)", "09:00 - 10:59 (巳)",
        "11:00 - 12:59 (午)", "13:00 - 14:59 (未)", "15:00 - 16:59 (申)",
        "17:00 - 18:59 (酉)", "19:00 - 20:59 (戌)", "21:00 - 22:59 (亥)",
        "23:00 - 23:59 (晚子)"
    ]
    birth_time_label = st.selectbox("出生時間", time_options, index=9)
    st.write("") 
    submit_btn = st.button("開始排盤", type="primary")

# --- 主畫面邏輯 ---

if submit_btn:
    if not name:
        st.error("請輸入姓名以開始排盤。")
    else:
        try:
            # === 計算八字 ===
            input_hour = get_hour_from_label(birth_time_label)
            solar = Solar.fromYmdHms(birth_date.year, birth_date.month, birth_date.day, input_hour, 0, 0)
            lunar = solar.getLunar()
            bazi = lunar.getEightChar()
            
            # 取得基礎資訊
            sheng_xiao = lunar.getYearShengXiao() # 生肖
            nong_li = lunar.toString() # 農曆日期文字
            
            # 取得四柱
            pillars = [
                (bazi.getYearGan(), bazi.getYearZhi()),
                (bazi.getMonthGan(), bazi.getMonthZhi()),
                (bazi.getDayGan(), bazi.getDayZhi()),
                (bazi.getTimeGan(), bazi.getTimeZhi())
            ]
            
            # 計算五行數量
            wuxing_counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
            for gan, zhi in pillars:
                wuxing_counts[get_wuxing(gan)] += 1
                wuxing_counts[get_wuxing(zhi)] += 1
                
            # 計算日主與身強身弱
            day_master = pillars[2][0] # 日干
            day_master_wuxing = get_wuxing(day_master)
            strength = get_shen_qiang(day_master_wuxing, wuxing_counts)

            # === 介面顯示 ===
            
            # 標題區
            st.markdown(f"<div class='main-title'>🔮 {name} 的八字命盤</div>", unsafe_allow_html=True)
            
            # 副標題：顯示 生肖、農曆、西元、身強身弱
            info_text = f"""
            <b>生肖：{sheng_xiao}</b> &nbsp;|&nbsp; 農曆：{nong_li}<br>
            西元：{birth_date.strftime('%Y-%m-%d')} {birth_time_label.split(' ')[0]}<br>
            <span style="color: #FFD700;">日主：{day_master} ({day_master_wuxing})</span> &nbsp;|&nbsp; 
            <span style="color: #4CAF50;">格局判斷：{strength}</span>
            """
            st.markdown(f"<div class='sub-info'>{info_text}</div>", unsafe_allow_html=True)
            
            st.divider()

            # 1. 八字四柱展示
            st.subheader("1. 八字四柱")
            cols = st.columns(4)
            labels = ["年柱", "月柱", "日柱", "時柱"]
            
            color_map = {"木": "#4CAF50", "火": "#FF5252", "土": "#FFC107", "金": "#E0E0E0", "水": "#2196F3"}

            for i, col in enumerate(cols):
                gan, zhi = pillars[i]
                w_gan = get_wuxing(gan)
                w_zhi = get_wuxing(zhi)
                c_gan = color_map.get(w_gan, "#FFF")
                c_zhi = color_map.get(w_zhi, "#FFF")

                with col:
                    st.markdown(f"""
                    <div class="pillar-box">
                        <div style="font-size: 14px; color: #aaa;">{labels[i]}</div>
                        <div style="font-size: 28px; font-weight: bold; margin-top: 10px;">
                            <span style="color: {c_gan};">{gan}</span>
                            <span style="color: {c_zhi};">{zhi}</span>
                        </div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            {w_gan}{w_zhi}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            # 2. 五行圖表 (條狀圖 + 圓餅圖)
            st.subheader("2. 五行能量分析")
            
            # 準備數據
            df = pd.DataFrame(list(wuxing_counts.items()), columns=['五行', '數量'])
            
            # 設定顏色映射 (給圖表用)
            domain = ["木", "火", "土", "金", "水"]
            range_ = ["#4CAF50", "#FF5252", "#FFC107", "#C0C0C0", "#2196F3"]

            c1, c2 = st.columns(2)
            
            with c1:
                st.write("**條狀分佈圖**")
                # 使用 Altair 畫條狀圖 (更美觀且不需要 matplotlib)
                bar_chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('五行', sort=domain),
                    y='數量',
                    color=alt.Color('五行', scale=alt.Scale(domain=domain, range=range_), legend=None),
                    tooltip=['五行', '數量']
                ).properties(height=300)
                st.altair_chart(bar_chart, use_container_width=True)

            with c2:
                st.write("**比例圓餅圖**")
                # 使用 Altair 畫圓餅圖 (Donut Chart)
                base = alt.Chart(df).encode(
                    theta=alt.Theta("數量", stack=True)
                )
                pie = base.mark_arc(outerRadius=100, innerRadius=40).encode(
                    color=alt.Color("五行", scale=alt.Scale(domain=domain, range=range_)),
                    order=alt.Order("數量", sort="descending"),
                    tooltip=["五行", "數量"]
                )
                text = base.mark_text(radius=120).encode(
                    text=alt.Text("數量", format=".0f"),
                    order=alt.Order("數量", sort="descending"),
                    color=alt.value("white")  # 文字白色
                )
                st.altair_chart(pie + text, use_container_width=True)

            st.divider()

            # 3. 運勢建議
            st.subheader("3. 2026 (丙午年) 運勢建議")
            
            advice = ""
            if strength == "身弱":
                advice = f"您的日主為【{day_master}】，判定為【身弱】。2026年火氣旺，建議尋求印星（生我者）或比劫（同伴）的幫助。多學習、多依靠長輩或團隊合作，不宜單打獨鬥。"
            else:
                advice = f"您的日主為【{day_master}】，判定為【身強】。2026年火氣旺，身強者可任財官。今年適合積極表現，承擔責任，但需注意個性過於強勢，需多傾聽他人意見。"

            st.success(f"""
            **命盤總評：**
            {day_master}日主，生於{sheng_xiao}年。五行中【{max(wuxing_counts, key=wuxing_counts.get)}】氣場最強。
            
            **流年建議：**
            {advice}
            """)

        except Exception as e:
            st.error(f"程式發生錯誤：{e}")

else:
    # 歡迎頁面
    st.write("")
    st.write("")
    st.markdown('<div class="main-title">歡迎來到專業八字五行排盤系統</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">探索命運的奧秘，掌握人生流年運勢</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="instruction">
            <h3>👈 請在左側輸入您的資料</h3>
            <p>系統將為您計算：</p>
            <ul style="text-align: left; display: inline-block;">
                <li>📜 <b>八字四柱</b> 與 <b>生肖/農曆</b></li>
                <li>⚖️ <b>身強身弱</b> 能量判斷</li>
                <li>📊 <b>五行條狀圖</b> 與 <b>圓餅圖</b></li>
                <li>📅 <b>2026年流年運勢建議</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)