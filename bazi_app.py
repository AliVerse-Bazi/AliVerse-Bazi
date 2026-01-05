import streamlit as st
import pandas as pd
from lunar_python import Lunar, Solar
import altair as alt
import datetime
import time
import random
import urllib.parse
import textwrap
import re
import streamlit.components.v1 as components

# --- 1. 網頁設定 (V50.2 品牌純淨終極版) ---
st.set_page_config(
    page_title="AliVerse 八字五行分析 - 2026運勢免費測 | 原廠車型鑑定",
    page_icon="🏎️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://lin.ee/3woTmES',      
        'Report a bug': "https://lin.ee/3woTmES", 
        'About': """
        # 🏎️ AliVerse 愛力宇宙
        這是一個結合 **科技數據** 與 **傳統命理** 的生命導航系統。
        **© 2026 AliVerse All Rights Reserved.**
        """
    }
)

# 雙密碼設定
VALID_CODES = ["ALI888", "17888"]

# --- [V44] 自動捲動核心函式 ---
def scroll_to(target_id):
    js = f"""
    <script>
        function scroll() {{
            var element = document.getElementById('{target_id}');
            if (element) {{
                element.scrollIntoView({{behavior: 'smooth', block: 'center'}});
            }}
        }}
        // 稍微延遲以確保 DOM 已渲染
        setTimeout(scroll, 300);
    </script>
    """
    components.html(js, height=0)

# 初始化捲動狀態
if 'scroll_target' not in st.session_state:
    st.session_state['scroll_target'] = None

# --- 2. CSS 樣式美化 ---
st.markdown("""
    <style>
    body { font-family: '微軟正黑體', sans-serif; }
    
    /* --- [V50.2 新增] 品牌純淨化工程 (隱藏所有官方標記) --- */
    
    /* 1. 隱藏右上角工具列 (Github貓咪, Deploy按鈕, 漢堡選單) */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 2. 隱藏頂部裝飾彩色條 */
    [data-testid="stDecoration"] {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 3. 隱藏頁面 Header */
    header {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 4. 隱藏右下角 Footer (Hosted with Streamlit) */
    footer {
        visibility: hidden !important;
        display: none !important;
        height: 0px !important;
    }
    
    /* 5. 隱藏右上角讀取狀態圈圈 */
    [data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
    
    /* 6. 強制隱藏部署按鈕 */
    .stDeployButton {
        display: none !important;
    }
    
    /* 7. 針對手機版可能的底部留白修正 */
    .block-container {
        padding-bottom: 20px !important;
    }
    
    /* --------------------------------------------------- */

    #MainMenu { display: none !important; }
    
    /* 側邊欄呼吸燈 */
    [data-testid="stSidebarCollapsedControl"] {
        animation: glowing 2s infinite;
        border-radius: 50%;
        border: 2px solid #FFD700;
        box-shadow: 0 0 10px #FFD700;
        background-color: rgba(0,0,0,0.5);
        color: #FFD700 !important;
    }
    @keyframes glowing {
        0% { box-shadow: 0 0 5px #FFD700; transform: scale(1); }
        50% { box-shadow: 0 0 20px #FF4B4B; transform: scale(1.1); }
        100% { box-shadow: 0 0 5px #FFD700; transform: scale(1); }
    }
    
    /* 浮動指引文字 */
    .sidebar-hint {
        position: fixed; top: 60px; left: 10px; z-index: 999999;
        background-color: #FF4B4B; color: white; padding: 5px 10px;
        border-radius: 15px; font-size: 12px; font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); animation: bounce 1.5s infinite;
        pointer-events: none;
    }
    .sidebar-hint::before { content: "▲"; position: absolute; top: -12px; left: 10px; color: #FF4B4B; font-size: 14px; }
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: white;
        padding: 40px 30px; border-radius: 15px; text-align: center;
        margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.1); margin-top: -30px;
    }
    .hero-title {
        font-size: 3em; font-weight: 800; margin: 0;
        background: linear-gradient(to right, #ffd700, #ffecb3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
    }
    .hero-subtitle { font-size: 1.2em; color: #a0a0a0; margin-top: 10px; font-weight: 500; }
    .highlight { color: #ffd700; font-weight: bold; }

    /* 按鈕樣式 */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 4em;
        background: linear-gradient(to right, #FF4B4B, #FF2B2B);
        color: white; font-weight: bold; font-size: 20px;
        box-shadow: 0 6px 15px rgba(255, 75, 75, 0.3); border: none; transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255, 75, 75, 0.4); }
    
    /* 喜忌神標籤 */
    .god-tag-container {
        display: flex; justify-content: space-around; margin-top: 15px; padding-top: 15px;
        border-top: 1px dashed rgba(255,255,255,0.2);
    }
    .god-box { text-align: center; }
    .god-label { font-size: 0.8em; color: #aaa; margin-bottom: 2px; }
    .god-value { font-size: 1.1em; font-weight: bold; }
    .neutral { color: #FFD700; }

    /* ASCII Art */
    .ascii-art {
        font-family: 'Courier New', Courier, monospace; 
        white-space: pre; line-height: 1.0; font-size: 12px; color: #FFD700;
        overflow-x: auto; margin: 20px auto; text-align: center;
        width: 100%; display: flex; justify-content: center;
    }

    /* HUD Animation */
    .hud-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle, rgba(20,20,30,0.95) 0%, rgba(0,0,0,1) 100%);
        z-index: 99999; display: flex; flex-direction: column;
        justify-content: center; align-items: center; text-align: center; color: #FFD700;
    }
    .speed-val { font-family: 'Courier New', monospace; font-size: 5.5em; font-weight: 800; line-height: 1; text-shadow: 0 0 15px currentColor; }
    .rpm-bar { width: 80%; height: 10px; background: #333; margin-top: 15px; border-radius: 5px; overflow: hidden; }
    .rpm-fill { height: 100%; background: linear-gradient(90deg, #39FF14, #FFD700, #FF0000); transition: width 0.1s; }
    
    /* 顏色卡片 */
    .color-card {
        padding: 10px; border-radius: 8px; text-align: center; color: white; font-weight: bold;
        text-shadow: 0 1px 3px rgba(0,0,0,0.8); border: 1px solid rgba(255,255,255,0.2); margin-bottom: 5px;
    }

    /* 解鎖任務區塊 */
    .lock-box {
        border: 2px dashed #FF4B4B; background-color: rgba(255, 75, 75, 0.05);
        padding: 25px; border-radius: 15px; text-align: center; margin-top: 30px;
    }
    .line-btn-container a { display: block; width: 100%; text-decoration: none; }
    .line-btn {
        width: 100%; background-color: #06C755; color: white; padding: 15px;
        border-radius: 12px; text-align: center; font-weight: bold; font-size: 18px;
        box-shadow: 0 4px 10px rgba(6, 199, 85, 0.3); margin-bottom: 15px; transition: transform 0.2s;
        text-decoration: none;
        display: block;
    }
    .line-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(6, 199, 85, 0.4);
    }
    
    /* 深度解析區塊 */
    .deep-dive-box {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #4CAF50;
        padding: 15px; margin-bottom: 20px;
        border-radius: 0 10px 10px 0;
    }
    
    /* 八字排盤樣式 */
    .bazi-table {
        width: 100%; text-align: center; background-color: rgba(0,0,0,0.2); border-radius: 10px; padding: 10px;
    }
    .bazi-header { font-size: 0.9em; color: #aaa; margin-bottom: 5px; }
    .ten-god-main { font-size: 0.8em; color: #FFD700; background: rgba(255,215,0,0.1); padding: 2px 5px; border-radius: 4px; display: inline-block; margin-bottom: 5px; }
    .gan-char { font-size: 2.5em; font-weight: bold; margin: 0; line-height: 1.2; }
    .zhi-char { font-size: 2.5em; font-weight: bold; margin: 0; line-height: 1.2; }
    .hidden-stems { font-size: 0.8em; color: #888; margin-top: 5px; border-top: 1px dashed #444; padding-top: 5px;}
    .hidden-stem-row { display: flex; justify-content: space-between; padding: 0 5px; }
    
    /* 靈魂導航 */
    .soul-message {
        font-family: 'Georgia', serif;
        font-style: italic;
        color: #E0E0E0;
        background: linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(255,255,255,0.1) 50%, rgba(0,0,0,0) 100%);
        padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; line-height: 1.8;
    }

    /* AliVerse Matrix Style */
    .matrix-box {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        border: 1px solid #444; border-radius: 15px; padding: 20px;
        margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .hex-symbol {
        font-size: 50px; color: #fff; line-height: 0.8; text-align: center;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.5); margin-bottom: 10px;
    }
    .matrix-item {
        margin-bottom: 15px; padding: 10px 15px;
        background: rgba(255,255,255,0.03); border-left: 3px solid #ffd700;
        border-radius: 0 8px 8px 0;
    }
    .matrix-item h4 { margin: 0 0 5px 0; color: #81ecec; font-size: 1em; }
    .matrix-item p { margin: 0; font-size: 0.95em; color: #ccc; }
    .matrix-tags span {
        display: inline-block; background: #333; color: #fff;
        padding: 2px 6px; border-radius: 3px; font-size: 0.8em;
        margin-right: 5px; margin-top: 5px; border: 1px solid #555;
    }

    /* Bridge Section Style */
    .bridge-box {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px dashed #FF4B4B;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 30px 0;
        position: relative;
    }
    .bridge-title { color: #FF4500; font-weight: bold; font-size: 1.2em; margin-bottom: 10px; }
    .bridge-arrow { font-size: 2em; color: #FFD700; margin: 10px 0; animation: bounce 2s infinite; }
    .bridge-text { color: #ddd; font-size: 0.95em; line-height: 1.6; }

    /* 籤詩動畫區 */
    .divination-box {
        text-align: center; padding: 30px; background-color: rgba(255,0,0,0.1);
        border: 2px solid #FFD700; border-radius: 15px; animation: pulse 2s infinite;
    }
    .lot-card {
        font-size: 2.5em; color: #FFD700; text-shadow: 0 0 20px #FFD700; margin: 20px 0; font-weight: bold;
    }
    @keyframes pulse { 0% {box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4);} 70% {box-shadow: 0 0 0 10px rgba(255, 215, 0, 0);} 100% {box-shadow: 0 0 0 0 rgba(255, 215, 0, 0);} }

    /* 全螢幕覆蓋層樣式 */
    .fullscreen-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(0, 0, 0, 0.95); z-index: 9999999;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        text-align: center; backdrop-filter: blur(5px);
    }
    .matrix-text {
        color: #0F0; font-family: 'Courier New', monospace; font-size: 2em;
        text-shadow: 0 0 10px #0F0; margin-bottom: 20px;
    }
    .cosmic-text {
        color: #FFD700; font-family: 'Georgia', serif; font-size: 2.5em;
        text-shadow: 0 0 20px #FFD700; animation: pulse-gold 1s infinite alternate;
    }
    @keyframes pulse-gold { from { opacity: 0.6; transform: scale(0.95); } to { opacity: 1; transform: scale(1.05); } }
    </style>
    <div class="sidebar-hint">👈 點此開啟駕駛艙 (商城/客服)</div>
    """, unsafe_allow_html=True)

# === 進站廣播 ===
if 'toast_shown' not in st.session_state:
    st.toast('👋 歡迎來到 AliVerse！點擊左上角「>」開啟駕駛艙，領取您的開運裝備。', icon='🏎️')
    st.session_state['toast_shown'] = True

# === 初始化 Session State ===
if 'unlocked' not in st.session_state:
    st.session_state['unlocked'] = False

# === 側邊欄 ===
with st.sidebar:
    st.markdown("## 👨‍✈️ 駕駛員中心")
    st.info("👋 歡迎來到 AliVerse 愛力宇宙數據中心。")
    st.link_button("🛒 前往官方商城 (贊助開發)", "https://aliverse-shop.fourthwall.com/", type="primary") 
    st.markdown("---")
    st.markdown("**📡 訊號連結**")
    st.link_button("📺 觀看 YouTube 頻道", "https://www.youtube.com/@Ali_Universe") 
    st.link_button("💬 加入 LINE 官方帳號", "https://lin.ee/3woTmES")
    st.markdown("---")
    st.markdown("### 📢 系統公告")
    st.success("✅ 目前版本：V50.2 (品牌純淨終極版)")
    with st.expander("📜 點此查看版本更新軌跡"):
        st.markdown("""
        **V50.2 (品牌純淨)**
        - 🚫 強力隱藏上方工具列與下方 Hosted 標籤，打造沉浸式體驗。

        **V50.0 (旗艦整合)**
        - 🎨 智能關鍵字著色：文案中的五行與顏色自動高亮。
        - 🔗 改裝戰略整合：將「車相建議」與「流年運勢」結合。
        """)
    st.markdown("---")
    st.markdown("© 2026 AliVerse")

# --- 主視覺 ---
st.markdown("""
<div class="hero-container">
<h1 class="hero-title">AliVerse 愛力宇宙</h1>
<p class="hero-subtitle">科技命理・生命載具調校專家</p>
<div class="hero-intro">
歡迎來到 AliVerse 原廠檢測中心。<br>
我們結合<span class="highlight">【八字．五行．十神．易經】</span><br>
為您進行全方位的生命載具數據分析與運勢解卦。<br>
</div>
</div>
""", unsafe_allow_html=True)

# --- 輸入區域 ---
with st.container(border=True):
    st.markdown("### 🛠️ 建立您的駕駛檔案")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 姓名 / 代號", value="", placeholder="請輸入您的姓名")
    with col2:
        gender = st.radio("⚥ 性別規格", ["男", "女"], horizontal=True)
    
    st.write("") 
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
    if 'analyzed' not in st.session_state: st.session_state['analyzed'] = False
    submit_btn = st.button("🚀 啟動引擎 (開始分析)")

# --- 核心邏輯函式庫 ---
COLOR_MAP = {
    "木": "#4CAF50", # 綠
    "火": "#FF5252", # 紅
    "土": "#FFC107", # 黃
    "金": "#E0E0E0", # 白
    "水": "#2196F3"  # 藍
}

# [V50.0 New] 智能關鍵字著色引擎
def highlight_keywords(text):
    """
    自動偵測文案中的五行、顏色等關鍵字，並套用對應的 HTML 顏色樣式。
    """
    keyword_colors = {
        # 五行
        "木": "#4CAF50", "火": "#FF5252", "土": "#FFC107", "金": "#E0E0E0", "水": "#2196F3",
        # 顏色 (Wood)
        "綠": "#4CAF50", "青": "#4CAF50", "藍綠": "#20B2AA",
        # 顏色 (Fire)
        "紅": "#FF5252", "紫": "#E040FB", "粉": "#FF80AB", "橘": "#FF6E40", "亮橘": "#FF6E40",
        # 顏色 (Earth)
        "黃": "#FFD700", "棕": "#8D6E63", "咖啡": "#8D6E63", "米": "#FFE082", "卡其": "#FFE082",
        # 顏色 (Metal)
        "白": "#FFFFFF", "銀": "#E0E0E0", "金": "#FFD700", "灰": "#9E9E9E",
        # 顏色 (Water)
        "黑": "#90A4AE", "藍": "#2196F3", "深藍": "#1565C0",
        # 特殊材質
        "碳纖維": "#B0BEC5", "麂皮": "#FF8A65", "實木": "#D7CCC8"
    }
    
    # 進行替換 (使用正則表達式避免重複替換標籤內的字)
    for kw, color in keyword_colors.items():
        # 簡單替換 (注意：這裡簡化處理，若有關鍵字重疊可能需更複雜邏輯)
        # 為了避免替換掉 HTML tag 裡面的字，我們只替換那些沒有被 < > 包圍的字，但這裡用簡單 replace
        # 技巧：先檢查是否已經被 span 包裹 (這裡暫略，假設輸入純文字)
        text = text.replace(kw, f"<span style='color:{color}; font-weight:bold;'>{kw}</span>")
    
    return text

def get_colored_text(elements_list):
    html_str = ""
    for el in elements_list:
        color = COLOR_MAP.get(el, "#FFF")
        html_str += f"<span style='color:{color}; font-weight:bold; margin-right:3px;'>{el}</span>"
    return html_str

# 舊的簡易上色函式 (保留相容性)
def highlight_text_elements(text):
    for char, color in COLOR_MAP.items():
        text = text.replace(char, f"<span style='color:{color}; font-weight:bold;'>{char}</span>")
    return text

def get_ten_god(day_master, target_stem):
    if day_master == target_stem: return "比肩"
    stems_info = {
        "甲": ("木", 1), "乙": ("木", 0), "丙": ("火", 1), "丁": ("火", 0), "戊": ("土", 1), 
        "己": ("土", 0), "庚": ("金", 1), "辛": ("金", 0), "壬": ("水", 1), "癸": ("水", 0)
    }
    if day_master not in stems_info or target_stem not in stems_info: return ""
    dm_wx, dm_yinyang = stems_info[day_master]
    tg_wx, tg_yinyang = stems_info[target_stem]
    relations = {
        "木": {"火": "生", "水": "被生", "土": "剋", "金": "被剋", "木": "同"},
        "火": {"土": "生", "木": "被生", "金": "剋", "水": "被剋", "火": "同"},
        "土": {"金": "生", "火": "被生", "水": "剋", "木": "被剋", "土": "同"},
        "金": {"水": "生", "土": "被生", "木": "剋", "火": "被剋", "金": "同"},
        "水": {"木": "生", "金": "被生", "火": "剋", "土": "被剋", "水": "同"}
    }
    rel = relations[dm_wx][tg_wx]
    same_yinyang = (dm_yinyang == tg_yinyang)
    if rel == "同": return "比肩" if same_yinyang else "劫財"
    if rel == "生": return "食神" if same_yinyang else "傷官"
    if rel == "被生": return "偏印" if same_yinyang else "正印"
    if rel == "剋": return "偏財" if same_yinyang else "正財"
    if rel == "被剋": return "七殺" if same_yinyang else "正官"
    return ""

def get_hidden_stems(branch):
    hidden_map = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"], "卯": ["乙"],
        "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"], "午": ["丁", "己"], "未": ["己", "丁", "乙"],
        "申": ["庚", "壬", "戊"], "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
    }
    return hidden_map.get(branch, [])

# ==========================================
# [Logic] 全系統喜忌神同步判定邏輯 (含專家覆寫)
# ==========================================
def determine_fates_guide(day_master, month_idx):
    """
    根據日主與出生月，決定【喜用神】與【忌神】
    expert_override: 針對特定格局 (如 Ali 的壬水酉月) 給予精準建議
    return: (joyful_list, taboo_list, description)
    """
    joyful = []
    taboo = []
    reason = ""

    # [Expert Override] 針對 Ali (壬水日主，秋天金旺)
    if day_master == "水" and month_idx in [7, 8, 9, 10]:
        joyful = ["火", "木"]
        taboo = ["金", "水"]
        reason = "格局金水過旺，能量急需釋放。喜用【火、木】，需要火來煉金成器（財星壞印），木來輸出才華（食傷洩秀）。忌【金、水】，引擎本體已過強，不需再加重負擔。"
        return joyful, taboo, reason
    
    if day_master == "水" and month_idx in [11, 12, 1]: # 冬天水
        joyful = ["火", "木"]
        taboo = ["水", "金"]
        reason = "生於隆冬，水寒金冷。首重【火】來調候溫暖，喜【木】來順生。忌金水過旺導致結冰不動。"
        return joyful, taboo, reason

    # [General Fallback] 簡易季節判斷
    if 2 <= month_idx <= 4: # 春
        if day_master in ["木", "火"]: joyful = ["金", "土"]; taboo = ["木", "火"]
        else: joyful = ["土", "金"]; taboo = ["木", "水"]
    elif 5 <= month_idx <= 7: # 夏
        if day_master in ["火", "土"]: joyful = ["水", "金"]; taboo = ["火", "木"]
        else: joyful = ["木", "火"] if day_master!="水" else ["金","水"]; taboo = ["金","水"] if day_master!="水" else ["火","土"]
    elif 8 <= month_idx <= 10: # 秋
        if day_master in ["金", "水"]: joyful = ["火", "木"]; taboo = ["金", "土"]
        else: joyful = ["土", "金"]; taboo = ["火", "木"]
    else: # 冬
        if day_master in ["水", "木"]: joyful = ["火", "土"]; taboo = ["水", "金"]
        else: joyful = ["金", "水"]; taboo = ["火", "土"]
            
    if not joyful: joyful = ["火", "木"]; taboo = ["金", "水"]; reason = "能量平衡建議：喜火木，忌金水。"
        
    return joyful, taboo, reason


# ==========================================
# [V50.0] AliVerse 64卦車相矩陣核心引擎 (含目的性文案)
# ==========================================
def get_aliverse_car_matrix(day_master, lucky_element):
    # 1. 八卦定義資料庫
    trigrams = {
        '乾': {'name': '乾', 'nature': '天', 'symbol': '☰', 'style': '旗艦豪華轎車 / 超跑', 'color': '金屬銀、珍珠白、香檳金', 'engine': 'V8/V12 大排量自然進氣', 'vibe': '尊貴、領袖氣場、經典', 'part': '金'},
        '兌': {'name': '兌', 'nature': '澤', 'symbol': '☱', 'style': '雙門 Coupe / 敞篷車', 'color': '白色、杏色、淺灰', 'engine': '精緻小排量 / 油電混合', 'vibe': '享樂、時尚、拉風', 'part': '金'},
        '離': {'name': '離', 'nature': '火', 'symbol': '☲', 'style': '流線性能跑車', 'color': '法拉利紅、亮紫、亮橘', 'engine': '高轉速 NA / 電子輔助強', 'vibe': '熱情、吸睛、速度', 'part': '火'},
        '震': {'name': '震', 'nature': '雷', 'symbol': '☳', 'style': '重改裝車 / 美式肌肉車', 'color': '賽車綠、青色、賽車塗裝', 'engine': '大渦輪增壓 (Turbo)', 'vibe': '爆發力、貼背感、震撼', 'part': '木'},
        '巽': {'name': '巽', 'nature': '風', 'symbol': '☴', 'style': '流線旅行車 / 掀背鋼砲', 'color': '消光黑、藍綠、變色龍', 'engine': '雙渦輪 / 空氣力學優化', 'vibe': '操控、靈活、高速', 'part': '木'},
        '坎': {'name': '坎', 'nature': '水', 'symbol': '☵', 'style': '黑頭車 / 豪華房車', 'color': '深邃黑、午夜藍', 'engine': '水冷強化 / 智能駕駛系統', 'vibe': '深沉、智謀、流動', 'part': '水'},
        '艮': {'name': '艮', 'nature': '山', 'symbol': '☶', 'style': '大型 SUV / G-Car / 皮卡', 'color': '土黃、咖啡、軍綠、水泥灰', 'engine': '柴油動力 / 大扭力四驅', 'vibe': '穩重、防禦、靠山', 'part': '土'},
        '坤': {'name': '坤', 'nature': '地', 'symbol': '☷', 'style': '豪華 MPV / 保母車', 'color': '黃色、大地色、消光', 'engine': '平順動力 / 氣壓懸吊', 'vibe': '包容、承載、舒適', 'part': '土'}
    }

    # 2. 映射邏輯
    dm_map = {'甲': '震', '乙': '巽', '丙': '離', '丁': '離', '戊': '艮', '己': '坤', '庚': '乾', '辛': '兌', '壬': '坎', '癸': '坎'}
    lucky_map = {'木': '巽', '火': '離', '土': '艮', '金': '乾', '水': '坎'}

    lower_key = dm_map.get(day_master, '乾')
    upper_key = lucky_map.get(lucky_element, '離')
    
    lower = trigrams[lower_key]
    upper = trigrams[upper_key]

    # 3. 文案生成 (加入目的導向)
    hexagram_name = f"{upper['nature']}{lower['nature']}卦"
    
    look_text = f"上卦為【{upper['name']} ({upper['nature']})】，這是能為您帶來平衡的「開運形象」。"
    look_text += f" 由於您的本命磁場需要{upper['part']}來調和，建議外觀選擇 **{upper['style']}** 風格。"
    look_text += f" 車色首選 **{upper['color']}**，**目的是轉化您原本的氣場，對外展現「{upper['vibe']}」的強大吸引力，吸引貴人目光**。"
    
    soul_text = f"下卦為【{lower['name']} ({lower['nature']})】，這代表您身為駕駛者的「原始靈魂」。"
    soul_text += f" 您的日主為「{day_master}」，本質上具備 **{lower['engine']}** 的特性。"
    soul_text += f" 雖然外表{upper['vibe']}，但您內在追求的是「{lower['vibe']}」的真實感受。"

    tuning_text = ""
    tuning_purpose = "" # 用於最後整合分析
    
    # 特殊判斷：Ali 的強金水喜火格局 (外火內水)
    if (upper['nature'] == '火' and lower['nature'] == '水') or (upper['nature'] == '水' and lower['nature'] == '火'):
         tuning_text = "這是一個「水火既濟」的完美平衡。您的本命金水過旺（容易給人冷冽、掉漆的感覺），因此**絕不能再選黑、白、銀色車**。"
         tuning_text += " 建議透過**「火」**的能量來煉金：內裝大膽採用**紅色縫線、紅色安全帶或 Alcantara 麂皮**。改裝重點在於**排氣聲浪**（聲名大噪），**目的是用熱情的火來溫暖原本冰冷的金水引擎，防止運勢故障，並在事業彎道上展現「霸氣超車」的決心**。"
         tuning_purpose = "透過火系改裝（紅色、聲浪）來「暖局煉金」，達成彎道超車與突破現狀的目的。"
    
    elif upper['part'] == lower['part']:
        tuning_text = "上下卦五行氣場相同，能量極為純粹。**不建議過度改裝外觀**，應維持原廠的設計語彙。重點放在車內清潔與「氣味」管理，**目的是保持能量流通，讓思緒如光纖般清晰**。"
        tuning_purpose = "維持原廠純粹能量，透過氣場管理來提升決策清晰度。"
    
    elif (upper['part'] == '火' and lower['part'] == '金') or (upper['part'] == '金' and lower['part'] == '木'):
        tuning_text = "此卦象帶有「火煉金」或「金剋木」的張力，代表這台車能激發您的戰鬥力。建議升級**煞車系統 (Brembo 等)** 與 **抓地力強的輪胎**，**目的是強化您的「控制力」，讓您在高速衝刺事業時，依然能穩穩抓住機會**。"
        tuning_purpose = "強化制動與抓地力，提升對局勢的掌控權。"
    
    else:
        extra_material = "真皮" if lower['part'] == '土' else "碳纖維飾板"
        tuning_text = f"這是一個相生的組合。因您的喜用神為{lucky_element}，建議在車身細節（如輪框蓋、後照鏡）點綴 **{upper['color']}**。內裝部分，建議多用{extra_material}，**目的是最大化五行相生的運勢，讓財運與貴人運源源不絕**。"
        tuning_purpose = f"透過五行相生改裝，增強貴人運與財運的流動。"

    verdict_text = f"經由 AliVerse 運算，您的專屬車相為【外{upper['nature']}內{lower['nature']}】。這台車是您「改運」的法器。"
    verdict_text += f" 它利用 **{upper['nature']} ({upper['vibe']})** 的外在形象，來平衡您內在 **{lower['nature']} ({lower['vibe']})** 的過強能量，達到真正的陰陽調和。"

    # 套用關鍵字上色
    look_text = highlight_keywords(look_text)
    soul_text = highlight_keywords(soul_text)
    tuning_text = highlight_keywords(tuning_text)
    verdict_text = highlight_keywords(verdict_text)

    return {
        "hex_name": hexagram_name,
        "symbol_upper": upper['symbol'],
        "symbol_lower": lower['symbol'],
        "upper_desc": f"外觀(喜用)：{upper['name']} ({upper['nature']})",
        "lower_desc": f"動力(本命)：{lower['name']} ({lower['nature']})",
        "look_text": look_text,
        "look_tags": [upper['style'], upper['color']],
        "soul_text": soul_text,
        "soul_tags": [lower['engine'], lower['vibe']],
        "tuning_text": tuning_text,
        "tuning_purpose": tuning_purpose, # 傳出目的，供最後整合使用
        "verdict_text": verdict_text
    }

# --- 運算 ---
if submit_btn:
    st.session_state['analyzed'] = True
    st.session_state['divination_done'] = False 
    st.session_state['unlocked'] = False
    st.session_state['do_scroll_to'] = 'result-anchor' # [V44] 設定啟動後捲動目標

if st.session_state['analyzed']:
    if inp_year is None or inp_month is None or inp_day is None or birth_hour is None:
        st.error("⚠️ 資料不完整，請檢查輸入。")
        st.stop()

    try:
        birth_date = datetime.date(int(inp_year), int(inp_month), int(inp_day))
    except ValueError:
        st.error("⚠️ 日期格式錯誤。")
        st.stop()
    
    display_name = name if name.strip() else "貴賓"
    
    # 排盤
    hour_map_rev = {
        "00:00 - 00:59 (早子)": 0, "01:00 - 02:59 (丑)": 2, "03:00 - 04:59 (寅)": 4,
        "05:00 - 06:59 (卯)": 6, "07:00 - 08:59 (辰)": 8, "09:00 - 10:59 (巳)": 10,
        "11:00 - 12:59 (午)": 12, "13:00 - 14:59 (未)": 14, "15:00 - 16:59 (申)": 16,
        "17:00 - 18:59 (酉)": 18, "19:00 - 20:59 (戌)": 20, "21:00 - 22:59 (亥)": 22,
        "23:00 - 23:59 (晚子)": 23
    }
    h_idx = hour_map_rev.get(birth_hour, 12)
    solar = Solar.fromYmdHms(birth_date.year, birth_date.month, birth_date.day, h_idx, 0, 0)
    lunar = solar.getLunar()
    bazi = lunar.getEightChar()
    lunar_year = lunar.getYearInGanZhi()
    lunar_month_cn = lunar.getMonthInChinese()
    lunar_day_cn = lunar.getDayInChinese()
    zodiac = lunar.getYearShengXiao()
    
    wuxing_map = {
        "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
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
    
    day_master_wx = wuxing_map.get(day_gan) 
    resource_wx = [k for k, v in producing_map.items() if v == day_master_wx][0]
    
    weights = [(year_gan, 5), (year_zhi, 20), (month_gan, 5), (month_zhi, 35), (day_zhi, 20), (time_gan, 5), (time_zhi, 10)]
    score = 0
    for char, w in weights:
        char_wx = wuxing_map.get(char)
        if char_wx == day_master_wx or char_wx == resource_wx:
            score += w
    
    # 計算格局分數
    strength_type = ""
    ascii_art = ""
    base_type = ""
    
    if score >= 85:
        strength_type = f"從強格 (特殊) {score}%"
        base_type = "🛡️ 重裝坦克"
        ascii_art = """   ░░░░░░░░░░░░░░░░░\n  ░░░░▄▄████▄▄░░░░░░\n  ░░░██████████░░░░░\n  ░▄▄████████████▄▄░\n  █  AliVerse Tank █\n  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀"""
        soul_message = f"親愛的 {day_master_wx} 行坦克駕駛：世界是用來征服的。但最強的履帶也需要潤滑，偶爾示弱不是輸，而是為了走更遠的路。"
    elif score > 45: 
        strength_type = f"身強 (Strong) {score}%"
        base_type = "🚜 全地形越野車"
        ascii_art = """      ____  \n     /  | \_ \n    |___|___\_\n    (o)----(o)\n   [ SUV-4WD ]"""
        soul_message = f"親愛的 {day_master_wx} 行越野車駕駛：您的能量像座活火山，不給它出口（才華/事業），就會在內部爆炸。請大膽地去冒險，舒適圈是您的監獄。"
    elif score >= 15:
        strength_type = f"身弱 (Weak) {score}%"
        base_type = "🏎️ 經典跑車/房車"
        ascii_art = """      ______\n     /  |   \_\n    |___|_____\__\n    (o)-----(o)\n    [  SEDAN  ]"""
        soul_message = f"親愛的 {day_master_wx} 行跑車駕駛：別羨慕坦克的耐撞，您的價值在於精準與優雅。這世界太吵，您需要的是懂您的副駕駛（夥伴）和高品質的保養（學習）。"
    else:
        strength_type = f"從弱格 (特殊) {score}%"
        base_type = "🛸 未來概念車"
        ascii_art = """      .---.\n    _/__~__\_\n   (_________)\n    /       \ \n   [   UFO   ]"""
        soul_message = f"親愛的 {day_master_wx} 行概念車駕駛：您是變色龍。不要被世俗的「自我」框架綁住。當您與趨勢合而為一，您就是趨勢本身。"

    # =======================================================
    # [V48.0 Upgrade] 使用新函數同步喜忌神
    # =======================================================
    joyful_gods, taboo_gods, god_reason = determine_fates_guide(day_master_wx, int(inp_month))

    # 提早定義顏色與運勢
    factory_color_hex = COLOR_MAP.get(day_master_wx, "#888")
    
    lucky_colors_list = [color_dict['name'] for wx in joyful_gods for name, color_dict in {'木':{'name':'叢林綠'}, '火':{'name':'法拉利紅'}, '土':{'name':'大地棕'}, '金':{'name':'鈦金銀'}, '水':{'name':'深海藍'}}.items() if name == wx]
    taboo_colors_list = [color_dict['name'] for wx in taboo_gods for name, color_dict in {'木':{'name':'叢林綠'}, '火':{'name':'法拉利紅'}, '土':{'name':'大地棕'}, '金':{'name':'鈦金銀'}, '水':{'name':'深海藍'}}.items() if name == wx]
    
    lucky_html = get_colored_text(joyful_gods)
    taboo_html = get_colored_text(taboo_gods)

    advice_2026 = ""
    if "火" in joyful_gods:
        advice_2026 = "2026 丙午火年，對您來說是絕佳的「氮氣加速」機會！流年火氣正旺，剛好補足您的動力缺口。易經卦象建議：大膽超車，創業或投資皆有利。"
    else:
        advice_2026 = "2026 丙午火年，火氣過旺，容易導致引擎過熱（情緒急躁、發炎）。易經卦象建議：切換至「定速巡航」模式，多穿戴「水/金」能量（藍/白）來降溫平衡。"

    def get_real_car_model(upper_num, lower_num):
        if upper_num == 1: return "Bugatti Chiron" if lower_num==1 else "Rolls-Royce" if lower_num==3 else "Mercedes-Benz S-Class"
        if upper_num == 8: return "Toyota Alphard" if lower_num==8 else "Range Rover" if lower_num==3 else "Land Cruiser"
        if upper_num == 3: return "Ferrari F8" if lower_num==3 else "Porsche 911"
        if upper_num == 6: return "Tesla Model S" if lower_num==6 else "BMW i7"
        if upper_num == 4: return "Nissan GT-R"
        if upper_num == 5: return "McLaren 720S"
        if upper_num == 7: return "Mercedes-Benz G-Class"
        if upper_num == 2: return "Mazda MX-5"
        return "Lexus LC500"
    
    def get_car_quote(upper_num, lower_num):
        if upper_num == 1: return "你的目標在雲端，不與凡車爭道。"
        if upper_num == 8: return "厚德載物，能容納所有人的夢想。"
        if upper_num == 3: return "你的存在就是為了燃燒與尖叫。"
        if upper_num == 6: return "適應力強，科技感十足。"
        return "獨特品味，融合了多種優點。"

    upper_num = (int(inp_year) + int(inp_month) + int(inp_day)) % 8
    if upper_num == 0: upper_num = 8
    hour_num = (h_idx // 2) + 1
    if h_idx == 23: hour_num = 1
    lower_num = (int(inp_year) + int(inp_month) + int(inp_day) + hour_num) % 8
    if lower_num == 0: lower_num = 8
    
    real_car_model = get_real_car_model(upper_num, lower_num)
    car_quote = get_car_quote(upper_num, lower_num)

    # --- 動畫 ---
    if submit_btn:
        animation_placeholder = st.empty()
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
        for s in range(0, 81, 5):
            show_hud(s, "系統暖機程序啟動...", "color: #39FF14; text-shadow: 0 0 15px #39FF14;")
            time.sleep(0.02)
        for s in range(81, 181, 10):
            show_hud(s, "十神系統連線中...", "color: #FFD700; text-shadow: 0 0 20px #FFD700;")
            time.sleep(0.01)
        for s in range(181, 281, 15):
            show_hud(s, "動力極限輸出！⚠️", "color: #FF4500; text-shadow: 0 0 25px #FF4500;")
            time.sleep(0.01)
        animation_placeholder.empty()

    # --- 結果顯示 ---
    st.write("---")
    # [V44] 插入錨點：結果區
    st.markdown("<div id='result-anchor'></div>", unsafe_allow_html=True)
    # [V44] 執行自動捲動 (檢查訊號)
    if st.session_state.get('do_scroll_to') == 'result-anchor':
        scroll_to('result-anchor')
        st.session_state['do_scroll_to'] = None # 重置訊號

    # [V49] 步驟一：原廠規格
    st.subheader("🏎️ 步驟一：原廠出廠規格 (Original Spec)")
    
    car_card_html = (
        f'<div style="padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); border: 2px solid {factory_color_hex}; background-color: rgba(0,0,0,0.3);">'
        f'<h2 style="margin-bottom: 5px; color: #fff;">{base_type}</h2>'
        f'<div style="color: #FFD700; font-weight: bold; margin-bottom: 10px;">{real_car_model}</div>'
        f'<div class="ascii-art">{ascii_art}</div>'
        f'<div class="god-tag-container">'
        f'<div class="god-box"><div class="god-label">引擎規格</div><div class="god-value neutral">{strength_type}</div></div>'
        f'<div class="god-box"><div class="god-label">幸運燃料 (喜用)</div><div class="god-value">{lucky_html}</div></div>'
        f'<div class="god-box"><div class="god-label">引擎殺手 (忌神)</div><div class="god-value">{taboo_html}</div></div>'
        f'</div>'
        f'<p style="font-style: italic; color: #aaa; margin-top: 15px; font-size: 0.9em;">"{car_quote}"</p>'
        f'</div>'
    )
    st.markdown(car_card_html, unsafe_allow_html=True)

    # =======================================================
    # [V49] 橋樑：技師總監的改裝診斷 (The Bridge)
    # =======================================================
    taboo_str = "、".join(taboo_gods)
    joyful_str = "、".join(joyful_gods)
    
    diagnosis_html = f"""
    <div class="bridge-box">
        <div class="bridge-title">🔧 技師總監的改裝診斷</div>
        <div class="bridge-text">
            檢測報告顯示，您的原廠設定（本命）中，{highlight_keywords(taboo_str)} 能量過高。<br>
            若維持原廠設定上路，容易出現動力遲滯（運勢受阻）或機件過冷（人際冷淡）。<br>
            <br>
            <b>👨‍🔧 解決方案：</b><br>
            我們批准了一套 <b>【{highlight_keywords(joyful_str)}系】</b> 的空力套件與塗裝升級。<br>
            這不是為了改變您的本質，而是為了<b>平衡</b>，讓您跑得更順、更穩！
        </div>
        <div class="bridge-arrow">⬇</div>
    </div>
    """
    st.markdown(diagnosis_html, unsafe_allow_html=True)
    # =======================================================

    # --- 鎖定區域 (色彩行銷文案) ---
    st.write("---")
    st.markdown("""
    <div class="lock-box">
        <div class="lock-title">🔐 權限鎖定：愛力宇宙轉運站</div>
        <div class="lock-desc" style="line-height: 1.8;">
            歡迎前往官方 LINE『愛力宇宙轉運站』，這不只是一組密碼。<br>
            這是一套結合 <span style="color:#FFD700; font-weight:bold;">梅花易數</span> 與 <span style="color:#00BFFF; font-weight:bold;">個人八字</span> 的精密運算系統。<br>
            <br>
            加入即享 <span style="color:#FF4500; font-weight:bold; font-size:1.1em;">永久專屬免費</span> 權益：<br>
            1. 🔓 解鎖您的 <b>八字五行能量圖表</b> 與 <b>深度靈魂解析</b><br>
            2. ⛩️ 啟動 <b>每日即時線上天時地利卜卦</b> (時空交感)<br>
            3. 🚀 獲取 <b>2026 火馬年專屬流年導航</b><br>
            <br>
            <span style="color:#aaa; font-size:0.9em;">(名額有限，請把握與宇宙連線的機會)</span>
            <br><br>
            1. <a href="https://lin.ee/3woTmES" target="_blank" class="line-link">👉 點此加入 LINE 官方帳號</a><br>
            2. 輸入關鍵字<b>『888』</b>獲取通關密碼
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("unlock_form"):
        c_lock1, c_lock2, c_lock3 = st.columns([1, 2, 1])
        with c_lock2:
            user_code = st.text_input("🔑 輸入解鎖碼", placeholder="請輸入官方 LINE 提供的通關密碼", label_visibility="collapsed")
        
        col_sub1, col_sub2, col_sub3 = st.columns([1, 1, 1])
        with col_sub2:
            unlock_submitted = st.form_submit_button("🧬 啟動天機解碼")

    if unlock_submitted and user_code in VALID_CODES:
        st.session_state['unlocked'] = True
        st.session_state['do_scroll_to'] = 'driver-anchor' # [V44] 設定解鎖後捲動目標
        
        # Matrix Animation
        matrix_placeholder = st.empty()
        for i in range(15):
            random_code = "".join([random.choice("01XYZΩ") for _ in range(30)])
            matrix_placeholder.markdown(
                f"""
                <div class="fullscreen-overlay">
                    <div class="matrix-text">{random_code}<br>SYSTEM DECODING...</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            time.sleep(0.1)
        matrix_placeholder.empty()
        st.success("✅ 驗證成功！天機已解密。")
        
    elif unlock_submitted and user_code not in VALID_CODES:
        st.error("⛔ 密碼錯誤，請輸入官方 LINE 提供的通關密碼")

    # --- 解鎖後顯示內容 ---
    if st.session_state['unlocked']:
        
        # 1. 四柱八字
        # [V44] 插入錨點：駕駛員設定
        st.markdown("<div id='driver-anchor'></div>", unsafe_allow_html=True)
        # [V44] 執行自動捲動
        if st.session_state.get('do_scroll_to') == 'driver-anchor':
            scroll_to('driver-anchor')
            st.session_state['do_scroll_to'] = None

        st.subheader("📄 駕駛員靈魂原廠設定 (十神解析)") # [V44] 文案優化
        dm_color = COLOR_MAP.get(day_master_wx, "#fff")
        st.markdown(f"**農曆：{lunar_year}年 {lunar_month_cn}月 {lunar_day_cn}** (屬{zodiac} • 日主<span style='color:{dm_color}'>{day_gan}{day_master_wx}</span>)", unsafe_allow_html=True)
        
        cols = st.columns(4)
        for i, (title, gan_char, zhi_char) in enumerate(pillars_data):
            gan_wx = wuxing_map.get(gan_char, "")
            zhi_wx = wuxing_map.get(zhi_char, "")
            ten_god_gan = "日主" if i == 2 else get_ten_god(day_gan, gan_char)
            hidden_stems = get_hidden_stems(zhi_char)
            hidden_gods = [get_ten_god(day_gan, s) for s in hidden_stems]
            hidden_display = []
            for stem, god in zip(hidden_stems, hidden_gods):
                hidden_display.append(f"<div class='hidden-stem-row'><span>{god}</span> <span>{stem}</span></div>")
            
            with cols[i]:
                html_block = f"""
                <div class="bazi-table">
                    <div class="bazi-header">{title}</div>
                    <div class="ten-god-main">{ten_god_gan}</div>
                    <h3 class="gan-char" style="color: {COLOR_MAP.get(gan_wx, '#FFF')}">{gan_char}</h3>
                    <h3 class="zhi-char" style="color: {COLOR_MAP.get(zhi_wx, '#FFF')}">{zhi_char}</h3>
                    <div class="hidden-stems">{''.join(hidden_display)}</div>
                </div>
                """
                st.markdown(html_block, unsafe_allow_html=True)

        with st.expander("📖 十神白話文對照表 (點此展開)"):
            st.markdown("""
            * **比肩/劫財 (朋友/競爭)**：代表同儕、意志力、也代表花錢。
            * **食神/傷官 (才華/叛逆)**：代表創意、表達、表演、但也可能招惹是非。
            * **正財/偏財 (薪水/投資)**：代表財富、現實、掌控慾。
            * **正官/七殺 (名聲/壓力)**：代表地位、責任、也代表災難或霸氣。
            * **正印/偏印 (貴人/靈感)**：代表學習、保護、母親、長輩緣。
            """)

        # 2. 靈魂導航
        st.write("---")
        st.subheader("🧠 引擎調校與靈魂導航")
        colored_soul_message = highlight_keywords(soul_message)
        colored_god_reason = highlight_keywords(god_reason)
        st.markdown(f"""<div class="soul-message">{colored_soul_message}</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="deep-dive-box"><b>🔧 技師診斷書 (格局分析)：</b><br>{colored_god_reason}</div>""", unsafe_allow_html=True)

        # 3. 圖表
        st.write("---")
        st.subheader("📊 五行能量庫存")
        counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        total_count = 0
        for char in [p[1] for p in pillars_data] + [p[2] for p in pillars_data]:
            wx = wuxing_map.get(char)
            if wx in counts: counts[wx] += 1; total_count += 1
        
        data = []
        for wx, count in counts.items():
            percentage = count / total_count if total_count > 0 else 0
            label_text = f"{wx} {percentage:.0%}" 
            data.append({"五行": wx, "數量": count, "標籤": label_text, "color": COLOR_MAP[wx]})
        df = pd.DataFrame(data)
        
        base = alt.Chart(df).encode(theta=alt.Theta("數量", stack=True).sort("descending"))
        pie = base.mark_arc(outerRadius=80).encode(
            color=alt.Color("color", scale=None),
            order=alt.Order("數量", sort="descending"),
            tooltip=["五行", "數量", "標籤"]
        )
        text = base.mark_text(radius=110).encode(
            text="標籤",
            order=alt.Order("數量", sort="descending"),
            color=alt.value("white")
        )
        chart_pie = (pie + text).properties(title="能量佔比 (Pie)")
        
        chart_bar = alt.Chart(df).mark_bar().encode(
            x=alt.X('五行', axis=alt.Axis(labelAngle=0, title="")),
            y=alt.Y('數量', axis=alt.Axis(title="數量", titleAngle=0, titleAlign="right", titleY=-10)),
            color=alt.Color('color', scale=None),
            tooltip=["五行", "數量"]
        ).properties(title="數量統計 (Bar)")

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1: st.altair_chart(chart_pie, use_container_width=True)
        with col_chart2: st.altair_chart(chart_bar, use_container_width=True)

        # ----------------------------------------------------
        # [AliVerse] 64卦車相矩陣顯示區
        # ----------------------------------------------------
        st.write("---")
        
        # [V49] 步驟二：改裝方案
        st.subheader("🔧 步驟二：AliVerse 傳說改裝廠 (Custom Tuning)")
        
        # 使用同步判定好的 joyful_gods[0] (第一喜用神)
        primary_lucky = joyful_gods[0]
        matrix_data = get_aliverse_car_matrix(day_gan, primary_lucky)

        st.markdown(f"<h3 style='text-align: center; color: #ffd700; margin-bottom: 20px;'>AliVerse 64卦車相矩陣：{matrix_data['hex_name']}</h3>", unsafe_allow_html=True)

        # 顯示卦象符號與架構
        c_mat1, c_mat2, c_mat3 = st.columns([1, 3, 1])
        with c_mat2:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 15px;">
                <div class="hex-symbol">{matrix_data['symbol_upper']}<br>{matrix_data['symbol_lower']}</div>
                <div style="color: #aaa; font-size: 0.9em; letter-spacing: 1px;">
                    {matrix_data['upper_desc']} <span style="color:#ff4757; margin:0 5px;">×</span> {matrix_data['lower_desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 顯示矩陣詳細內容
        st.markdown(f"""
        <div class="matrix-box">
            <div class="matrix-item">
                <h4><i class="fas fa-car"></i> 經典車型畫像 (The Look)</h4>
                <p>{matrix_data['look_text']}</p>
                <div class="matrix-tags"><span>{matrix_data['look_tags'][0]}</span><span>{matrix_data['look_tags'][1]}</span></div>
            </div>
            <div class="matrix-item">
                <h4><i class="fas fa-cogs"></i> 引擎與性能靈魂 (The Soul)</h4>
                <p>{matrix_data['soul_text']}</p>
                <div class="matrix-tags"><span>{matrix_data['soul_tags'][0]}</span><span>{matrix_data['soul_tags'][1]}</span></div>
            </div>
            <div class="matrix-item">
                <h4><i class="fas fa-wrench"></i> AliVerse 改裝特調 (The Tuning)</h4>
                <p style="color: #ffd700;">{matrix_data['tuning_text']}</p>
            </div>
            <div class="matrix-item" style="border-left-color: #ff4757; background: rgba(255, 71, 87, 0.08);">
                <h4><i class="fas fa-bolt"></i> 運勢總評 (The Verdict)</h4>
                <p>{matrix_data['verdict_text']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ----------------------------------------------------
        # [END] AliVerse 64卦車相矩陣
        # ----------------------------------------------------

        # 4. 互動式時空卜卦
        st.write("---")
        st.subheader("🔥 2026 (丙午火馬年) 時空運勢占卜")
        
        if 'divination_done' not in st.session_state:
            st.session_state['divination_done'] = False
            
        if not st.session_state['divination_done']:
            st.info("👇 請輸入一個字或數字，結合當下時空與您的意念，啟動 2026 專屬卦象...")
            
            with st.form(key='divination_form'):
                div_input = st.text_input("✍️ 請在此輸入您的直覺字/數：", placeholder="例如：8, 心, 贏...")
                submit_div = st.form_submit_button("🙏 誠心啟動時空卜卦")
            
            if submit_div:
                if div_input:
                    # 全螢幕卜卦動畫
                    anim_placeholder = st.empty()
                    for _ in range(20): # 2秒動畫
                        anim_placeholder.markdown(
                            f"""
                            <div class="fullscreen-overlay">
                                <div class="cosmic-text">
                                    ✦ 天地交感中 ✦<br>
                                    <span style="font-size:0.5em; color:#fff;">正在連結宇宙資料庫...</span>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        time.sleep(0.1)
                    anim_placeholder.empty()
                    
                    st.session_state['divination_done'] = True
                    st.session_state['user_div_input'] = div_input
                    st.session_state['div_time'] = datetime.datetime.now()
                    st.session_state['do_scroll_to'] = 'divination-anchor' # [V44] 設定卜卦後捲動目標
                    st.rerun()
                else:
                    st.warning("請先輸入一個字或數字，讓系統捕捉您的意念。")
        else:
            # [V44] 插入錨點：卜卦結果
            st.markdown("<div id='divination-anchor'></div>", unsafe_allow_html=True)
            # [V44] 執行自動捲動
            if st.session_state.get('do_scroll_to') == 'divination-anchor':
                scroll_to('divination-anchor')
                st.session_state['do_scroll_to'] = None

            div_time = st.session_state.get('div_time', datetime.datetime.now())
            user_input_val = st.session_state.get('user_div_input', 'A')
            current_solar = Solar.fromYmdHms(div_time.year, div_time.month, div_time.day, div_time.hour, div_time.minute, 0)
            current_lunar = current_solar.getLunar()
            time_ganzhi = f"{current_lunar.getYearInGanZhi()}年 {current_lunar.getMonthInChinese()}月 {current_lunar.getDayInChinese()} {current_lunar.getTimeZhi()}時"
            input_hash = sum([ord(c) for c in user_input_val])
            seed_val = input_hash + div_time.second
            
            gua_list = [
                ("乾為天", "大吉", "飛龍在天，利見大人。", "強勢突破，但需注意姿態。"),
                ("坤為地", "吉", "厚德載物，君子以厚德載物。", "順勢而為，包容能成大事。"),
                ("水火既濟", "中吉", "初吉終亂，需防守成。", "目前狀態極佳，但要小心物極必反。"),
                ("火水未濟", "吉", "君子以慎辨物居方。", "充滿無限可能，是將想法落地的好時機。"),
                ("火天大有", "大吉", "日麗中天，遍照萬物。", "資源豐富，貴人顯現，適合大展鴻圖。"),
                ("地山謙", "吉", "謙謙君子，用涉大川。", "低調謙虛，反而能獲得最大利益。")
            ]
            gua_idx = seed_val % len(gua_list)
            gua_name, gua_luck, gua_text, gua_advice = gua_list[gua_idx]
            
            st.markdown(f"""
            <div class="divination-box">
                <div style="font-size:0.9em; color:#aaa;">占卜時間：{time_ganzhi}</div>
                <div style="font-size:1.2em; color:#fff; margin-top:5px;">✨ 意念『{user_input_val}』與時空共振結果 ✨</div>
                <div class="lot-card">{gua_luck}籤：{gua_name}</div>
                <div style="font-style:italic; color:#fff; margin-bottom:10px;">"{gua_text}"</div>
                <div style="color:#FFD700; font-weight:bold;">易經指引：{gua_advice}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # [V50.0] 綜合療癒運勢解析 (整合改裝建議)
            final_advice = f"""
            嘿，<b>{real_car_model}</b> 的車主！<br><br>
            今年是<b>丙午火馬年</b>，對於你這台 <b>{base_type}</b> 來說，路況是「火力全開」的賽道。<br>
            因為你的引擎（日主 {get_colored_text([day_master_wx])}）{('喜火，這簡直是你的主場，油門踩到底就對了！') if '火' in joyful_gods else ('忌火，這代表引擎容易過熱，請務必安裝「水冷系統」（冷靜/休息）。')}<br><br>
            
            <b>🛡️ 改裝戰略整合：</b><br>
            {matrix_data['tuning_purpose']}<br><br>
            
            加上你剛剛抽到的<b>「{gua_name}」</b>卦象，顯示你潛意識中渴望<b>{('突破與展現') if '火' in gua_name or '天' in gua_name else ('穩定與積累')}</b>。<br><br>
            👉 <b>全方位能量補給建議：</b><br>
            建議您在 <b>食衣住行育樂</b> 中，多<b>補充和添加</b>您的幸運燃料：<b>{lucky_html}</b>。<br>
            同時要刻意避開 <b>{taboo_html}</b> 能量，以免產生不必要的 {highlight_keywords('能量壓力')} 與 {highlight_keywords('精神內耗')}。<br><br>
            祝你在 2026 的賽道上，不僅跑得快，還能帥氣過彎，安全抵達終點！🚗💨
            """
            
            # 應用高亮 (確保最終輸出也有顏色)
            final_advice = highlight_keywords(final_advice)
            
            st.markdown(f"""
            <div style="background-color: rgba(255, 69, 0, 0.1); padding: 20px; border-radius: 10px; border: 1px solid #FFD700; margin-top: 20px;">
                <h4 style="color: #FF4500; margin-top: 0;">🚀 您的 2026 專屬導航</h4>
                <p style="font-size: 1.1em; line-height: 1.8;">{final_advice}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 5. 分享與下載
            st.write("---")
            
            full_report_text = f"""
【AliVerse 2026 運勢完整報告】
================================
駕駛員：{display_name}
日主本命：{day_gan}{day_master_wx}
原廠車型：{real_car_model} ({base_type})
能量規格：{strength_type} (指數 {score}%)
專屬車相：{matrix_data['hex_name']} (外{matrix_data['upper_desc'].split('：')[1]} 內{matrix_data['lower_desc'].split('：')[1]})
================================
【時空占卜紀錄】
占卜時間：{time_ganzhi}
靈動意念：{user_input_val}
得卦：{gua_name} ({gua_luck})
卦辭：{gua_text}
================================
【2026 火馬年路況】
{advice_2026}
================================
【易經指引】
{gua_advice}
================================
【幸運改裝方案】
幸運燃料：{'、'.join(lucky_colors_list)}
避凶警示：{'、'.join(taboo_colors_list)}
改裝戰略：{matrix_data['tuning_purpose']}
================================
AliVerse 愛力宇宙 - 科技命理
立即測算：https://aliverse-bazi.streamlit.app
"""
            c_share1, c_share2 = st.columns(2)
            with c_share1:
                st.download_button(
                    label="📄 下載完整運勢報告",
                    data=full_report_text.encode('utf-8'),
                    file_name=f"AliVerse_2026_{display_name}.txt",
                    mime="text/plain"
                )
            
            fun_share_text = f"🏎️ 我剛剛在 AliVerse 測出來，我是 {real_car_model}！\n車相矩陣顯示是「{matrix_data['hex_name']}」！\n易經卜卦說我 2026 年要{'火力全開' if '火' in joyful_gods else '注意過熱'}！\n你也來測測看你是什麼車？\n👉 https://aliverse-bazi.streamlit.app"
            
            st.info("👇 點擊右上角複製按鈕，分享到 IG/LINE：")
            st.code(fun_share_text, language="text")
            
            line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(fun_share_text)}"
            st.markdown(f'<a href="{line_url}" target="_blank" style="text-decoration:none;"><div class="line-btn">💚 分享至 LINE</div></a>', unsafe_allow_html=True)

    elif user_code:
        st.error("⛔ 密碼錯誤，請輸入官方 LINE 提供的通關密碼")
