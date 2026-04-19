import sys
import os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd
import bcrypt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_DIR      = os.path.abspath(os.path.dirname(__file__))
csv_path      = os.path.join(BASE_DIR, "../data/processed/exercises_cleaned.csv")
progress_file = os.path.join(BASE_DIR, "../data/user/progress.csv")
users_file    = os.path.join(BASE_DIR, "../data/user/users.csv")
os.makedirs(os.path.dirname(progress_file), exist_ok=True)

if not os.path.isfile(progress_file):
    pd.DataFrame(columns=["date","weight","steps","sleep_time"]).to_csv(progress_file, index=False)
if not os.path.isfile(users_file):
    pd.DataFrame(columns=["email","password"]).to_csv(users_file, index=False)

df = pd.read_csv(csv_path)
df["Burns Calories"] = pd.to_numeric(df["Burns Calories"], errors="coerce")

st.set_page_config(
    page_title="FitCore",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [data-testid="stAppViewContainer"] {
  color-scheme: dark !important;
}

:root {
  --s0: #000000;
  --s1: #0f0f0f;
  --s2: #1a1a1a;
  --s3: #242424;
  --bd: rgba(255,255,255,0.07);
  --bd2: rgba(255,255,255,0.13);
  --red: #ff375f;
  --blue: #0a84ff;
  --green: #30d158;
  --orange: #ff9f0a;
  --font: 'Inter', -apple-system, sans-serif;
  --snap: cubic-bezier(0.16,1,0.3,1);
  --ease: cubic-bezier(0.25,0.46,0.45,0.94);
  --spr:  cubic-bezier(0.34,1.56,0.64,1);
  --r2: 13px; --r3: 18px; --r4: 24px;
}

@keyframes fadeUp  { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn  { from{opacity:0} to{opacity:1} }
@keyframes scaleIn { from{opacity:0;transform:scale(0.93)} to{opacity:1;transform:scale(1)} }
@keyframes popIn   { 0%{opacity:0;transform:scale(0.84)} 65%{transform:scale(1.03)} 100%{opacity:1;transform:scale(1)} }
@keyframes chatR   { from{opacity:0;transform:translateX(14px)} to{opacity:1;transform:translateX(0)} }
@keyframes chatL   { from{opacity:0;transform:translateX(-14px)} to{opacity:1;transform:translateX(0)} }
@keyframes spin    { to{transform:rotate(360deg)} }

/* ── App shell ── */
.stApp {
  background: #000000 !important;
  font-family: var(--font) !important;
  color: #ffffff !important;
  -webkit-font-smoothing: antialiased !important;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }

[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
button[kind="header"] { display:none !important; }

.main .block-container {
  padding: 2rem 2.5rem 4rem !important;
  max-width: 1100px !important;
}

/* ── Nuke all ghost backgrounds ── */
.stMarkdown, [data-testid="stMarkdownContainer"],
[data-testid="stText"], [data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"], [data-testid="element-container"],
.element-container, .stElementContainer,
[data-testid="stWidgetLabel"], .stWidgetLabel,
[data-testid="stCaptionContainer"] {
  background: transparent !important;
  background-color: transparent !important;
}

/* ── Typography ── */
p, li, span, div, label,
.stMarkdown p, .stMarkdown li,
[data-testid="stMarkdownContainer"] p {
  font-family: var(--font) !important;
  color: rgba(255,255,255,0.62) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.62) !important;
  line-height: 1.6 !important;
}
h1, h2, h3, h4,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: var(--font) !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  letter-spacing: -0.03em !important;
}
h1, .stMarkdown h1 {
  font-size: clamp(1.9rem,5vw,3.2rem) !important;
  font-weight: 900 !important;
  line-height: 1.05 !important;
}
h2, .stMarkdown h2 {
  font-size: clamp(1.15rem,3vw,1.6rem) !important;
  font-weight: 700 !important;
}
h3, .stMarkdown h3 {
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  color: rgba(255,255,255,0.38) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.38) !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
}
strong, b {
  font-weight: 700 !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
.stCaption, [data-testid="stCaptionContainer"] p {
  color: rgba(255,255,255,0.36) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.36) !important;
  font-size: 0.78rem !important;
}
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
[data-testid="stText"], [data-testid="stWrite"] {
  color: rgba(255,255,255,0.62) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.62) !important;
  font-family: var(--font) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.07) !important;
  border-radius: 13px !important;
  padding: 5px !important;
  gap: 3px !important;
  animation: fadeIn 0.4s var(--ease) both;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-radius: 9px !important;
  padding: 9px 18px !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  font-size: 0.84rem !important;
  letter-spacing: -0.01em !important;
  color: rgba(255,255,255,0.38) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.38) !important;
  transition: all 0.18s var(--ease) !important;
  flex: 1 !important;
  text-align: center !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: rgba(255,255,255,0.65) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.65) !important;
  background: #1a1a1a !important;
}
.stTabs [aria-selected="true"] {
  background: #242424 !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  box-shadow: 0 1px 5px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.13) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding: 24px 0 0 !important;
  animation: fadeUp 0.32s var(--snap) both;
}

/* ── Buttons ── */
.stButton > button {
  background: #1a1a1a !important;
  border: 1px solid rgba(255,255,255,0.13) !important;
  border-radius: 13px !important;
  padding: 11px 22px !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  font-size: 0.87rem !important;
  letter-spacing: -0.01em !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  transition: all 0.16s var(--ease) !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.5) !important;
}
.stButton > button:hover {
  background: #242424 !important;
  border-color: rgba(255,255,255,0.22) !important;
  transform: scale(1.02) !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.55) !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
.stButton > button:active {
  transform: scale(0.97) !important;
  background: #0f0f0f !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}

/* Form submit — red */
.stFormSubmitButton > button {
  background: #ff375f !important;
  border: none !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 20px rgba(255,55,95,0.38) !important;
}
.stFormSubmitButton > button:hover {
  background: #ff526e !important;
  transform: scale(1.02) !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  box-shadow: 0 6px 26px rgba(255,55,95,0.52) !important;
}

/* Link button */
.stLinkButton > a {
  background: #ff375f !important;
  border: none !important;
  border-radius: 13px !important;
  padding: 12px 24px !important;
  font-family: var(--font) !important;
  font-weight: 700 !important;
  font-size: 0.88rem !important;
  letter-spacing: -0.01em !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  text-decoration: none !important;
  display: inline-block !important;
  transition: all 0.18s var(--ease) !important;
  box-shadow: 0 4px 16px rgba(255,55,95,0.38) !important;
}
.stLinkButton > a:hover {
  background: #ff526e !important;
  transform: scale(1.02) !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  box-shadow: 0 6px 24px rgba(255,55,95,0.52) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.13) !important;
  border-radius: 13px !important;
  padding: 12px 15px !important;
  font-family: var(--font) !important;
  font-size: 0.93rem !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.4) !important;
  transition: all 0.16s var(--ease) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
  border-color: #0a84ff !important;
  background: #1a1a1a !important;
  box-shadow: 0 0 0 3px rgba(10,132,255,0.18), inset 0 1px 3px rgba(0,0,0,0.3) !important;
  outline: none !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea textarea::placeholder {
  color: rgba(255,255,255,0.18) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.18) !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stMultiSelect label, .stSlider label, .stDateInput label,
.stTextArea label, .stWidgetLabel p {
  font-family: var(--font) !important;
  font-weight: 600 !important;
  font-size: 0.71rem !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
  color: rgba(255,255,255,0.38) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.38) !important;
}

/* ── Select / Multiselect ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.13) !important;
  border-radius: 13px !important;
}
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
  background: transparent !important;
  border: none !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-family: var(--font) !important;
}
[data-baseweb="select"] span {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
[data-baseweb="popover"] [data-baseweb="menu"] {
  background: #1c1c1e !important;
  border: 1px solid rgba(255,255,255,0.13) !important;
  border-radius: 18px !important;
  box-shadow: 0 20px 60px rgba(0,0,0,0.85) !important;
  animation: scaleIn 0.14s var(--snap) both !important;
  overflow: hidden !important;
}
[data-baseweb="option"] {
  background: transparent !important;
  color: rgba(255,255,255,0.65) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.65) !important;
  font-family: var(--font) !important;
  font-size: 0.9rem !important;
  padding: 12px 16px !important;
}
[data-baseweb="option"]:hover {
  background: rgba(255,255,255,0.06) !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
[data-baseweb="tag"] {
  background: rgba(10,132,255,0.18) !important;
  border: 1px solid rgba(10,132,255,0.38) !important;
  border-radius: 8px !important;
  color: #0a84ff !important;
  -webkit-text-fill-color: #0a84ff !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  font-size: 0.79rem !important;
  animation: popIn 0.2s var(--spr) both;
}

/* ── Sliders ── */
.stSlider > div > div > div {
  background: #1a1a1a !important;
  border-radius: 99px !important;
}
[data-testid="stSlider"] [role="slider"] {
  background: #ffffff !important;
  border-radius: 50% !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.7) !important;
  transition: transform 0.14s var(--spr) !important;
}
[data-testid="stSlider"] [role="slider"]:hover { transform: scale(1.22) !important; }
[data-testid="stSlider"] [data-baseweb="slider"] [role="progressbar"] {
  background: #ff375f !important;
  border-radius: 99px !important;
}
[data-testid="stSlider"] p,
[data-testid="stTickBarMin"],
[data-testid="stTickBarMax"] {
  color: rgba(255,255,255,0.38) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.38) !important;
}

/* ── Date input ── */
.stDateInput > div > div {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.13) !important;
  border-radius: 13px !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-family: var(--font) !important;
}

/* ── Form ── */
[data-testid="stForm"] {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.07) !important;
  border-radius: 22px !important;
  padding: 26px 22px !important;
  box-shadow: 0 4px 28px rgba(0,0,0,0.45) !important;
  animation: fadeUp 0.38s var(--snap) both;
}

/* ── Dataframe — THE FIX ── */
.stDataFrame {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.07) !important;
  border-radius: 16px !important;
  overflow: hidden !important;
  box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
  animation: fadeUp 0.38s var(--snap) both;
  color-scheme: dark !important;
}
.stDataFrame * {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-family: var(--font) !important;
}
/* Force the iframe inside the dataframe to use dark mode */
.stDataFrame iframe {
  color-scheme: dark !important;
  background: #0f0f0f !important;
}
[data-testid="stDataFrameResizable"] {
  color-scheme: dark !important;
  background: #0f0f0f !important;
}
[data-testid="stDataFrameResizable"] iframe {
  color-scheme: dark !important;
}

/* ── Chat ── */
.stChatMessage {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.07) !important;
  border-radius: 16px !important;
  padding: 16px 20px !important;
  margin: 8px 0 !important;
}
.stChatMessage:hover { border-color: rgba(255,255,255,0.13) !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: rgba(10,132,255,0.09) !important;
  border-color: rgba(10,132,255,0.22) !important;
  margin-left: 48px !important;
  animation: chatR 0.28s var(--snap) both !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
  margin-right: 48px !important;
  animation: chatL 0.28s var(--snap) both !important;
}
.stChatMessage p, .stChatMessage div, .stChatMessage span {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  background: transparent !important;
  font-family: var(--font) !important;
}
.stChatInput > div {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.13) !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
}
.stChatInput > div:focus-within {
  border-color: #0a84ff !important;
  box-shadow: 0 0 0 3px rgba(10,132,255,0.14) !important;
}
.stChatInput textarea {
  background: transparent !important;
  border: none !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-family: var(--font) !important;
}

/* ── Alerts ── */
.stSuccess {
  background: rgba(48,209,88,0.07) !important;
  border: 1px solid rgba(48,209,88,0.25) !important;
  border-radius: 13px !important;
  animation: popIn 0.22s var(--spr) both !important;
}
.stError {
  background: rgba(255,55,95,0.07) !important;
  border: 1px solid rgba(255,55,95,0.25) !important;
  border-radius: 13px !important;
  animation: popIn 0.22s var(--spr) both !important;
}
.stWarning {
  background: rgba(255,159,10,0.07) !important;
  border: 1px solid rgba(255,159,10,0.25) !important;
  border-radius: 13px !important;
  animation: popIn 0.22s var(--spr) both !important;
}
.stInfo {
  background: rgba(10,132,255,0.07) !important;
  border: 1px solid rgba(10,132,255,0.25) !important;
  border-radius: 13px !important;
  animation: popIn 0.22s var(--spr) both !important;
}
.stSuccess p, .stSuccess span, .stSuccess div,
.stError p,   .stError span,   .stError div,
.stWarning p, .stWarning span, .stWarning div,
.stInfo p,    .stInfo span,    .stInfo div {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  background: transparent !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.07) !important;
  border-radius: 13px !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  color: rgba(255,255,255,0.65) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.65) !important;
}
.streamlit-expanderHeader:hover {
  background: #1a1a1a !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
.streamlit-expanderContent {
  background: #0f0f0f !important;
  border: 1px solid rgba(255,255,255,0.07) !important;
  border-top: none !important;
  border-radius: 0 0 13px 13px !important;
}

/* ── Metrics ── */
[data-testid="stMetricValue"] {
  font-family: var(--font) !important;
  font-weight: 800 !important;
  font-size: 1.8rem !important;
  letter-spacing: -0.04em !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
[data-testid="stMetricLabel"] {
  font-family: var(--font) !important;
  font-weight: 600 !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
  color: rgba(255,255,255,0.38) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.38) !important;
}

/* ── Progress bar ── */
.stProgress > div > div { background: #1a1a1a !important; border-radius: 99px !important; }
.stProgress > div > div > div {
  background: #ff375f !important;
  border-radius: 99px !important;
  box-shadow: 0 0 10px rgba(255,55,95,0.35) !important;
}

/* ── Divider ── */
hr {
  border: none !important;
  height: 1px !important;
  background: rgba(255,255,255,0.07) !important;
  margin: 24px 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2e2e2e; border-radius: 99px; }

/* ── Images ── */
.stImage img {
  border-radius: 16px !important;
  border: 1px solid rgba(255,255,255,0.07) !important;
  transition: all 0.18s ease !important;
}
.stImage img:hover {
  transform: scale(1.02) !important;
  border-color: rgba(255,255,255,0.13) !important;
}

/* ── Number input buttons ── */
.stNumberInput button {
  background: #1a1a1a !important;
  border: 1px solid rgba(255,255,255,0.13) !important;
  border-radius: 8px !important;
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
.stNumberInput button:hover {
  background: #242424 !important;
  transform: scale(1.12) !important;
}

/* ── Spinner ── */
.stSpinner > div {
  border-color: #ff375f transparent transparent transparent !important;
  animation: spin 0.7s linear infinite !important;
}

/* ── Stagger ── */
[data-testid="stVerticalBlock"] > div:nth-child(1) { animation: fadeUp 0.38s 0.04s var(--snap) both }
[data-testid="stVerticalBlock"] > div:nth-child(2) { animation: fadeUp 0.38s 0.08s var(--snap) both }
[data-testid="stVerticalBlock"] > div:nth-child(3) { animation: fadeUp 0.38s 0.12s var(--snap) both }
[data-testid="stVerticalBlock"] > div:nth-child(4) { animation: fadeUp 0.38s 0.16s var(--snap) both }
[data-testid="stVerticalBlock"] > div:nth-child(5) { animation: fadeUp 0.38s 0.20s var(--snap) both }
[data-testid="stVerticalBlock"] > div:nth-child(6) { animation: fadeUp 0.38s 0.24s var(--snap) both }

[data-testid="column"] { padding: 0 6px !important; }

/* ── Mobile ── */
@media (max-width: 768px) {
  .main .block-container { padding: 1rem 1rem 3rem !important; }
  .stTabs [data-baseweb="tab"] { padding: 8px 8px !important; font-size: 0.74rem !important; }
  .stTabs [data-baseweb="tab-list"] { padding: 4px !important; gap: 2px !important; }
  .stButton > button, .stFormSubmitButton > button { width: 100% !important; }
  [data-testid="stForm"] { padding: 18px 14px !important; }
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { margin-left: 0 !important; }
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) { margin-right: 0 !important; }
  [data-testid="column"] { padding: 0 3px !important; }
}
@media (max-width: 480px) {
  h1, .stMarkdown h1 { font-size: 1.6rem !important; }
  .stTabs [data-baseweb="tab"] { font-size: 0.67rem !important; padding: 7px 5px !important; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AUTH helpers
# ─────────────────────────────────────────────────────────────────────────────
def hash_password(pw):  return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw, h): return bcrypt.checkpw(pw.encode(), h.encode())
def load_users():       return pd.read_csv(users_file)

def save_user(email, pw):
    users = load_users()
    if email in users["email"].values:
        return False
    users = pd.concat(
        [users, pd.DataFrame([{"email": email, "password": hash_password(pw)}])],
        ignore_index=True
    )
    users.to_csv(users_file, index=False)
    return True


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

from analyses.filter_data   import filter_data
from analyses.nutrition_chat import chat_with_history
from analyses.nutrition_search import search_foods


# ─────────────────────────────────────────────────────────────────────────────
# DARK TABLE HELPER — renders a pandas DataFrame as a styled HTML table
# so it's always dark regardless of Streamlit's iframe color-scheme
# ─────────────────────────────────────────────────────────────────────────────
def dark_table(dataframe, link_col=None):
    """Render a DataFrame as a dark HTML table inside st.markdown."""
    df_render = dataframe.copy()
    cols = list(df_render.columns)

    rows_html = ""
    for _, row in df_render.iterrows():
        cells = ""
        for col in cols:
            val = row[col]
            if link_col and col == link_col and str(val) not in ("#", "", "—"):
                cell_content = f'<a href="{val}" target="_blank" style="color:#0a84ff;text-decoration:none;font-weight:600">Open ↗</a>'
            else:
                cell_content = str(val) if val is not None else "—"
            cells += f'<td style="padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.06);color:rgba(255,255,255,0.82);font-size:0.85rem;white-space:nowrap">{cell_content}</td>'
        rows_html += f"<tr>{cells}</tr>"

    headers = ""
    for col in cols:
        if link_col and col == link_col:
            label = "Details"
        else:
            label = col
        headers += f'<th style="padding:10px 14px;text-align:left;font-size:0.7rem;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:rgba(255,255,255,0.38);border-bottom:1px solid rgba(255,255,255,0.1);white-space:nowrap">{label}</th>'

    html = f"""
    <div style="width:100%;overflow-x:auto;border-radius:14px;border:1px solid rgba(255,255,255,0.07);background:#0f0f0f;box-shadow:0 4px 24px rgba(0,0,0,0.4);margin-bottom:8px">
      <table style="width:100%;border-collapse:collapse;font-family:'Inter',-apple-system,sans-serif;background:#0f0f0f">
        <thead><tr style="background:#0f0f0f">{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("# FitCore")
        st.markdown("Your personal health & fitness companion.")
        st.markdown("<br>", unsafe_allow_html=True)
        tab_in, tab_up = st.tabs(["Sign In", "Create Account"])
        with tab_in:
            st.markdown("<br>", unsafe_allow_html=True)
            email    = st.text_input("Email",    key="li_email", placeholder="you@example.com")
            password = st.text_input("Password", key="li_pw",    placeholder="••••••••", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", key="li_btn"):
                users = load_users()
                match = users[users["email"] == email]
                if not match.empty and check_password(password, match.iloc[0]["password"]):
                    st.session_state.authenticated = True
                    st.session_state.user = email
                    st.rerun()
                else:
                    st.error("Incorrect email or password.")
        with tab_up:
            st.markdown("<br>", unsafe_allow_html=True)
            ne = st.text_input("Email",    key="su_email", placeholder="you@example.com")
            np = st.text_input("Password", key="su_pw",    placeholder="Create a strong password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", key="su_btn"):
                if save_user(ne, np):
                    st.success("Account created — please sign in.")
                else:
                    st.error("An account with this email already exists.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

# Top bar
col_logo, col_user, col_out = st.columns([6, 3, 1])
with col_logo:
    st.markdown("# 🔥 FitCore")
with col_user:
    st.markdown(f"<br><span style='color:rgba(255,255,255,0.38);font-size:0.82rem'>{st.session_state.user}</span>", unsafe_allow_html=True)
with col_out:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sign out"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

st.markdown("##### Track workouts · Discover nutrition · Build better habits")
st.markdown("<br>", unsafe_allow_html=True)

# ── Quick stats ───────────────────────────────────────────────────────────────
try:
    qdf = pd.read_csv(progress_file)
    qdf["date"] = pd.to_datetime(qdf["date"])
    entries = len(qdf)
    avg_w   = f"{qdf['weight'].mean():.1f} lbs"     if entries else "—"
    avg_s   = f"{int(qdf['steps'].mean())} /day"     if entries else "—"
    avg_sl  = f"{qdf['sleep_time'].mean():.1f} hrs"  if entries else "—"
except Exception:
    entries, avg_w, avg_s, avg_sl = 0, "—", "—", "—"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Days Logged",  str(entries))
c2.metric("Avg Weight",   avg_w)
c3.metric("Avg Steps",    avg_s)
c4.metric("Avg Sleep",    avg_sl)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["💪  Workouts", "🤖  AI Coach", "🥗  Nutrition", "📊  Tracker"])


# ══ WORKOUTS ══════════════════════════════════════════════════════════════════
with tab1:
    st.header("Exercise Finder")
    st.caption("Filter by muscle group, equipment, and intensity")
    st.link_button("Take the Fitness Survey →", "https://docs.google.com/forms/d/e/1FAIpQLSdtK96V0z11r_DRwxdEqCclLHmwz6jk7ndTa193uyXBYyJQ8g/viewform?usp=sharing&ouid=118083238042336260263")
    st.markdown("<br>", unsafe_allow_html=True)

    equipment_options = sorted([
        "Parallel Bars","Chairs","Pull-up Bar","Dumbbell","Barbell",
        "Bench","Platform","Kettlebell","Step","Box",
        "Resistance Band","Cable Machine","Low Bar","TRX","Wall","Sturdy Surface",
    ])
    muscle_options = sorted([
        "Triceps","Chest","Back","Biceps","Core","Obliques",
        "Hamstrings","Glutes","Quadriceps","Rear Deltoids","Upper Back",
        "Shoulders","Calves","Forearms","Full Core","Full Body",
        "Legs","Upper Chest","Lower Chest",
    ])

    calories_min      = st.slider("Min calories burned", 10, 1000, 100)
    calories_max      = st.slider("Max calories burned", 10, 1000, 1000)
    st.markdown("<br>", unsafe_allow_html=True)
    difficulty        = st.multiselect("Difficulty level",      ["Beginner","Intermediate","Advanced"])
    equipment_include = st.multiselect("Required equipment",    equipment_options)
    equipment_exclude = st.multiselect("Exclude equipment",     equipment_options)
    muscle_group      = st.multiselect("Target muscle groups",  muscle_options)
    st.caption("All selected filters use AND logic. Choices within each filter use OR logic.")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Find Workouts →", key="find"):
        results = filter_data(
            df, int(calories_min), int(calories_max),
            difficulty or "All", equipment_include or None,
            equipment_exclude or None, muscle_group or "All",
        )
        if not results.empty:
            st.caption(f"{len(results)} exercises found")
            dark_table(results)
        else:
            st.warning("No exercises match your filters. Try relaxing some criteria.")


# ══ AI COACH ══════════════════════════════════════════════════════════════════
with tab2:
    st.header("AI Nutrition Coach")
    st.caption("Ask anything about food, calories, macros, or your goals")

    if "nutrition_chat" not in st.session_state:
        st.session_state.nutrition_chat = []

    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px">'
        '<span style="font-family:Inter,sans-serif;font-size:0.79rem;font-weight:500;'
        'color:rgba(255,255,255,0.5);background:#1a1a1a;'
        'border:1px solid rgba(255,255,255,0.1);border-radius:99px;padding:6px 14px">'
        'How many calories should I eat?</span>'
        '<span style="font-family:Inter,sans-serif;font-size:0.79rem;font-weight:500;'
        'color:rgba(255,255,255,0.5);background:#1a1a1a;'
        'border:1px solid rgba(255,255,255,0.1);border-radius:99px;padding:6px 14px">'
        'Best foods for muscle gain</span>'
        '<span style="font-family:Inter,sans-serif;font-size:0.79rem;font-weight:500;'
        'color:rgba(255,255,255,0.5);background:#1a1a1a;'
        'border:1px solid rgba(255,255,255,0.1);border-radius:99px;padding:6px 14px">'
        'How much protein do I need?</span>'
        '</div>',
        unsafe_allow_html=True
    )

    col_cl, _ = st.columns([1, 7])
    with col_cl:
        if st.button("Clear chat", key="clr"):
            st.session_state.nutrition_chat = []
            st.rerun()

    for msg in st.session_state.nutrition_chat:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        name   = "You" if msg["role"] == "user" else "FitCore AI"
        with st.chat_message(name, avatar=avatar):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask your nutrition question..."):
        st.session_state.nutrition_chat.append({"role": "user", "content": prompt})
        with st.chat_message("You", avatar="🧑"):
            st.markdown(prompt)
        with st.chat_message("FitCore AI", avatar="🤖"):
            with st.spinner(""):
                answer = chat_with_history(st.session_state.nutrition_chat)
            st.markdown(answer)
        st.session_state.nutrition_chat.append({"role": "assistant", "content": answer})


# ══ NUTRITION ═════════════════════════════════════════════════════════════════
with tab3:
    st.header("Nutrition Database")
    st.caption("Search 900,000+ foods — macros, calories, and more")

    food_query = st.text_input("", key="fq",
        placeholder="🔍  Search any food — banana, oats, chicken breast...")

    if st.button("Search", key="srch"):
        q = (food_query or "").strip()
        if not q:
            st.warning("Please enter a food name.")
        else:
            try:
                st.session_state.results     = search_foods(q)
                st.session_state.page_index  = 0
                st.session_state.query       = q
                st.session_state.nsearch_err = None
            except Exception as exc:
                st.session_state.results     = []
                st.session_state.query       = q
                st.session_state.nsearch_err = str(exc)

    if st.session_state.get("nsearch_err"):
        st.error(st.session_state["nsearch_err"])

    if "results" in st.session_state and st.session_state.results:
        results   = st.session_state.results
        total     = len(results)
        PAGE_SIZE = 6
        num_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        if "page_index" not in st.session_state:
            st.session_state.page_index = 0

        st.caption(f"{total} results for \"{st.session_state.query}\"")

        pc, mc, nc = st.columns([1, 3, 1])
        with pc:
            if st.button("← Prev", key="prev") and st.session_state.page_index > 0:
                st.session_state.page_index -= 1
        with mc:
            st.caption(f"Page {st.session_state.page_index+1} of {num_pages}")
        with nc:
            if st.button("Next →", key="nxt") and st.session_state.page_index < num_pages - 1:
                st.session_state.page_index += 1

        start        = st.session_state.page_index * PAGE_SIZE
        page_results = results[start:start + PAGE_SIZE]
        rows = []

        for food in page_results:
            name = food.get("food_name") or "Unknown"
            url  = food.get("food_url")  or "#"
            kc, fg, cg, pg = (
                food.get("calories"), food.get("fat_g"),
                food.get("carbs_g"),  food.get("protein_g")
            )
            if kc is None and food.get("food_description"):
                info   = food.get("food_description", "")
                mpart  = info.split(" - ", 1)[-1]
                macros = {}
                for chunk in mpart.split("|"):
                    if ":" in chunk:
                        k, v = chunk.split(":", 1)
                        macros[k.strip()] = v.strip()
                cal_s  = macros.get("Calories","—").replace("kcal","").strip()
                fat_s  = macros.get("Fat",     "—")
                carb_s = macros.get("Carbs",   "—")
                prot_s = macros.get("Protein", "—")
            else:
                cal_s  = f"{kc:.0f}"  if kc is not None else "—"
                fat_s  = f"{fg:g} g"  if fg is not None else "—"
                carb_s = f"{cg:g} g"  if cg is not None else "—"
                prot_s = f"{pg:g} g"  if pg is not None else "—"
            rows.append({
                "Product":  name,
                "Brand":    food.get("brand")         or "—",
                "Serving":  food.get("serving_label") or "—",
                "Calories": cal_s, "Fat": fat_s,
                "Carbs":    carb_s, "Protein": prot_s,
                "Link":     url,
            })

        dark_table(pd.DataFrame(rows), link_col="Link")

        with st.expander("View food photos", expanded=False):
            cols = st.columns(3)
            for i, food in enumerate(page_results):
                img = (food.get("image_url") or "").strip()
                with cols[i % 3]:
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("No image")
                    st.caption(food.get("food_name") or "—")

    elif "results" in st.session_state and st.session_state.get("query"):
        st.info('No results. Try a simpler term like "banana" or "chicken".')


# ══ TRACKER ═══════════════════════════════════════════════════════════════════
with tab4:
    st.header("Activity Tracker")
    st.caption("Log daily metrics and watch your progress over time")

    with st.form("prog_form"):
        date       = st.date_input("Date", value=datetime.date.today())
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            weight     = st.number_input("Weight (lbs)",  min_value=0.0, step=0.1, format="%.1f")
        with col_b:
            steps      = st.number_input("Steps",         min_value=0,   step=100)
        with col_c:
            sleep_time = st.number_input("Sleep (hrs)",   min_value=0.0, max_value=24.0, step=0.5, format="%.1f")
        submitted = st.form_submit_button("Log Entry")

    if submitted:
        dp = pd.read_csv(progress_file)
        if date.isoformat() in set(dp["date"]):
            st.warning(f"Entry already exists for {date.strftime('%B %d, %Y')}.")
        else:
            dp = pd.concat([dp, pd.DataFrame([{
                "date": date.isoformat(), "weight": weight,
                "steps": steps, "sleep_time": sleep_time
            }])], ignore_index=True)
            dp.to_csv(progress_file, index=False)
            st.success("Entry logged.")
            st.rerun()

    dp = pd.read_csv(progress_file)
    dp["date"] = pd.to_datetime(dp["date"])
    dp = dp.sort_values("date").reset_index(drop=True)

    ddf = pd.DataFrame({
        "Date":         dp["date"].dt.strftime("%b %d, %Y"),
        "Weight (lbs)": dp["weight"],
        "Steps":        dp["steps"],
        "Sleep (hrs)":  dp["sleep_time"],
    })

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Progress Log")
    dark_table(ddf)

    to_del = st.multiselect(
        "Select entries to remove",
        [f"{d}  ·  {w} lbs" for d, w in zip(ddf["Date"], ddf["Weight (lbs)"])]
    )
    if st.button("Remove Selected") and to_del:
        keep = [f"{d}  ·  {w} lbs" not in to_del
                for d, w in zip(ddf["Date"], ddf["Weight (lbs)"])]
        dp = dp[keep].reset_index(drop=True)
        dp.to_csv(progress_file, index=False)
        st.success(f"Removed {len(to_del)} entr{'y' if len(to_del)==1 else 'ies'}.")
        st.rerun()

    # ── Weight chart ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Weight Trend")

    fig, ax = plt.subplots(figsize=(10, 3.6))
    fig.patch.set_facecolor('#0f0f0f')
    ax.set_facecolor('#0f0f0f')

    dates   = dp["date"]
    weights = dp["weight"]

    if not dates.empty:
        ax.fill_between(dates, weights, alpha=0.10, color='#ff375f', zorder=1)
        ax.plot(
            dates, weights, color='#ff375f', linewidth=2.4, zorder=2,
            marker='o', markersize=6, markerfacecolor='#ff375f',
            markeredgecolor='#000000', markeredgewidth=1.8,
            solid_capstyle='round', solid_joinstyle='round'
        )
        ax.set_xticks(dates)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    dim_white = (1.0, 1.0, 1.0, 0.28)
    ax.set_ylabel("lbs", fontsize=9, fontweight='600', color=dim_white, labelpad=10)
    ax.tick_params(colors=dim_white, labelsize=8.5)
    for sp in ['top', 'right']:
        ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color('#222222')
    ax.spines['left'].set_linewidth(0.7)
    ax.spines['bottom'].set_color('#222222')
    ax.spines['bottom'].set_linewidth(0.7)
    ax.grid(True, alpha=0.06, color='#ffffff', linestyle='--', linewidth=0.7)
    ax.margins(x=0.04)
    fig.autofmt_xdate(rotation=28)
    plt.tight_layout(pad=1.4)
    st.pyplot(fig)

# Footer
st.markdown("---")
st.caption("FitCore · Built for your best self")
