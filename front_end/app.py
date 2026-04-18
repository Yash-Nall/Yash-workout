import sys
import os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd
import bcrypt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
csv_path = os.path.join(BASE_DIR, "../data/processed/exercises_cleaned.csv")
progress_file = os.path.join(BASE_DIR, "../data/user/progress.csv")
users_file = os.path.join(BASE_DIR, "../data/user/users.csv")
os.makedirs(os.path.dirname(progress_file), exist_ok=True)

if not os.path.isfile(progress_file):
    pd.DataFrame(columns=["date", "weight", "steps", "sleep_time"]).to_csv(progress_file, index=False)
if not os.path.isfile(users_file):
    pd.DataFrame(columns=["email", "password"]).to_csv(users_file, index=False)

df = pd.read_csv(csv_path)
df["Burns Calories"] = pd.to_numeric(df["Burns Calories"], errors="coerce")

st.set_page_config(page_title="FitCore — Personal Health", layout="wide", initial_sidebar_state="collapsed")

CSS = """
<style>
/* ─── FONTS ─────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Bebas+Neue&display=swap');

/* ─── DESIGN TOKENS ──────────────────────────────────────────────────────── */
:root {
  --bg:           #0d1b2a;
  --bg2:          #112236;
  --bg3:          #0a1520;
  --s-light:      #1a3050;
  --s-dark:       #060e16;
  --primary:      #4f8ef7;
  --primary-dim:  #2d5eb8;
  --primary-glow: rgba(79,142,247,0.35);
  --accent:       #00d4aa;
  --accent-glow:  rgba(0,212,170,0.30);
  --text:         #e8f0fe;
  --text-sub:     #7a9cc4;
  --text-muted:   #4a6785;
  --border:       rgba(79,142,247,0.12);
  --radius-sm:    10px;
  --radius-md:    16px;
  --radius-lg:    22px;
  --radius-xl:    30px;
  --font:         'Plus Jakarta Sans', sans-serif;
  --font-display: 'Bebas Neue', sans-serif;
  --transition:   all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --spring:       all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ─── KEYFRAMES ──────────────────────────────────────────────────────────── */
@keyframes fadeUp   { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn   { from{opacity:0} to{opacity:1} }
@keyframes slideLeft{ from{opacity:0;transform:translateX(-18px)} to{opacity:1;transform:translateX(0)} }
@keyframes slideRight{from{opacity:0;transform:translateX(18px)} to{opacity:1;transform:translateX(0)} }
@keyframes scaleIn  { from{opacity:0;transform:scale(0.88)} to{opacity:1;transform:scale(1)} }
@keyframes glow-pulse{
  0%,100%{box-shadow:0 0 0 0 var(--primary-glow)}
  50%    {box-shadow:0 0 22px 6px var(--primary-glow)}
}
@keyframes shimmer-text{
  0%  {background-position:0% 50%}
  100%{background-position:200% 50%}
}
@keyframes float{
  0%,100%{transform:translateY(0)}
  50%    {transform:translateY(-5px)}
}
@keyframes scan-line{
  0%  {top:-4px}
  100%{top:100%}
}
@keyframes border-flow{
  0%  {background-position:0% 50%}
  50% {background-position:100% 50%}
  100%{background-position:0% 50%}
}
@keyframes ripple{
  0%  {transform:scale(0);opacity:0.5}
  100%{transform:scale(2.5);opacity:0}
}
@keyframes spin{
  from{transform:rotate(0deg)}
  to  {transform:rotate(360deg)}
}
@keyframes bounce-in{
  0%  {transform:scale(0.5);opacity:0}
  60% {transform:scale(1.1)}
  80% {transform:scale(0.95)}
  100%{transform:scale(1);opacity:1}
}

/* ─── GLOBAL RESET / BASE ────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
  background: var(--bg) !important;
  font-family: var(--font) !important;
  color: var(--text) !important;
  min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden !important; }

/* ─── REMOVE ALL UNWANTED BACKGROUNDS ───────────────────────────────────── */
.stMarkdown, [data-testid="stMarkdownContainer"],
[data-testid="stText"], [data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"], [data-testid="element-container"],
.element-container, .stElementContainer,
[data-testid="stWidgetLabel"], .stWidgetLabel,
[data-testid="stCaptionContainer"] {
  background: transparent !important;
  background-color: transparent !important;
}

/* ─── MAIN CONTAINER ─────────────────────────────────────────────────────── */
.main .block-container {
  padding: 1.5rem 2rem !important;
  max-width: 1140px !important;
  margin: 0 auto !important;
  animation: fadeUp 0.55s ease both;
}

/* ─── TYPOGRAPHY ─────────────────────────────────────────────────────────── */
p, li, span, div, label,
.stMarkdown p, .stMarkdown li,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-family: var(--font) !important;
  line-height: 1.65 !important;
}

h1, h2, h3, h4,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: var(--font) !important;
  color: var(--text) !important;
  letter-spacing: -0.025em !important;
}

/* Gradient animated title */
h1, .stMarkdown h1 {
  font-family: var(--font-display) !important;
  font-size: clamp(2.2rem, 5vw, 3.8rem) !important;
  font-weight: 400 !important;
  letter-spacing: 0.04em !important;
  background: linear-gradient(90deg, #4f8ef7, #00d4aa, #4f8ef7, #a78bfa) !important;
  background-size: 300% auto !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
  animation: shimmer-text 5s linear infinite, fadeUp 0.7s ease both !important;
  line-height: 1.1 !important;
}

h2, .stMarkdown h2 {
  font-size: clamp(1.3rem, 3vw, 1.75rem) !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  animation: fadeUp 0.5s ease both;
}

h3, .stMarkdown h3 {
  font-size: 1.15rem !important;
  font-weight: 600 !important;
  color: var(--text-sub) !important;
  -webkit-text-fill-color: var(--text-sub) !important;
}

/* Subheader */
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
}

/* Caption */
.stCaption, [data-testid="stCaptionContainer"],
.stCaption p, [data-testid="stCaptionContainer"] p {
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
  font-size: 0.8rem !important;
  font-style: italic !important;
}

/* Bold inline text */
strong, b,
.stMarkdown strong, .stMarkdown b {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-weight: 700 !important;
}

/* ─── TABS ───────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg2) !important;
  border-radius: var(--radius-lg) !important;
  padding: 6px !important;
  box-shadow:
    inset 4px 4px 10px var(--s-dark),
    inset -4px -4px 10px var(--s-light),
    0 0 0 1px var(--border) !important;
  gap: 4px !important;
  animation: fadeIn 0.5s ease both;
  flex-wrap: wrap !important;
}

.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: var(--radius-md) !important;
  padding: 10px 18px !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  font-family: var(--font) !important;
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
  border: none !important;
  transition: var(--transition) !important;
  white-space: nowrap !important;
  letter-spacing: 0.01em !important;
}

.stTabs [data-baseweb="tab"]:hover {
  color: var(--text-sub) !important;
  -webkit-text-fill-color: var(--text-sub) !important;
  background: rgba(79,142,247,0.07) !important;
}

.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(79,142,247,0.18), rgba(0,212,170,0.1)) !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  box-shadow:
    inset 3px 3px 8px var(--s-dark),
    inset -3px -3px 8px rgba(79,142,247,0.08),
    0 0 12px var(--primary-glow) !important;
}

.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding: 18px 2px !important;
  animation: fadeUp 0.4s ease both;
}

/* ─── NEUMORPHIC CARD HELPER ─────────────────────────────────────────────── */
.neu-card {
  background: var(--bg2);
  border-radius: var(--radius-lg);
  box-shadow:
    6px 6px 14px var(--s-dark),
    -6px -6px 14px var(--s-light),
    0 0 0 1px var(--border);
  padding: 24px;
  transition: var(--transition);
  animation: fadeUp 0.5s ease both;
}
.neu-card:hover {
  box-shadow:
    8px 8px 18px var(--s-dark),
    -8px -8px 18px var(--s-light),
    0 0 20px var(--primary-glow),
    0 0 0 1px rgba(79,142,247,0.25);
}

/* ─── BUTTONS ────────────────────────────────────────────────────────────── */
.stButton > button {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  padding: 11px 24px !important;
  font-weight: 700 !important;
  font-family: var(--font) !important;
  font-size: 0.88rem !important;
  letter-spacing: 0.02em !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  box-shadow:
    5px 5px 12px var(--s-dark),
    -5px -5px 12px var(--s-light) !important;
  transition: var(--spring) !important;
  position: relative !important;
  overflow: hidden !important;
}

.stButton > button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(79,142,247,0.08), rgba(0,212,170,0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: var(--radius-md);
}

.stButton > button:hover {
  transform: translateY(-3px) scale(1.02) !important;
  border-color: rgba(79,142,247,0.4) !important;
  box-shadow:
    8px 8px 20px var(--s-dark),
    -8px -8px 20px var(--s-light),
    0 6px 20px var(--primary-glow) !important;
  color: #7ab3ff !important;
  -webkit-text-fill-color: #7ab3ff !important;
}
.stButton > button:hover::before { opacity: 1; }

.stButton > button:active {
  transform: translateY(0) scale(0.97) !important;
  box-shadow:
    inset 4px 4px 10px var(--s-dark),
    inset -4px -4px 10px var(--s-light) !important;
}

/* Form submit — accent gradient */
.stFormSubmitButton > button {
  background: linear-gradient(135deg, var(--primary-dim), var(--primary)) !important;
  color: #fff !important;
  -webkit-text-fill-color: #fff !important;
  border: none !important;
  box-shadow:
    5px 5px 15px var(--s-dark),
    0 4px 18px var(--primary-glow) !important;
}
.stFormSubmitButton > button:hover {
  background: linear-gradient(135deg, var(--primary), #6ea8ff) !important;
  box-shadow:
    8px 8px 22px var(--s-dark),
    0 6px 28px rgba(79,142,247,0.55) !important;
}

/* Link button — teal accent */
.stLinkButton > a {
  background: linear-gradient(135deg, #009d7f, var(--accent)) !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  padding: 13px 30px !important;
  font-weight: 700 !important;
  font-family: var(--font) !important;
  font-size: 0.9rem !important;
  letter-spacing: 0.03em !important;
  color: #fff !important;
  -webkit-text-fill-color: #fff !important;
  box-shadow: 5px 5px 15px var(--s-dark), 0 4px 18px var(--accent-glow) !important;
  transition: var(--spring) !important;
  text-decoration: none !important;
  animation: float 3.5s ease-in-out infinite !important;
  display: inline-block !important;
}
.stLinkButton > a:hover {
  transform: translateY(-4px) scale(1.04) !important;
  box-shadow: 8px 8px 24px var(--s-dark), 0 8px 30px rgba(0,212,170,0.5) !important;
}

/* ─── INPUTS ─────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 12px 15px !important;
  box-shadow:
    inset 4px 4px 9px var(--s-dark),
    inset -4px -4px 9px var(--s-light) !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 0.92rem !important;
  transition: var(--transition) !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
  border-color: rgba(79,142,247,0.5) !important;
  box-shadow:
    inset 4px 4px 9px var(--s-dark),
    inset -4px -4px 9px var(--s-light),
    0 0 0 3px rgba(79,142,247,0.12),
    0 0 14px var(--primary-glow) !important;
  outline: none !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea textarea::placeholder {
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
}

/* Input Labels */
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stMultiSelect label,
.stSlider label, .stDateInput label,
.stTextArea label, .stWidgetLabel p {
  color: var(--text-sub) !important;
  -webkit-text-fill-color: var(--text-sub) !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
  font-family: var(--font) !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
  margin-bottom: 5px !important;
}

/* ─── SELECTBOX / MULTISELECT ─────────────────────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  box-shadow:
    inset 4px 4px 9px var(--s-dark),
    inset -4px -4px 9px var(--s-light) !important;
}

.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
  background: transparent !important;
  border: none !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-family: var(--font) !important;
}

[data-baseweb="popover"] [data-baseweb="menu"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow:
    8px 8px 24px var(--s-dark),
    0 0 30px rgba(79,142,247,0.1) !important;
  animation: scaleIn 0.18s ease both !important;
}

[data-baseweb="option"] {
  background: transparent !important;
  color: var(--text-sub) !important;
  -webkit-text-fill-color: var(--text-sub) !important;
  font-family: var(--font) !important;
  font-size: 0.9rem !important;
  transition: background 0.18s ease !important;
}
[data-baseweb="option"]:hover {
  background: rgba(79,142,247,0.12) !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
}

[data-baseweb="tag"] {
  background: linear-gradient(135deg, rgba(79,142,247,0.2), rgba(0,212,170,0.15)) !important;
  border: 1px solid rgba(79,142,247,0.35) !important;
  border-radius: 7px !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  font-family: var(--font) !important;
  font-size: 0.82rem !important;
  animation: bounce-in 0.25s ease both;
}

/* ─── SLIDERS ─────────────────────────────────────────────────────────────── */
.stSlider > div > div > div {
  background: var(--bg3) !important;
  border-radius: 10px !important;
  box-shadow:
    inset 3px 3px 7px var(--s-dark),
    inset -3px -3px 7px var(--s-light) !important;
}

[data-testid="stSlider"] [role="slider"] {
  background: linear-gradient(135deg, var(--primary-dim), var(--primary)) !important;
  border-radius: 50% !important;
  box-shadow:
    3px 3px 8px var(--s-dark),
    0 0 14px var(--primary-glow) !important;
  transition: var(--spring) !important;
}
[data-testid="stSlider"] [role="slider"]:hover {
  transform: scale(1.25) !important;
  animation: glow-pulse 1.5s ease infinite;
}

/* Slider track fill */
[data-testid="stSlider"] [data-baseweb="slider"] [role="progressbar"] {
  background: linear-gradient(90deg, var(--primary-dim), var(--primary)) !important;
}

/* ─── DATAFRAME ───────────────────────────────────────────────────────────── */
.stDataFrame {
  background: var(--bg2) !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  box-shadow:
    6px 6px 14px var(--s-dark),
    -6px -6px 14px var(--s-light) !important;
  overflow: hidden !important;
  animation: fadeUp 0.5s ease both;
}

/* ─── FORMS ───────────────────────────────────────────────────────────────── */
[data-testid="stForm"] {
  background: var(--bg2) !important;
  border-radius: var(--radius-lg) !important;
  border: 1px solid var(--border) !important;
  padding: 28px !important;
  box-shadow:
    8px 8px 20px var(--s-dark),
    -8px -8px 20px var(--s-light) !important;
  animation: fadeUp 0.5s ease both;
}

/* ─── SIDEBAR ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 24px var(--s-dark) !important;
  animation: slideLeft 0.5s ease both;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  background: transparent !important;
}

[data-testid="stSidebar"] .stButton > button {
  width: 100% !important;
  margin-top: 8px !important;
  color: #ff6b6b !important;
  -webkit-text-fill-color: #ff6b6b !important;
  border-color: rgba(255,107,107,0.2) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  color: #ff4444 !important;
  -webkit-text-fill-color: #ff4444 !important;
  border-color: rgba(255,68,68,0.4) !important;
  box-shadow: 8px 8px 20px var(--s-dark), 0 6px 20px rgba(255,107,107,0.25) !important;
}

/* ─── CHAT ────────────────────────────────────────────────────────────────── */
.stChatMessage {
  background: var(--bg2) !important;
  border-radius: var(--radius-lg) !important;
  border: 1px solid var(--border) !important;
  padding: 16px 20px !important;
  margin: 8px 0 !important;
  box-shadow:
    5px 5px 12px var(--s-dark),
    -5px -5px 12px var(--s-light) !important;
  animation: fadeUp 0.38s ease both;
  transition: var(--transition) !important;
}
.stChatMessage:hover {
  border-color: rgba(79,142,247,0.28) !important;
  box-shadow:
    7px 7px 18px var(--s-dark),
    -7px -7px 18px var(--s-light),
    0 0 16px var(--primary-glow) !important;
  transform: translateY(-2px);
}

.stChatMessage p, .stChatMessage span, .stChatMessage div {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  background: transparent !important;
}

.stChatInput > div {
  background: var(--bg2) !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  box-shadow:
    inset 4px 4px 9px var(--s-dark),
    inset -4px -4px 9px var(--s-light) !important;
  transition: var(--transition) !important;
}
.stChatInput > div:focus-within {
  border-color: rgba(79,142,247,0.4) !important;
  box-shadow:
    inset 4px 4px 9px var(--s-dark),
    inset -4px -4px 9px var(--s-light),
    0 0 0 3px rgba(79,142,247,0.1),
    0 0 16px var(--primary-glow) !important;
}
.stChatInput textarea {
  background: transparent !important;
  border: none !important;
  font-family: var(--font) !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
}

/* ─── EXPANDER ────────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
  background: var(--bg2) !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  box-shadow:
    4px 4px 10px var(--s-dark),
    -4px -4px 10px var(--s-light) !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  color: var(--text-sub) !important;
  -webkit-text-fill-color: var(--text-sub) !important;
  transition: var(--transition) !important;
}
.streamlit-expanderHeader:hover {
  border-color: rgba(79,142,247,0.3) !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
}
.streamlit-expanderContent {
  background: var(--bg2) !important;
  border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
}

/* ─── ALERTS ──────────────────────────────────────────────────────────────── */
.stSuccess {
  background: rgba(0,212,170,0.08) !important;
  border: 1px solid rgba(0,212,170,0.3) !important;
  border-left: 4px solid var(--accent) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 4px 16px rgba(0,212,170,0.15) !important;
  animation: bounce-in 0.3s ease both !important;
}
.stWarning {
  background: rgba(255,193,7,0.08) !important;
  border: 1px solid rgba(255,193,7,0.3) !important;
  border-left: 4px solid #ffc107 !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 4px 16px rgba(255,193,7,0.15) !important;
  animation: bounce-in 0.3s ease both !important;
}
.stError {
  background: rgba(255,82,82,0.08) !important;
  border: 1px solid rgba(255,82,82,0.3) !important;
  border-left: 4px solid #ff5252 !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 4px 16px rgba(255,82,82,0.15) !important;
  animation: bounce-in 0.3s ease both !important;
}
.stInfo {
  background: rgba(79,142,247,0.08) !important;
  border: 1px solid rgba(79,142,247,0.3) !important;
  border-left: 4px solid var(--primary) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 4px 16px var(--primary-glow) !important;
  animation: bounce-in 0.3s ease both !important;
}

.stSuccess p, .stSuccess span, .stSuccess div,
.stWarning p, .stWarning span, .stWarning div,
.stError p, .stError span, .stError div,
.stInfo p, .stInfo span, .stInfo div {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  background: transparent !important;
}

/* ─── DATE INPUT ──────────────────────────────────────────────────────────── */
.stDateInput > div > div {
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  box-shadow:
    inset 3px 3px 7px var(--s-dark),
    inset -3px -3px 7px var(--s-light) !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
}

/* ─── METRICS ─────────────────────────────────────────────────────────────── */
[data-testid="stMetricValue"] {
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  font-weight: 800 !important;
  font-family: var(--font-display) !important;
  font-size: 2.2rem !important;
  letter-spacing: 0.02em !important;
}
[data-testid="stMetricLabel"] {
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
  font-size: 0.75rem !important;
}

/* ─── PROGRESS BAR ────────────────────────────────────────────────────────── */
.stProgress > div > div {
  background: var(--bg3) !important;
  border-radius: 99px !important;
  box-shadow: inset 3px 3px 7px var(--s-dark), inset -3px -3px 7px var(--s-light) !important;
}
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--primary-dim), var(--primary), var(--accent)) !important;
  background-size: 200% !important;
  border-radius: 99px !important;
  animation: shimmer-text 2s linear infinite !important;
  box-shadow: 0 0 12px var(--primary-glow) !important;
}

/* ─── SPINNER ─────────────────────────────────────────────────────────────── */
.stSpinner > div {
  border-color: var(--primary) transparent transparent transparent !important;
  animation: spin 0.75s linear infinite !important;
}

/* ─── DIVIDER ─────────────────────────────────────────────────────────────── */
hr {
  border: none !important;
  height: 1px !important;
  background: linear-gradient(90deg, transparent, var(--border), var(--primary-glow), var(--border), transparent) !important;
  margin: 28px 0 !important;
}

/* ─── SCROLLBAR ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track {
  background: var(--bg3);
  border-radius: 99px;
}
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--primary-dim), var(--text-muted));
  border-radius: 99px;
}
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ─── IMAGES ──────────────────────────────────────────────────────────────── */
.stImage img {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border) !important;
  box-shadow:
    4px 4px 14px var(--s-dark),
    0 0 0 1px var(--border) !important;
  transition: var(--transition) !important;
}
.stImage img:hover {
  transform: scale(1.03) translateY(-2px) !important;
  box-shadow:
    8px 8px 24px var(--s-dark),
    0 0 20px var(--primary-glow),
    0 0 0 1px rgba(79,142,247,0.3) !important;
}

/* ─── NUMBER INPUT BUTTONS ────────────────────────────────────────────────── */
.stNumberInput button {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  box-shadow: 3px 3px 7px var(--s-dark), -3px -3px 7px var(--s-light) !important;
  transition: var(--spring) !important;
}
.stNumberInput button:hover {
  transform: scale(1.15) !important;
  box-shadow: 4px 4px 10px var(--s-dark), 0 0 10px var(--primary-glow) !important;
}

/* ─── TOOLTIP ─────────────────────────────────────────────────────────────── */
[data-testid="stTooltipIcon"] { color: var(--text-muted) !important; }

/* ─── MATPLOTLIB / CHART WRAPPER ──────────────────────────────────────────── */
[data-testid="stImage"], .stPlotlyChart {
  border-radius: var(--radius-lg) !important;
  overflow: hidden !important;
  border: 1px solid var(--border) !important;
  box-shadow:
    6px 6px 18px var(--s-dark),
    0 0 30px rgba(79,142,247,0.08) !important;
  animation: fadeUp 0.6s ease both;
}

/* ─── COLUMNS ─────────────────────────────────────────────────────────────── */
[data-testid="column"] { padding: 0 8px !important; }

/* ─── STAGGER FADE DELAYS ─────────────────────────────────────────────────── */
[data-testid="stVerticalBlock"] > div:nth-child(1){animation:fadeUp 0.5s 0.05s ease both}
[data-testid="stVerticalBlock"] > div:nth-child(2){animation:fadeUp 0.5s 0.10s ease both}
[data-testid="stVerticalBlock"] > div:nth-child(3){animation:fadeUp 0.5s 0.15s ease both}
[data-testid="stVerticalBlock"] > div:nth-child(4){animation:fadeUp 0.5s 0.20s ease both}
[data-testid="stVerticalBlock"] > div:nth-child(5){animation:fadeUp 0.5s 0.25s ease both}
[data-testid="stVerticalBlock"] > div:nth-child(6){animation:fadeUp 0.5s 0.30s ease both}

/* ─── MOBILE RESPONSIVE ───────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .main .block-container {
    padding: 1rem 0.75rem !important;
  }

  h1, .stMarkdown h1 {
    font-size: 2rem !important;
  }

  .stTabs [data-baseweb="tab"] {
    padding: 8px 12px !important;
    font-size: 0.78rem !important;
  }

  .stTabs [data-baseweb="tab-list"] {
    gap: 2px !important;
    padding: 5px !important;
  }

  .stButton > button {
    padding: 10px 16px !important;
    font-size: 0.83rem !important;
    width: 100% !important;
  }

  .stLinkButton > a {
    padding: 11px 20px !important;
    font-size: 0.85rem !important;
  }

  [data-testid="stForm"] {
    padding: 18px 14px !important;
  }

  .stChatMessage {
    padding: 12px 14px !important;
  }

  [data-testid="column"] { padding: 0 4px !important; }

  .stDataFrame { font-size: 0.78rem !important; }

  /* Stack number inputs on mobile */
  .stNumberInput > div {
    flex-wrap: wrap !important;
  }
}

@media (max-width: 480px) {
  h1, .stMarkdown h1 { font-size: 1.7rem !important; }
  h2, .stMarkdown h2 { font-size: 1.25rem !important; }

  .stTabs [data-baseweb="tab"] {
    padding: 7px 9px !important;
    font-size: 0.72rem !important;
  }
}

/* ─── WRITE ELEMENTS ──────────────────────────────────────────────────────── */
[data-testid="stText"], [data-testid="stWrite"] {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-family: var(--font) !important;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ===================== AUTH SYSTEM =====================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def load_users():
    return pd.read_csv(users_file)

def save_user(email, password):
    users = load_users()
    if email in users["email"].values:
        return False
    users.loc[len(users)] = [email, hash_password(password)]
    users.to_csv(users_file, index=False)
    return True

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

from analyses.filter_data import filter_data
from analyses.nutrition_chat import chat_with_history
from analyses.nutrition_search import search_foods

# ===================== LOGIN / SIGNUP =====================
if not st.session_state.authenticated:
    st.title("FitCore")
    st.markdown("##### Your personal health assistant. Login or create an account to get started.")
    tab_login, tab_signup = st.tabs(["🔐 Login", "✨ Sign Up"])

    with tab_login:
        email = st.text_input("Email", key="login_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="login_pw", placeholder="Your password")
        if st.button("Login", key="login_btn"):
            users = load_users()
            match = users[users["email"] == email]
            if not match.empty and check_password(password, match.iloc[0]["password"]):
                st.session_state.authenticated = True
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab_signup:
        new_email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
        new_password = st.text_input("Password", type="password", key="signup_pw", placeholder="Create a strong password")
        if st.button("Create Account", key="signup_btn"):
            if save_user(new_email, new_password):
                st.success("Account created! Please log in.")
            else:
                st.error("Email already exists")
    st.stop()

# ===================== LOGGED IN APP =====================
st.sidebar.markdown("### 👤 Account")
st.sidebar.write(f"**{st.session_state.user}**")
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

st.title("FitCore")
st.markdown("##### Build your best self — track, discover, and optimize.")
st.link_button("Start Fitness Survey 🚀", "https://docs.google.com/forms/d/e/1FAIpQLSdtK96V0z11r_DRwxdEqCclLHmwz6jk7ndTa193uyXBYyJQ8g/viewform?usp=sharing&ouid=118083238042336260263")

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["💪 Workout Finder", "🤖 Calorie Chat", "🥗 Nutrition", "📊 Tracker"])

# ── TAB 1: WORKOUT FINDER ────────────────────────────────────────────────────
with tab1:
    st.header("Exercise Recommender")
    equipment_options = sorted([
        "Parallel Bars","Chairs","Pull-up Bar","Dumbbell","Barbell",
        "Bench","Platform","Kettlebell","Step","Box",
        "Resistance Band","Cable Machine","Low Bar","TRX","Wall","Sturdy Surface",
    ])
    muscle_group_options = sorted([
        "Triceps","Chest","Back","Biceps","Core","Obliques",
        "Hamstrings","Glutes","Quadriceps","Rear Deltoids","Upper Back",
        "Shoulders","Calves","Forearms","Full Core","Full Body",
        "Legs","Upper Chest","Lower Chest",
    ])

    col_a, col_b = st.columns(2)
    with col_a:
        calories_min = st.slider("Min calories burned", 10, 1000, 100)
    with col_b:
        calories_max = st.slider("Max calories burned", 10, 1000, 1000)

    difficulty = st.multiselect("Difficulty Level(s)", ["Beginner","Intermediate","Advanced"],
        help="Leave empty for any difficulty.")
    equipment_include = st.multiselect("Include Equipment", equipment_options,
        help="Leave empty for any equipment.")
    equipment_exclude = st.multiselect("Exclude Equipment", equipment_options,
        help="Hide exercises that require any of these.")
    muscle_group = st.multiselect("Muscle Group(s)", muscle_group_options,
        help="Leave empty for any muscle group.")
    st.caption("Filters combine with AND. Within each list, choices use OR.")

    if st.button("🔍 Find Workouts"):
        results = filter_data(
            df, int(calories_min), int(calories_max),
            difficulty or "All", equipment_include or None,
            equipment_exclude or None, muscle_group or "All",
        )
        if not results.empty:
            st.write("**Recommended Workouts:**")
            st.dataframe(results)
        else:
            st.warning("No workouts found. Try adjusting your filters.")

# ── TAB 2: CALORIE CHATBOT ───────────────────────────────────────────────────
with tab2:
    st.header("Calorie Chatbot")
    st.caption("Optional: add GROQ_API_KEY or OPENAI_API_KEY in .streamlit/secrets.toml for AI-powered answers.")

    if "nutrition_chat" not in st.session_state:
        st.session_state.nutrition_chat = []

    if st.button("🗑️ Clear chat", key="clear_chat"):
        st.session_state.nutrition_chat = []
        st.rerun()

    for msg in st.session_state.nutrition_chat:
        role = msg["role"]

# map ugly roles → clean UI labels
        role_icon = {
            "user": "🧑",
            "assistant": "🤖"
        }.get(role, "💬")

        with st.chat_message(role):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about nutrition, calories, or diet..."):
        st.session_state.nutrition_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = chat_with_history(st.session_state.nutrition_chat)
            st.markdown(answer)
        st.session_state.nutrition_chat.append({"role": "assistant", "content": answer})

# ── TAB 3: NUTRITION CALCULATOR ──────────────────────────────────────────────
with tab3:
    st.header("Nutrition Calculator")
    st.caption("Data from Open Food Facts. Results ranked by name relevance.")

    food_query = st.text_input("Search for a food:", key="food_query",
        placeholder="e.g. banana, chicken breast, oats")

    if st.button("🔍 Search", key="search"):
        q = (food_query or "").strip()
        if not q:
            st.warning("Enter a food name first.")
        else:
            try:
                st.session_state.results = search_foods(q)
                st.session_state.page_index = 0
                st.session_state.query = q
                st.session_state.nutrition_search_error = None
            except Exception as exc:
                st.session_state.results = []
                st.session_state.query = q
                st.session_state.nutrition_search_error = str(exc)

    if st.session_state.get("nutrition_search_error"):
        st.error(st.session_state["nutrition_search_error"])

    if "results" in st.session_state and st.session_state.results:
        st.subheader(f'Results for "{st.session_state.query}"')
        results = st.session_state.results
        total = len(results)
        PAGE_SIZE = 6
        num_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

        if "page_index" not in st.session_state:
            st.session_state.page_index = 0

        prev_col, mid_col, next_col = st.columns([1, 2, 1])
        with prev_col:
            if st.button("← Prev", key="prev") and st.session_state.page_index > 0:
                st.session_state.page_index -= 1
        with mid_col:
            st.write(f"Page {st.session_state.page_index+1} of {num_pages} ({total} items)")
        with next_col:
            if st.button("Next →", key="next") and st.session_state.page_index < num_pages - 1:
                st.session_state.page_index += 1

        start = st.session_state.page_index * PAGE_SIZE
        page_results = results[start:start + PAGE_SIZE]
        table_rows = []

        for food in page_results:
            name = food.get("food_name") or "Unknown"
            url  = food.get("food_url") or "#"
            kc   = food.get("calories")
            fg   = food.get("fat_g")
            cg   = food.get("carbs_g")
            pg   = food.get("protein_g")

            if kc is None and food.get("food_description"):
                info = food.get("food_description") or ""
                macros_part = info.split(" - ", 1)[-1]
                macros = {}
                for chunk in macros_part.split("|"):
                    if ":" in chunk:
                        lab, val = chunk.split(":", 1)
                        macros[lab.strip()] = val.strip()
                cal_s  = macros.get("Calories","—").replace("kcal","").strip()
                fat_s  = macros.get("Fat","—")
                carb_s = macros.get("Carbs","—")
                prot_s = macros.get("Protein","—")
            else:
                cal_s  = f"{kc:.0f}" if kc  is not None else "—"
                fat_s  = f"{fg:g} g" if fg  is not None else "—"
                carb_s = f"{cg:g} g" if cg  is not None else "—"
                prot_s = f"{pg:g} g" if pg  is not None else "—"

            table_rows.append({
                "Product": name,
                "Brand": food.get("brand") or "—",
                "Serving": food.get("serving_label") or "—",
                "Calories": cal_s, "Fat": fat_s, "Carbs": carb_s, "Protein": prot_s,
                "Link": url,
            })

        st.dataframe(
            pd.DataFrame(table_rows),
            column_config={"Link": st.column_config.LinkColumn("Details", display_text="Open")},
            hide_index=True, use_container_width=True,
        )

        with st.expander("📸 Photos", expanded=False):
            cols = st.columns(3)
            for i, food in enumerate(page_results):
                img = (food.get("image_url") or "").strip()
                with cols[i % 3]:
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("No image")
                    st.caption(food.get("food_name") or "—")
        st.markdown("---")

    elif "results" in st.session_state and st.session_state.get("query"):
        st.info(
            'No foods found. Try a simpler name like "banana", "oats", or "chicken breast".'
        )

# ── TAB 4: PERSONAL TRACKER ──────────────────────────────────────────────────
with tab4:
    st.header("Personal Tracker")

    with st.form("progress_form"):
        date       = st.date_input("Date", value=datetime.date.today())
        col1, col2, col3 = st.columns(3)
        with col1:
            weight = st.number_input("Weight (lbs)", min_value=0.0, step=0.1)
        with col2:
            steps  = st.number_input("Steps", min_value=0, step=10)
        with col3:
            sleep_time = st.number_input("Sleep (hrs)", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("➕ Add Entry")

    if submitted:
        df_progress = pd.read_csv(progress_file)
        if date.isoformat() in set(df_progress["date"]):
            st.warning(f"Entry already exists for {date.strftime('%m/%d/%Y')}.")
        else:
            df_progress.loc[len(df_progress)] = [date.isoformat(), weight, steps, sleep_time]
            df_progress.to_csv(progress_file, index=False)
            st.success("Entry added!")

    df_progress = pd.read_csv(progress_file)
    df_progress["date"] = pd.to_datetime(df_progress["date"])
    df_progress = df_progress.sort_values("date").reset_index(drop=True)

    display_df = pd.DataFrame({
        "Date":           df_progress["date"].dt.strftime("%m/%d/%Y"),
        "Weight (lbs)":   df_progress["weight"],
        "Steps":          df_progress["steps"],
        "Sleep (hrs)":    df_progress["sleep_time"],
    })

    st.subheader("Progress Log")
    st.dataframe(display_df, use_container_width=True)

    to_delete = st.multiselect(
        "Select entries to delete",
        [f"{d} — {w} lbs" for d, w in zip(display_df["Date"], display_df["Weight (lbs)"])]
    )
    if st.button("🗑️ Delete Selected") and to_delete:
        keep = [f"{d} — {w} lbs" not in to_delete
                for d, w in zip(display_df["Date"], display_df["Weight (lbs)"])]
        df_progress = df_progress[keep].reset_index(drop=True)
        df_progress.to_csv(progress_file, index=False)
        st.success(f"Deleted {len(to_delete)} entries.")

    # ── Chart ────────────────────────────────────────────────────────────────
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#0d1b2a')
    ax.set_facecolor('#0a1520')

    dates   = df_progress["date"]
    weights = df_progress["weight"]

    # Gradient fill via polygon
    ax.fill_between(dates, weights, alpha=0.18, color='#4f8ef7', zorder=1)
    ax.plot(dates, weights,
            marker="o", color='#4f8ef7', linewidth=2.5, markersize=8,
            markerfacecolor='#00d4aa', markeredgecolor='#4f8ef7',
            markeredgewidth=2, zorder=2)

    ax.set_xlabel("Date", fontsize=11, fontweight='600', color='#7a9cc4', labelpad=10)
    ax.set_ylabel("Weight (lbs)", fontsize=11, fontweight='600', color='#7a9cc4', labelpad=10)
    ax.set_title("Weight Over Time", fontsize=15, fontweight='700', color='#e8f0fe', pad=18)
    ax.margins(x=0.05)
    ax.set_xticks(dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))
    ax.tick_params(colors='#4a6785', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#1a3050')
    ax.spines['bottom'].set_color('#1a3050')
    ax.grid(True, alpha=0.12, color='#1a3050', linestyle='--')
    fig.autofmt_xdate()
    plt.tight_layout()
    st.pyplot(fig)
