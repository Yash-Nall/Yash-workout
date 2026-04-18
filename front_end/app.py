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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

/* ─── DESIGN TOKENS ──────────────────────────────────────────────────────── */
:root {
  --navy-deep:    #06111f;
  --navy-base:    #0b1d33;
  --navy-mid:     #102847;
  --navy-light:   #163356;
  --navy-lift:    #1d4270;

  --glass-bg:     rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.13);
  --glass-hover:  rgba(255,255,255,0.10);
  --glass-active: rgba(255,255,255,0.04);

  --primary:      #5b9cf6;
  --primary-soft: rgba(91,156,246,0.22);
  --primary-glow: rgba(91,156,246,0.35);
  --accent:       #38e0c5;
  --accent-soft:  rgba(56,224,197,0.20);
  --accent-glow:  rgba(56,224,197,0.30);

  --user-bg:      rgba(91,156,246,0.14);
  --user-border:  rgba(91,156,246,0.35);
  --bot-bg:       rgba(56,224,197,0.09);
  --bot-border:   rgba(56,224,197,0.30);

  --text:         #dceeff;
  --text-sub:     #8fb4d8;
  --text-muted:   #4d7499;

  --radius-sm:    10px;
  --radius-md:    16px;
  --radius-lg:    22px;
  --radius-xl:    32px;

  --font:         'DM Sans', sans-serif;
  --font-display: 'Syne', sans-serif;

  --ease-out:     cubic-bezier(0.22, 1, 0.36, 1);
  --ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ─── KEYFRAMES ──────────────────────────────────────────────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(22px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes shimmer {
  0%   { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
@keyframes float {
  0%,100% { transform: translateY(0px); }
  50%      { transform: translateY(-6px); }
}
@keyframes pulseGlow {
  0%,100% { box-shadow: 0 0 0 0 var(--primary-glow); }
  50%      { box-shadow: 0 0 24px 8px var(--primary-glow); }
}
@keyframes slideRight {
  from { opacity: 0; transform: translateX(-16px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes popIn {
  0%   { opacity: 0; transform: scale(0.88); }
  60%  { transform: scale(1.04); }
  100% { opacity: 1; transform: scale(1); }
}
@keyframes chatUser {
  from { opacity: 0; transform: translateX(20px) scale(0.96); }
  to   { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes chatBot {
  from { opacity: 0; transform: translateX(-20px) scale(0.96); }
  to   { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
@keyframes borderFlow {
  0%,100% { border-color: rgba(91,156,246,0.3); }
  50%      { border-color: rgba(56,224,197,0.4); }
}
@keyframes ripple {
  0%   { transform: scale(0); opacity: 0.6; }
  100% { transform: scale(2.5); opacity: 0; }
}
@keyframes meshMove {
  0%,100% { background-position: 0% 50%; }
  50%      { background-position: 100% 50%; }
}

/* ─── GLOBAL BASE ────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
  background:
    radial-gradient(ellipse at 20% 10%, rgba(91,156,246,0.08) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 90%, rgba(56,224,197,0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 40%, rgba(30,80,140,0.10) 0%, transparent 60%),
    linear-gradient(160deg, #06111f 0%, #0b1d33 40%, #0d2240 70%, #06111f 100%) !important;
  background-attachment: fixed !important;
  font-family: var(--font) !important;
  color: var(--text) !important;
  min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden !important; }

/* ─── TRANSPARENT INTERNALS ──────────────────────────────────────────────── */
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
  max-width: 1160px !important;
  margin: 0 auto !important;
  animation: fadeUp 0.6s var(--ease-out) both;
}

/* ─── TYPOGRAPHY ─────────────────────────────────────────────────────────── */
p, li, span, div, label,
.stMarkdown p, .stMarkdown li,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-family: var(--font) !important;
  line-height: 1.68 !important;
}

h1, h2, h3, h4 {
  font-family: var(--font) !important;
  color: var(--text) !important;
  letter-spacing: -0.02em !important;
}

h1, .stMarkdown h1 {
  font-family: var(--font-display) !important;
  font-size: clamp(2.4rem, 5vw, 4rem) !important;
  font-weight: 800 !important;
  letter-spacing: 0.01em !important;
  background: linear-gradient(90deg, #5b9cf6, #38e0c5, #7ab8ff, #5b9cf6) !important;
  background-size: 300% auto !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
  animation: shimmer 5s linear infinite, fadeUp 0.7s var(--ease-out) both !important;
  line-height: 1.1 !important;
}

h2, .stMarkdown h2 {
  font-size: clamp(1.3rem, 3vw, 1.8rem) !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
}

h3, .stMarkdown h3 {
  font-size: 1.1rem !important;
  font-weight: 600 !important;
  color: var(--text-sub) !important;
  -webkit-text-fill-color: var(--text-sub) !important;
}

strong, b,
.stMarkdown strong, .stMarkdown b {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-weight: 700 !important;
}

.stCaption, [data-testid="stCaptionContainer"],
.stCaption p, [data-testid="stCaptionContainer"] p {
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
  font-size: 0.8rem !important;
}

/* ─── TABS ───────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(18px) !important;
  -webkit-backdrop-filter: blur(18px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 6px !important;
  gap: 4px !important;
  animation: fadeIn 0.5s var(--ease-out) both;
}

.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: var(--radius-md) !important;
  padding: 10px 20px !important;
  font-weight: 600 !important;
  font-size: 0.86rem !important;
  font-family: var(--font) !important;
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
  border: none !important;
  transition: all 0.25s var(--ease-out) !important;
  letter-spacing: 0.01em !important;
}

.stTabs [data-baseweb="tab"]:hover {
  color: var(--text-sub) !important;
  -webkit-text-fill-color: var(--text-sub) !important;
  background: rgba(255,255,255,0.06) !important;
  transform: translateY(-1px) !important;
}

.stTabs [aria-selected="true"] {
  background: rgba(91,156,246,0.16) !important;
  backdrop-filter: blur(10px) !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  border: 1px solid rgba(91,156,246,0.28) !important;
  box-shadow: 0 0 18px var(--primary-glow), inset 0 1px 0 rgba(255,255,255,0.12) !important;
}

.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding: 20px 2px !important;
  animation: fadeUp 0.4s var(--ease-out) both;
}

/* ─── GLASS CARD BASE ────────────────────────────────────────────────────── */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow:
    0 8px 32px rgba(0,0,0,0.25),
    0 2px 8px rgba(0,0,0,0.15),
    inset 0 1px 0 rgba(255,255,255,0.10);
  transition: all 0.3s var(--ease-out);
}
.glass-card:hover {
  border-color: rgba(91,156,246,0.28);
  box-shadow:
    0 16px 48px rgba(0,0,0,0.3),
    0 0 32px var(--primary-glow),
    inset 0 1px 0 rgba(255,255,255,0.14);
  transform: translateY(-3px);
}

/* ─── BUTTONS ────────────────────────────────────────────────────────────── */
.stButton > button {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  padding: 11px 26px !important;
  font-weight: 600 !important;
  font-family: var(--font) !important;
  font-size: 0.88rem !important;
  letter-spacing: 0.02em !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.09) !important;
  transition: all 0.28s var(--ease-spring) !important;
  position: relative !important;
  overflow: hidden !important;
}

.stButton > button::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(91,156,246,0.10), rgba(56,224,197,0.07));
  opacity: 0;
  transition: opacity 0.25s ease;
  border-radius: inherit;
}

.stButton > button:hover {
  transform: translateY(-3px) scale(1.02) !important;
  border-color: rgba(91,156,246,0.45) !important;
  box-shadow: 0 8px 28px rgba(0,0,0,0.25), 0 0 20px var(--primary-glow), inset 0 1px 0 rgba(255,255,255,0.14) !important;
  color: #84baff !important;
  -webkit-text-fill-color: #84baff !important;
}
.stButton > button:hover::after { opacity: 1; }

.stButton > button:active {
  transform: translateY(0) scale(0.97) !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}

/* Form submit */
.stFormSubmitButton > button {
  background: linear-gradient(135deg, rgba(91,156,246,0.35), rgba(91,156,246,0.20)) !important;
  backdrop-filter: blur(16px) !important;
  border: 1px solid rgba(91,156,246,0.45) !important;
  color: #c8ddff !important;
  -webkit-text-fill-color: #c8ddff !important;
  box-shadow: 0 4px 20px rgba(91,156,246,0.25), inset 0 1px 0 rgba(255,255,255,0.15) !important;
}
.stFormSubmitButton > button:hover {
  background: linear-gradient(135deg, rgba(91,156,246,0.48), rgba(91,156,246,0.28)) !important;
  box-shadow: 0 8px 32px rgba(91,156,246,0.4) !important;
}

/* Link button */
.stLinkButton > a {
  background: linear-gradient(135deg, rgba(56,224,197,0.22), rgba(56,224,197,0.12)) !important;
  backdrop-filter: blur(16px) !important;
  border: 1px solid rgba(56,224,197,0.35) !important;
  border-radius: var(--radius-md) !important;
  padding: 13px 32px !important;
  font-weight: 700 !important;
  font-family: var(--font) !important;
  font-size: 0.92rem !important;
  letter-spacing: 0.03em !important;
  color: var(--accent) !important;
  -webkit-text-fill-color: var(--accent) !important;
  box-shadow: 0 4px 20px rgba(56,224,197,0.18), inset 0 1px 0 rgba(255,255,255,0.10) !important;
  transition: all 0.3s var(--ease-spring) !important;
  text-decoration: none !important;
  animation: float 3.5s ease-in-out infinite !important;
  display: inline-block !important;
}
.stLinkButton > a:hover {
  transform: translateY(-4px) scale(1.04) !important;
  box-shadow: 0 12px 36px rgba(56,224,197,0.35), inset 0 1px 0 rgba(255,255,255,0.15) !important;
  border-color: rgba(56,224,197,0.55) !important;
}

/* ─── INPUTS ─────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
  background: rgba(255,255,255,0.04) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 12px 16px !important;
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 0.92rem !important;
  transition: all 0.25s var(--ease-out) !important;
  box-shadow: inset 0 1px 4px rgba(0,0,0,0.2) !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {
  border-color: rgba(91,156,246,0.55) !important;
  background: rgba(91,156,246,0.06) !important;
  box-shadow: 0 0 0 3px rgba(91,156,246,0.12), 0 0 16px var(--primary-glow), inset 0 1px 4px rgba(0,0,0,0.15) !important;
  outline: none !important;
  animation: borderFlow 2s ease infinite !important;
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
  font-size: 0.75rem !important;
  font-family: var(--font) !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  margin-bottom: 5px !important;
}

/* ─── SELECT / MULTISELECT ───────────────────────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: rgba(255,255,255,0.04) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
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
  background: rgba(13,30,55,0.92) !important;
  backdrop-filter: blur(24px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 16px 48px rgba(0,0,0,0.4), 0 0 24px rgba(91,156,246,0.08) !important;
  animation: popIn 0.2s var(--ease-out) both !important;
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
  background: rgba(91,156,246,0.12) !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
}

[data-baseweb="tag"] {
  background: rgba(91,156,246,0.15) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(91,156,246,0.30) !important;
  border-radius: 7px !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  font-family: var(--font) !important;
  font-size: 0.82rem !important;
  animation: popIn 0.22s var(--ease-out) both;
}

/* ─── SLIDERS ─────────────────────────────────────────────────────────────── */
.stSlider > div > div > div {
  background: rgba(255,255,255,0.06) !important;
  border-radius: 10px !important;
}

[data-testid="stSlider"] [role="slider"] {
  background: linear-gradient(135deg, var(--primary), #84baff) !important;
  border-radius: 50% !important;
  box-shadow: 0 0 16px var(--primary-glow) !important;
  transition: all 0.25s var(--ease-spring) !important;
}
[data-testid="stSlider"] [role="slider"]:hover {
  transform: scale(1.28) !important;
  animation: pulseGlow 1.5s ease infinite;
}

[data-testid="stSlider"] [data-baseweb="slider"] [role="progressbar"] {
  background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
}

/* ─── DATAFRAME ───────────────────────────────────────────────────────────── */
.stDataFrame {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.08) !important;
  overflow: hidden !important;
  animation: fadeUp 0.5s var(--ease-out) both;
}

/* ─── FORMS ───────────────────────────────────────────────────────────────── */
[data-testid="stForm"] {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 28px !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.22), inset 0 1px 0 rgba(255,255,255,0.09) !important;
  animation: fadeUp 0.5s var(--ease-out) both;
}

/* ─── SIDEBAR ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: rgba(6,17,31,0.85) !important;
  backdrop-filter: blur(28px) !important;
  -webkit-backdrop-filter: blur(28px) !important;
  border-right: 1px solid var(--glass-border) !important;
  box-shadow: 4px 0 32px rgba(0,0,0,0.3) !important;
  animation: slideRight 0.5s var(--ease-out) both;
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
  color: #ff8585 !important;
  -webkit-text-fill-color: #ff8585 !important;
  border-color: rgba(255,107,107,0.22) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  color: #ff5252 !important;
  -webkit-text-fill-color: #ff5252 !important;
  border-color: rgba(255,82,82,0.4) !important;
  box-shadow: 0 8px 24px rgba(255,82,82,0.2) !important;
}

/* ─── CHAT MESSAGES — DIFFERENTIATED ─────────────────────────────────────── */

/* Hide Streamlit's default avatar name label to avoid duplication */
[data-testid="stChatMessageAvatarUser"] ~ div > [data-testid="stChatMessageContent"] [data-testid="stChatMessageAvatarName"],
.stChatMessage [data-testid="stChatMessageAvatarName"] {
  display: none !important;
}

/* Base chat bubble */
.stChatMessage {
  border-radius: var(--radius-lg) !important;
  padding: 16px 20px !important;
  margin: 10px 0 !important;
  transition: all 0.3s var(--ease-out) !important;
  position: relative !important;
  background: var(--glass-bg) !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: 0 4px 18px rgba(0,0,0,0.18) !important;
}

/* User messages — blue tint, right indent */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: var(--user-bg) !important;
  border: 1px solid var(--user-border) !important;
  border-left: 3px solid var(--primary) !important;
  box-shadow: 0 4px 20px rgba(91,156,246,0.12), inset 0 1px 0 rgba(255,255,255,0.08) !important;
  margin-left: 60px !important;
  animation: chatUser 0.35s var(--ease-out) both !important;
}

/* Assistant messages — teal tint, left indent */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
  background: var(--bot-bg) !important;
  border: 1px solid var(--bot-border) !important;
  border-left: 3px solid var(--accent) !important;
  box-shadow: 0 4px 20px rgba(56,224,197,0.10), inset 0 1px 0 rgba(255,255,255,0.06) !important;
  margin-right: 60px !important;
  animation: chatBot 0.35s var(--ease-out) both !important;
}

/* Style the avatar icons */
[data-testid="stChatMessageAvatarUser"] {
  background: rgba(91,156,246,0.20) !important;
  border: 1px solid rgba(91,156,246,0.40) !important;
  border-radius: 50% !important;
  box-shadow: 0 0 10px rgba(91,156,246,0.25) !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
  background: rgba(56,224,197,0.15) !important;
  border: 1px solid rgba(56,224,197,0.35) !important;
  border-radius: 50% !important;
  box-shadow: 0 0 10px rgba(56,224,197,0.20) !important;
}

.stChatMessage:hover {
  border-color: rgba(91,156,246,0.30) !important;
  box-shadow: 0 8px 28px rgba(0,0,0,0.22), 0 0 18px var(--primary-glow) !important;
  transform: translateY(-2px) !important;
}

.stChatMessage p, .stChatMessage span, .stChatMessage div {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  background: transparent !important;
}

/* Chat input */
.stChatInput > div {
  background: var(--glass-bg) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.08) !important;
  transition: all 0.25s var(--ease-out) !important;
}
.stChatInput > div:focus-within {
  border-color: rgba(91,156,246,0.45) !important;
  box-shadow: 0 0 0 3px rgba(91,156,246,0.10), 0 0 20px var(--primary-glow) !important;
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
  background: var(--glass-bg) !important;
  backdrop-filter: blur(16px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  color: var(--text-sub) !important;
  -webkit-text-fill-color: var(--text-sub) !important;
  transition: all 0.25s var(--ease-out) !important;
  box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important;
}
.streamlit-expanderHeader:hover {
  border-color: rgba(91,156,246,0.30) !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  transform: translateY(-1px) !important;
}
.streamlit-expanderContent {
  background: rgba(255,255,255,0.03) !important;
  backdrop-filter: blur(16px) !important;
  border: 1px solid var(--glass-border) !important;
  border-top: none !important;
  border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
}

/* ─── ALERTS ──────────────────────────────────────────────────────────────── */
.stSuccess {
  background: rgba(56,224,197,0.08) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(56,224,197,0.28) !important;
  border-left: 4px solid var(--accent) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 4px 18px rgba(56,224,197,0.12) !important;
  animation: popIn 0.3s var(--ease-out) both !important;
}
.stWarning {
  background: rgba(255,193,7,0.07) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255,193,7,0.28) !important;
  border-left: 4px solid #ffc107 !important;
  border-radius: var(--radius-md) !important;
  animation: popIn 0.3s var(--ease-out) both !important;
}
.stError {
  background: rgba(255,82,82,0.07) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255,82,82,0.28) !important;
  border-left: 4px solid #ff5252 !important;
  border-radius: var(--radius-md) !important;
  animation: popIn 0.3s var(--ease-out) both !important;
}
.stInfo {
  background: rgba(91,156,246,0.08) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(91,156,246,0.28) !important;
  border-left: 4px solid var(--primary) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 4px 18px var(--primary-glow) !important;
  animation: popIn 0.3s var(--ease-out) both !important;
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
  background: rgba(255,255,255,0.04) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
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
}
[data-testid="stMetricLabel"] {
  color: var(--text-muted) !important;
  -webkit-text-fill-color: var(--text-muted) !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
  font-size: 0.72rem !important;
}

/* ─── PROGRESS BAR ────────────────────────────────────────────────────────── */
.stProgress > div > div {
  background: rgba(255,255,255,0.06) !important;
  border-radius: 99px !important;
}
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
  border-radius: 99px !important;
  animation: shimmer 2s linear infinite !important;
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
  background: linear-gradient(90deg, transparent, rgba(91,156,246,0.25), rgba(56,224,197,0.20), rgba(91,156,246,0.25), transparent) !important;
  margin: 28px 0 !important;
}

/* ─── SCROLLBAR ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.03); border-radius: 99px; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--primary), var(--text-muted));
  border-radius: 99px;
}
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ─── IMAGES ──────────────────────────────────────────────────────────────── */
.stImage img {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: 0 8px 28px rgba(0,0,0,0.3) !important;
  transition: all 0.3s var(--ease-out) !important;
}
.stImage img:hover {
  transform: scale(1.03) translateY(-3px) !important;
  box-shadow: 0 14px 40px rgba(0,0,0,0.35), 0 0 22px var(--primary-glow) !important;
  border-color: rgba(91,156,246,0.35) !important;
}

/* ─── NUMBER INPUT BUTTONS ────────────────────────────────────────────────── */
.stNumberInput button {
  background: rgba(255,255,255,0.05) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 8px !important;
  color: var(--primary) !important;
  -webkit-text-fill-color: var(--primary) !important;
  transition: all 0.22s var(--ease-spring) !important;
}
.stNumberInput button:hover {
  transform: scale(1.18) !important;
  box-shadow: 0 0 12px var(--primary-glow) !important;
  border-color: rgba(91,156,246,0.40) !important;
}

/* ─── CHART / PLOT WRAPPER ────────────────────────────────────────────────── */
[data-testid="stImage"], .stPlotlyChart {
  border-radius: var(--radius-lg) !important;
  overflow: hidden !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25) !important;
  animation: fadeUp 0.6s var(--ease-out) both;
}

/* ─── COLUMNS ─────────────────────────────────────────────────────────────── */
[data-testid="column"] { padding: 0 8px !important; }

/* ─── STAGGER ANIMATIONS ──────────────────────────────────────────────────── */
[data-testid="stVerticalBlock"] > div:nth-child(1) { animation: fadeUp 0.5s 0.05s var(--ease-out) both; }
[data-testid="stVerticalBlock"] > div:nth-child(2) { animation: fadeUp 0.5s 0.10s var(--ease-out) both; }
[data-testid="stVerticalBlock"] > div:nth-child(3) { animation: fadeUp 0.5s 0.15s var(--ease-out) both; }
[data-testid="stVerticalBlock"] > div:nth-child(4) { animation: fadeUp 0.5s 0.20s var(--ease-out) both; }
[data-testid="stVerticalBlock"] > div:nth-child(5) { animation: fadeUp 0.5s 0.25s var(--ease-out) both; }
[data-testid="stVerticalBlock"] > div:nth-child(6) { animation: fadeUp 0.5s 0.30s var(--ease-out) both; }

/* ─── MOBILE — TABLET (≤768px) ────────────────────────────────────────────── */
@media (max-width: 768px) {
  /* Layout */
  .main .block-container {
    padding: 1rem 0.75rem !important;
    max-width: 100% !important;
  }

  /* Typography */
  h1, .stMarkdown h1 { font-size: 2rem !important; }
  h2, .stMarkdown h2 { font-size: 1.3rem !important; }
  h3, .stMarkdown h3 { font-size: 1rem !important; }
  p, li, span { font-size: 0.9rem !important; line-height: 1.6 !important; }

  /* Tabs — show emoji only on very small, keep text on tablet */
  .stTabs [data-baseweb="tab-list"] {
    gap: 2px !important;
    padding: 5px !important;
    flex-wrap: wrap !important;
  }
  .stTabs [data-baseweb="tab"] {
    padding: 8px 10px !important;
    font-size: 0.76rem !important;
    flex: 1 1 auto !important;
    text-align: center !important;
    white-space: nowrap !important;
  }

  /* Buttons — full width on mobile */
  .stButton > button {
    width: 100% !important;
    padding: 11px 14px !important;
    font-size: 0.85rem !important;
  }
  .stFormSubmitButton > button {
    width: 100% !important;
  }
  .stLinkButton > a {
    display: block !important;
    text-align: center !important;
    padding: 12px 20px !important;
    font-size: 0.88rem !important;
    animation: none !important; /* disable float on mobile */
  }

  /* Forms */
  [data-testid="stForm"] {
    padding: 16px 12px !important;
  }

  /* Columns — stack on mobile */
  [data-testid="column"] {
    padding: 0 2px !important;
    min-width: 0 !important;
  }

  /* Chat bubbles — remove side indents on mobile so text has room */
  .stChatMessage {
    padding: 12px 14px !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    border-radius: var(--radius-md) !important;
  }
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    margin-left: 0 !important;
  }
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    margin-right: 0 !important;
  }

  /* Inputs */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stTextArea textarea {
    font-size: 0.88rem !important;
    padding: 10px 12px !important;
  }

  /* Dataframe */
  .stDataFrame { font-size: 0.76rem !important; }

  /* Metrics */
  [data-testid="stMetricValue"] { font-size: 1.6rem !important; }

  /* Sidebar */
  [data-testid="stSidebar"] { width: 240px !important; }

  /* Chart */
  [data-testid="stImage"], .stPlotlyChart {
    border-radius: var(--radius-md) !important;
  }

  /* Multiselect tags wrap nicely */
  [data-baseweb="tag"] {
    font-size: 0.75rem !important;
    padding: 3px 8px !important;
  }
}

/* ─── MOBILE — PHONE (≤480px) ─────────────────────────────────────────────── */
@media (max-width: 480px) {
  .main .block-container { padding: 0.75rem 0.5rem !important; }

  h1, .stMarkdown h1 { font-size: 1.65rem !important; }
  h2, .stMarkdown h2 { font-size: 1.15rem !important; }
  h3, .stMarkdown h3 { font-size: 0.95rem !important; }

  /* Tabs — emoji only, hide text */
  .stTabs [data-baseweb="tab"] {
    padding: 8px 8px !important;
    font-size: 0 !important;      /* hide text */
    line-height: 0 !important;
  }
  /* Keep emoji visible by targeting first character */
  .stTabs [data-baseweb="tab"]::first-letter {
    font-size: 1rem !important;
    line-height: 1.4 !important;
  }

  /* Sliders — full width */
  .stSlider { padding: 0 !important; }

  /* Number inputs stack controls */
  .stNumberInput > div { flex-wrap: wrap !important; gap: 4px !important; }
  .stNumberInput > div > div { flex: 1 1 100% !important; }

  /* Chat input */
  .stChatInput > div { border-radius: var(--radius-md) !important; }

  /* Forms tighter */
  [data-testid="stForm"] { padding: 12px 10px !important; border-radius: var(--radius-md) !important; }

  /* Reduce animation delays on mobile for snappiness */
  [data-testid="stVerticalBlock"] > div:nth-child(n) {
    animation-delay: 0.03s !important;
  }

  /* Pagination buttons side by side */
  [data-testid="column"] [data-testid="stButton"] > button {
    padding: 8px 10px !important;
    font-size: 0.78rem !important;
  }

  /* Metric cards */
  [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
  [data-testid="stMetricLabel"] { font-size: 0.65rem !important; }
}

/* ─── MISC ────────────────────────────────────────────────────────────────── */
[data-testid="stText"], [data-testid="stWrite"] {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
  font-family: var(--font) !important;
}
[data-testid="stTooltipIcon"] { color: var(--text-muted) !important; }

[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
  color: var(--text) !important;
  -webkit-text-fill-color: var(--text) !important;
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
    new_row = pd.DataFrame([{"email": email, "password": hash_password(password)}])
    users = pd.concat([users, new_row], ignore_index=True)
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
    st.markdown("##### Your personal health assistant. Log in or create an account to get started.")
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
                st.error("Invalid email or password.")

    with tab_signup:
        new_email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
        new_password = st.text_input("Password", type="password", key="signup_pw", placeholder="Create a strong password")
        if st.button("Create Account", key="signup_btn"):
            if save_user(new_email, new_password):
                st.success("Account created! Please log in.")
            else:
                st.error("An account with this email already exists.")
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
        "Parallel Bars", "Chairs", "Pull-up Bar", "Dumbbell", "Barbell",
        "Bench", "Platform", "Kettlebell", "Step", "Box",
        "Resistance Band", "Cable Machine", "Low Bar", "TRX", "Wall", "Sturdy Surface",
    ])
    muscle_group_options = sorted([
        "Triceps", "Chest", "Back", "Biceps", "Core", "Obliques",
        "Hamstrings", "Glutes", "Quadriceps", "Rear Deltoids", "Upper Back",
        "Shoulders", "Calves", "Forearms", "Full Core", "Full Body",
        "Legs", "Upper Chest", "Lower Chest",
    ])

    calories_min = st.slider("Min calories burned", 10, 1000, 100)
    calories_max = st.slider("Max calories burned", 10, 1000, 1000)

    difficulty = st.multiselect(
        "Difficulty Level(s)", ["Beginner", "Intermediate", "Advanced"],
        help="Leave empty for any difficulty."
    )
    equipment_include = st.multiselect(
        "Include Equipment", equipment_options,
        help="Leave empty for any equipment."
    )
    equipment_exclude = st.multiselect(
        "Exclude Equipment", equipment_options,
        help="Hide exercises that require any of these."
    )
    muscle_group = st.multiselect(
        "Muscle Group(s)", muscle_group_options,
        help="Leave empty for any muscle group."
    )
    st.caption("Filters combine with AND logic. Within each list, selections use OR logic.")

    if st.button("🔍 Find Workouts"):
        results = filter_data(
            df, int(calories_min), int(calories_max),
            difficulty or "All", equipment_include or None,
            equipment_exclude or None, muscle_group or "All",
        )
        if not results.empty:
            st.write("**Recommended Workouts:**")
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("No workouts found. Try adjusting your filters.")

# ── TAB 2: CALORIE CHATBOT ───────────────────────────────────────────────────
with tab2:
    st.header("Calorie Chatbot")
    st.caption("Ask anything about nutrition, calories, or your diet goals.")

    if "nutrition_chat" not in st.session_state:
        st.session_state.nutrition_chat = []

    if st.button("🗑️ Clear conversation", key="clear_chat"):
        st.session_state.nutrition_chat = []
        st.rerun()

    # Render chat history
    for msg in st.session_state.nutrition_chat:
        role = msg["role"]
        if role == "user":
            with st.chat_message("You", avatar="🧑"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("FitCore AI", avatar="🤖"):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about nutrition, calories, or diet..."):
        st.session_state.nutrition_chat.append({"role": "user", "content": prompt})
        with st.chat_message("You", avatar="🧑"):
            st.markdown(prompt)
        with st.chat_message("FitCore AI", avatar="🤖"):
            with st.spinner("Thinking..."):
                answer = chat_with_history(st.session_state.nutrition_chat)
            st.markdown(answer)
        st.session_state.nutrition_chat.append({"role": "assistant", "content": answer})

# ── TAB 3: NUTRITION CALCULATOR ──────────────────────────────────────────────
with tab3:
    st.header("Nutrition Calculator")
    st.caption("Data sourced from Open Food Facts. Results are ranked by name relevance.")

    food_query = st.text_input(
        "Search for a food:", key="food_query",
        placeholder="e.g. banana, chicken breast, oats"
    )

    if st.button("🔍 Search", key="search"):
        q = (food_query or "").strip()
        if not q:
            st.warning("Please enter a food name first.")
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
            st.write(f"Page {st.session_state.page_index + 1} of {num_pages} ({total} items)")
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
                cal_s  = macros.get("Calories", "—").replace("kcal", "").strip()
                fat_s  = macros.get("Fat", "—")
                carb_s = macros.get("Carbs", "—")
                prot_s = macros.get("Protein", "—")
            else:
                cal_s  = f"{kc:.0f}" if kc is not None else "—"
                fat_s  = f"{fg:g} g" if fg is not None else "—"
                carb_s = f"{cg:g} g" if cg is not None else "—"
                prot_s = f"{pg:g} g" if pg is not None else "—"

            table_rows.append({
                "Product":  name,
                "Brand":    food.get("brand") or "—",
                "Serving":  food.get("serving_label") or "—",
                "Calories": cal_s,
                "Fat":      fat_s,
                "Carbs":    carb_s,
                "Protein":  prot_s,
                "Link":     url,
            })

        st.dataframe(
            pd.DataFrame(table_rows),
            column_config={"Link": st.column_config.LinkColumn("Details", display_text="Open")},
            hide_index=True, use_container_width=True,
        )

        with st.expander("📸 Food Photos", expanded=False):
            cols = st.columns(3)
            for i, food in enumerate(page_results):
                img = (food.get("image_url") or "").strip()
                with cols[i % 3]:
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("No image available")
                    st.caption(food.get("food_name") or "—")
        st.markdown("---")

    elif "results" in st.session_state and st.session_state.get("query"):
        st.info('No foods found. Try a simpler search term such as "banana", "oats", or "chicken breast".')

# ── TAB 4: PERSONAL TRACKER ──────────────────────────────────────────────────
with tab4:
    st.header("Personal Tracker")

    with st.form("progress_form"):
        date = st.date_input("Date", value=datetime.date.today())
        weight = st.number_input("Weight (lbs)", min_value=0.0, step=0.1)
        steps = st.number_input("Steps", min_value=0, step=10)
        sleep_time = st.number_input("Sleep (hrs)", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("➕ Add Entry")

    if submitted:
        df_progress = pd.read_csv(progress_file)
        if date.isoformat() in set(df_progress["date"]):
            st.warning(f"An entry already exists for {date.strftime('%B %d, %Y')}.")
        else:
            new_row = pd.DataFrame([{
                "date": date.isoformat(),
                "weight": weight,
                "steps": steps,
                "sleep_time": sleep_time
            }])
            df_progress = pd.concat([df_progress, new_row], ignore_index=True)
            df_progress.to_csv(progress_file, index=False)
            st.success("Entry added successfully!")

    df_progress = pd.read_csv(progress_file)
    df_progress["date"] = pd.to_datetime(df_progress["date"])
    df_progress = df_progress.sort_values("date").reset_index(drop=True)

    display_df = pd.DataFrame({
        "Date":         df_progress["date"].dt.strftime("%m/%d/%Y"),
        "Weight (lbs)": df_progress["weight"],
        "Steps":        df_progress["steps"],
        "Sleep (hrs)":  df_progress["sleep_time"],
    })

    st.subheader("Progress Log")
    st.dataframe(display_df, use_container_width=True)

    to_delete = st.multiselect(
        "Select entries to delete",
        [f"{d} — {w} lbs" for d, w in zip(display_df["Date"], display_df["Weight (lbs)"])]
    )
    if st.button("🗑️ Delete Selected") and to_delete:
        keep = [
            f"{d} — {w} lbs" not in to_delete
            for d, w in zip(display_df["Date"], display_df["Weight (lbs)"])
        ]
        df_progress = df_progress[keep].reset_index(drop=True)
        df_progress.to_csv(progress_file, index=False)
        st.success(f"Deleted {len(to_delete)} entr{'y' if len(to_delete)==1 else 'ies'}.")

    # ── Weight Chart ─────────────────────────────────────────────────────────
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#06111f')
    ax.set_facecolor('#0b1d33')

    dates   = df_progress["date"]
    weights = df_progress["weight"]

    ax.fill_between(dates, weights, alpha=0.15, color='#5b9cf6', zorder=1)
    ax.plot(
        dates, weights,
        marker="o", color='#5b9cf6', linewidth=2.5, markersize=8,
        markerfacecolor='#38e0c5', markeredgecolor='#5b9cf6',
        markeredgewidth=2, zorder=2
    )

    ax.set_xlabel("Date", fontsize=11, fontweight='600', color='#8fb4d8', labelpad=10)
    ax.set_ylabel("Weight (lbs)", fontsize=11, fontweight='600', color='#8fb4d8', labelpad=10)
    ax.set_title("Weight Over Time", fontsize=15, fontweight='700', color='#dceeff', pad=18)
    ax.margins(x=0.05)

    if not dates.empty:
        ax.set_xticks(dates)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))

    ax.tick_params(colors='#4d7499', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#163356')
    ax.spines['bottom'].set_color('#163356')
    ax.grid(True, alpha=0.10, color='#163356', linestyle='--')
    fig.autofmt_xdate()
    plt.tight_layout()
    st.pyplot(fig)
