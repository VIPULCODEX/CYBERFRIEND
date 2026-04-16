"""
app.py – Streamlit UI for QuantX AI Assistant
Run: streamlit run app.py
Premium Cyberpunk Dashboard — Production-Ready Interface
"""

import os
import sys
import time
import json
import streamlit as st
from dotenv import load_dotenv

CHAT_HISTORY_FILE = "chat_history.json"

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_chat_history(messages):
    try:
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2)
    except Exception as e:
        print(f"Error saving chat history: {e}")

# Force UTF-8 encoding on Windows to prevent codec errors
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


# ── Load env vars first ──────────────────────────────────────────
load_dotenv()

# ── Page config (MUST be first Streamlit call) ───────────────────
st.set_page_config(
    page_title="QuantX AI",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════
#  PREMIUM CYBERPUNK CSS
# ════════════════════════════════════════════════════════════════
PREMIUM_CSS = """
<style>
/* ══════════════════════════════════════════════════════════════
   TYPOGRAPHY — Google Fonts
   ══════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ══════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ══════════════════════════════════════════════════════════════ */
:root {
    --primary: #FFC857;
    --primary-dim: rgba(255, 200, 87, 0.15);
    --primary-glow: rgba(255, 200, 87, 0.4);
    --primary-subtle: rgba(255, 200, 87, 0.06);
    --accent: #4CAF50;
    --accent-dim: rgba(76, 175, 80, 0.15);
    --accent-glow: rgba(76, 175, 80, 0.4);
    --alert: #FF3D5A;
    --alert-dim: rgba(255, 61, 90, 0.1);
    --info-blue: #00CFFF;
    --info-blue-dim: rgba(0, 207, 255, 0.08);
    --bg-deep: #0B0F14;
    --bg-card: rgba(11, 15, 20, 0.75);
    --bg-card-hover: rgba(15, 20, 26, 0.85);
    --bg-sidebar: #070a0e;
    --text-primary: #FFFFFF;
    --text-secondary: #A0AEC0;
    --text-muted: #4A5568;
    --border-subtle: rgba(255, 200, 87, 0.08);
    --border-default: rgba(255, 200, 87, 0.15);
    --border-hover: rgba(255, 200, 87, 0.35);
    --glass-blur: blur(16px);
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 18px;
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 36px;
    --space-2xl: 48px;
    --transition-fast: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-smooth: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ══════════════════════════════════════════════════════════════
   GLOBAL RESET
   ══════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ══════════════════════════════════════════════════════════════
   SUBTLE GRID BACKGROUND
   ══════════════════════════════════════════════════════════════ */
.grid-bg {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
    pointer-events: none;
    perspective: 1200px;
    overflow: hidden;
}

.grid-bg::after {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background-size: 60px 60px;
    background-image:
        linear-gradient(to right, rgba(255, 200, 87, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 200, 87, 0.03) 1px, transparent 1px);
    transform: rotateX(60deg);
    animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
    from { transform: rotateX(60deg) translateY(0); }
    to { transform: rotateX(60deg) translateY(60px); }
}

/* Vignette overlay for depth */
.vignette {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 0;
    pointer-events: none;
    background: radial-gradient(ellipse at center, transparent 50%, rgba(0, 0, 0, 0.6) 100%);
}

/* ══════════════════════════════════════════════════════════════
   MAIN CONTENT AREA
   ══════════════════════════════════════════════════════════════ */
.main .block-container {
    position: relative;
    z-index: 1;
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
}

/* ══════════════════════════════════════════════════════════════
   HEADER — QUANTX AI TITLE
   ══════════════════════════════════════════════════════════════ */
.cyber-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
    position: relative;
}

.cyber-header h1 {
    font-family: 'Orbitron', monospace;
    font-size: 2.6rem;
    font-weight: 800;
    color: var(--accent);
    text-shadow:
        0 0 20px rgba(255, 200, 87, 0.5),
        0 0 40px rgba(255, 200, 87, 0.2),
        0 0 80px rgba(255, 200, 87, 0.1);
    letter-spacing: 8px;
    text-transform: uppercase;
    margin: 0;
    animation: headerGlow 4s ease-in-out infinite alternate;
}

@keyframes headerGlow {
    0% {
        text-shadow:
            0 0 15px rgba(255, 200, 87, 0.4),
            0 0 30px rgba(255, 200, 87, 0.15);
        filter: brightness(1);
    }
    100% {
        text-shadow:
            0 0 25px rgba(255, 200, 87, 0.7),
            0 0 50px rgba(255, 200, 87, 0.3),
            0 0 80px rgba(255, 200, 87, 0.15);
        filter: brightness(1.05);
    }
}

.cyber-header .subtitle {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-secondary);
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 4px;
    margin-top: 0.6rem;
    text-transform: uppercase;
}

.header-rule {
    width: 60%;
    max-width: 500px;
    margin: 0.8rem auto 0 auto;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--primary-dim), var(--primary-glow), var(--primary-dim), transparent);
    border: none;
}

/* ══════════════════════════════════════════════════════════════
   SECURE CHANNEL BAR
   ══════════════════════════════════════════════════════════════ */
.secure-bar {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-muted);
    font-size: 0.68rem;
    letter-spacing: 2px;
    padding: 0.6rem 0 1.8rem 0;
    position: relative;
}
.secure-bar::before {
    content: '●';
    color: var(--primary);
    margin-right: 8px;
    font-size: 0.5rem;
    vertical-align: middle;
    animation: statusBlink 2s ease-in-out infinite;
}
@keyframes statusBlink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ══════════════════════════════════════════════════════════════
   GLASSMORPHISM CARD BASE
   ══════════════════════════════════════════════════════════════ */
.glass-card {
    background: var(--bg-card) !important;
    backdrop-filter: var(--glass-blur) !important;
    -webkit-backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--space-lg) !important;
    transition: all var(--transition-smooth) !important;
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--primary-dim), transparent);
    opacity: 0;
    transition: opacity var(--transition-smooth);
}

.glass-card:hover {
    border-color: var(--border-hover) !important;
    box-shadow: 0 0 30px rgba(0, 255, 159, 0.06), 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

.glass-card:hover::before {
    opacity: 1;
}

/* ══════════════════════════════════════════════════════════════
   CHAT CONTAINER
   ══════════════════════════════════════════════════════════════ */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: var(--space-lg);
    margin-bottom: 1.5rem;
}

/* ── User Message Bubble ── */
.msg-user {
    align-self: flex-end;
    background: var(--info-blue-dim) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 207, 255, 0.15) !important;
    border-radius: var(--radius-lg) var(--radius-lg) 2px var(--radius-lg);
    padding: var(--space-md) var(--space-lg);
    max-width: 80%;
    color: var(--info-blue);
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(0, 207, 255, 0.04);
    animation: msgSlideIn 0.4s ease-out;
}

.msg-user::before {
    content: 'OPERATOR';
    display: block;
    font-family: 'Rajdhani', sans-serif;
    color: rgba(0, 207, 255, 0.5);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 3px;
    margin-bottom: 6px;
    text-transform: uppercase;
}

/* ── Bot Message Bubble ── */
.msg-bot {
    align-self: flex-start;
    background: var(--primary-subtle) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 255, 159, 0.1) !important;
    border-left: 3px solid var(--primary) !important;
    border-radius: var(--radius-lg) var(--radius-lg) var(--radius-lg) 2px;
    padding: var(--space-lg) var(--space-xl);
    max-width: 90%;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    line-height: 1.75;
    box-shadow: 0 4px 25px rgba(0, 255, 159, 0.03);
    white-space: pre-wrap;
    word-wrap: break-word;
    animation: msgFadeIn 0.5s ease-out;
}

.msg-bot::before {
    content: 'QUANTX CORE v2.1';
    display: block;
    font-family: 'Rajdhani', sans-serif;
    color: var(--primary);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 3px;
    margin-bottom: 10px;
    text-transform: uppercase;
}

@keyframes msgSlideIn {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes msgFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── News Card ── */
.news-card {
    background: var(--info-blue-dim) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 207, 255, 0.1) !important;
    border-top: 2px solid var(--info-blue) !important;
    border-radius: var(--radius-md);
    padding: var(--space-lg) var(--space-xl);
    margin: var(--space-md) 0;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    line-height: 1.7;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    animation: msgFadeIn 0.5s ease-out;
}

/* ── Alert / Attack Card ── */
.attack-card {
    background: var(--alert-dim) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 61, 90, 0.15) !important;
    border-left: 3px solid var(--alert) !important;
    border-radius: var(--radius-md);
    padding: var(--space-lg) var(--space-xl);
    color: #FFC0CB;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    line-height: 1.7;
    box-shadow: 0 4px 20px rgba(255, 61, 90, 0.05);
    animation: msgFadeIn 0.5s ease-out;
}

/* ── Status Badges ── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 4px;
    font-size: 0.62rem;
    letter-spacing: 2px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.badge-rag {
    background: rgba(0, 255, 159, 0.08);
    color: var(--primary);
    border: 1px solid rgba(0, 255, 159, 0.25);
}
.badge-news {
    background: rgba(0, 207, 255, 0.08);
    color: var(--info-blue);
    border: 1px solid rgba(0, 207, 255, 0.25);
}
.badge-alert {
    background: rgba(255, 61, 90, 0.08);
    color: var(--alert);
    border: 1px solid rgba(255, 61, 90, 0.25);
}

/* ══════════════════════════════════════════════════════════════
   SIDEBAR — TACTICAL PANEL
   ══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020a05 0%, #030d08 50%, #020a05 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
    overflow-x: hidden !important;
}
[data-testid="stSidebar"] > div {
    overflow-x: hidden !important;
    padding-top: 1rem !important;
}

.sidebar-title {
    font-family: 'Orbitron', monospace;
    color: var(--primary);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    padding: 0.5rem 0 0.3rem 0;
    position: relative;
}

.sidebar-section-label {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-muted);
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: var(--space-lg);
    margin-bottom: var(--space-sm);
}

/* ── Threat Level Component ── */
.threat-panel {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: var(--space-md) var(--space-md) var(--space-md) var(--space-md);
    margin-bottom: var(--space-lg);
    transition: all var(--transition-smooth);
}
.threat-panel:hover {
    border-color: var(--border-default);
    box-shadow: 0 0 20px rgba(0, 255, 159, 0.04);
}

.threat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.threat-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-secondary);
}
.threat-value {
    font-family: 'Orbitron', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 2px 10px;
    border-radius: 3px;
}

.threat-bar-track {
    height: 6px;
    width: 100%;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 3px;
    overflow: hidden;
    position: relative;
}

.threat-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1),
                background 0.8s ease;
    position: relative;
}
.threat-bar-fill::after {
    content: '';
    position: absolute;
    right: 0;
    top: 0;
    width: 20px;
    height: 100%;
    border-radius: 3px;
    animation: barPulse 1.5s ease-in-out infinite;
}
@keyframes barPulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

/* ── Radar Component ── */
.radar-box {
    width: 100%;
    display: flex;
    justify-content: center;
    padding: var(--space-md) 0 var(--space-lg) 0;
}
.radar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 1px solid rgba(0, 255, 159, 0.2);
    position: relative;
    overflow: hidden;
    background: radial-gradient(circle, rgba(0, 255, 159, 0.05) 0%, transparent 70%);
}
.radar::before {
    content: '';
    position: absolute;
    top: 50%; left: 5%; right: 5%;
    height: 1px;
    background: rgba(0, 255, 159, 0.1);
}
.radar::after {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    width: 200%; height: 200%;
    background: conic-gradient(from 0deg, rgba(0, 255, 159, 0.25) 0%, transparent 20%);
    transform: translate(-50%, -50%);
    animation: radarSweep 3.5s linear infinite;
}
@keyframes radarSweep {
    from { transform: translate(-50%, -50%) rotate(0deg); }
    to { transform: translate(-50%, -50%) rotate(360deg); }
}
/* Radar crosshair */
.radar-center {
    position: absolute;
    top: 50%; left: 50%;
    width: 6px; height: 6px;
    background: var(--primary);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 6px var(--primary), 0 0 12px var(--primary-glow);
    z-index: 2;
}
.radar-ring {
    position: absolute;
    top: 50%; left: 50%;
    border-radius: 50%;
    border: 1px solid rgba(0, 255, 159, 0.08);
}
.radar-ring-1 { width: 33%; height: 33%; transform: translate(-50%, -50%); }
.radar-ring-2 { width: 66%; height: 66%; transform: translate(-50%, -50%); }

/* ── System Status Dot ── */
.status-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: var(--space-sm) 0;
}
.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--primary);
    box-shadow: 0 0 8px var(--primary), 0 0 16px var(--primary-glow);
    animation: statusPulse 2s ease-in-out infinite;
}
@keyframes statusPulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--primary); }
    50% { opacity: 0.4; box-shadow: 0 0 3px var(--primary); }
}
.status-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 3px;
    color: var(--primary);
    text-transform: uppercase;
}

/* ── System Logs Panel ── */
.log-panel {
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: var(--space-sm) var(--space-md);
    height: 200px;
    font-size: 0.68rem;
    font-family: 'JetBrains Mono', monospace;
    overflow-y: auto;
    display: flex;
    flex-direction: column-reverse;
    gap: 3px;
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 255, 159, 0.2) transparent;
}
.log-line {
    padding: 3px 0 3px 10px;
    border-left: 2px solid transparent;
    animation: logSlideIn 0.3s ease-out;
    line-height: 1.5;
}
.log-line.log-info {
    color: var(--primary);
    border-left-color: rgba(0, 255, 159, 0.3);
}
.log-line.log-warn {
    color: var(--accent);
    border-left-color: rgba(255, 200, 87, 0.4);
}
.log-line.log-error {
    color: var(--alert);
    border-left-color: rgba(255, 61, 90, 0.4);
}
.log-line.log-system {
    color: var(--text-muted);
    border-left-color: rgba(255, 255, 255, 0.1);
}
.log-timestamp {
    color: var(--text-muted);
    margin-right: 6px;
}

@keyframes logSlideIn {
    from { opacity: 0; transform: translateX(-8px); }
    to { opacity: 1; transform: translateX(0); }
}

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    padding: var(--space-md) !important;
    transition: all var(--transition-smooth) !important;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-default) !important;
    box-shadow: 0 0 15px rgba(0, 255, 159, 0.05) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-secondary) !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: var(--primary) !important;
    font-size: 1.3rem !important;
    font-weight: 600 !important;
}

/* ══════════════════════════════════════════════════════════════
   INPUT FIELDS — Focus Glow
   ══════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea textarea {
    background-color: rgba(8, 12, 10, 0.7) !important;
    color: var(--primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    padding: 12px 16px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    transition: all var(--transition-fast) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(0, 255, 159, 0.1), 0 0 20px rgba(0, 255, 159, 0.08) !important;
    outline: none !important;
}

[data-testid="stChatInput"] {
    background-color: rgba(8, 12, 10, 0.7) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    transition: all var(--transition-fast) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(0, 255, 159, 0.08), 0 0 25px rgba(0, 255, 159, 0.06) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--primary) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] button {
    background-color: var(--primary) !important;
    color: var(--bg-deep) !important;
    border-radius: var(--radius-sm) !important;
    transition: all var(--transition-fast) !important;
}
[data-testid="stChatInput"] button:hover {
    box-shadow: 0 0 15px var(--primary-glow) !important;
    transform: scale(1.05);
}

/* ══════════════════════════════════════════════════════════════
   BUTTONS — Hover Glow + Scale
   ══════════════════════════════════════════════════════════════ */
.stButton > button {
    background: transparent !important;
    color: var(--primary) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    padding: 8px 16px !important;
    transition: all var(--transition-fast) !important;
}
.stButton > button:hover {
    background: var(--primary) !important;
    color: var(--bg-deep) !important;
    box-shadow: 0 0 25px rgba(0, 255, 159, 0.35) !important;
    transform: translateY(-1px) !important;
    border-color: var(--primary) !important;
}
.stButton > button:hover * {
    color: var(--bg-deep) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 0 10px rgba(0, 255, 159, 0.2) !important;
}

/* ══════════════════════════════════════════════════════════════
   CYBER LOADER — Scanning Effect
   ══════════════════════════════════════════════════════════════ */
.cyber-loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: var(--space-xl) 0;
    animation: msgFadeIn 0.3s ease-out;
}
.loader-bar {
    width: 200px;
    height: 3px;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 2px;
    position: relative;
    overflow: hidden;
}
.loader-bar::after {
    content: '';
    position: absolute;
    top: 0; left: -40%;
    width: 40%;
    height: 100%;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    animation: scanLine 1.5s ease-in-out infinite;
}
@keyframes scanLine {
    0% { left: -40%; }
    100% { left: 100%; }
}
.loader-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 2px;
}
.loader-dots {
    display: flex;
    gap: 6px;
}
.loader-dot {
    width: 5px; height: 5px;
    background: var(--primary);
    border-radius: 50%;
    animation: dotPulse 1.4s ease-in-out infinite;
}
.loader-dot:nth-child(2) { animation-delay: 0.2s; }
.loader-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotPulse {
    0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
    40% { opacity: 1; transform: scale(1.2); }
}

/* ══════════════════════════════════════════════════════════════
   WELCOME CARD
   ══════════════════════════════════════════════════════════════ */
.welcome-card {
    background: var(--bg-card) !important;
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border-subtle) !important;
    border-left: 3px solid var(--info-blue) !important;
    border-radius: var(--radius-lg);
    padding: var(--space-xl) var(--space-xl);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    line-height: 1.8;
    animation: msgFadeIn 0.6s ease-out;
}
.welcome-card .welcome-title {
    font-family: 'Rajdhani', sans-serif;
    color: var(--info-blue);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 3px;
    margin-bottom: 12px;
    text-transform: uppercase;
}
.welcome-card .capability {
    color: var(--text-secondary);
    margin: 4px 0;
}
.welcome-card .capability::before {
    content: '›';
    color: var(--primary);
    margin-right: 8px;
    font-weight: 700;
}
.welcome-card .hint {
    color: var(--primary);
    font-size: 0.82rem;
    margin-top: 12px;
    opacity: 0.8;
}

/* ══════════════════════════════════════════════════════════════
   TABS — Clean Styling
   ══════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: rgba(0, 0, 0, 0.3) !important;
    border-radius: var(--radius-md);
    padding: 3px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 1px !important;
    color: var(--text-secondary) !important;
    border-radius: var(--radius-sm) !important;
    padding: 8px 20px !important;
    transition: all var(--transition-fast) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--primary) !important;
    background: rgba(0, 255, 159, 0.04) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    background: rgba(0, 255, 159, 0.08) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--primary) !important;
}
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ══════════════════════════════════════════════════════════════
   DIVIDERS
   ══════════════════════════════════════════════════════════════ */
hr {
    border-color: var(--border-subtle) !important;
    margin: var(--space-lg) 0 !important;
}

.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-subtle), transparent);
    margin: var(--space-md) 0;
}

/* ══════════════════════════════════════════════════════════════
   SLIDERS & TOGGLES
   ══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stToggle label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    color: var(--text-secondary) !important;
}

/* ══════════════════════════════════════════════════════════════
   SPINNER OVERRIDE
   ══════════════════════════════════════════════════════════════ */
.stSpinner > div {
    border-color: var(--primary) transparent transparent transparent !important;
}

/* ══════════════════════════════════════════════════════════════
   HIDE STREAMLIT BRANDING
   ══════════════════════════════════════════════════════════════ */
#MainMenu, footer { visibility: hidden; }
header { 
    visibility: hidden; 
    background-color: transparent !important;
}
header button { 
    visibility: visible !important;
}
.stDeployButton { display: none !important; }

/* Keep sidebar toggle visible and tappable on mobile/tablet. */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="baseButton-headerNoPadding"],
button[kind="header"] {
    min-width: 44px !important;
    min-height: 44px !important;
    border-radius: 8px !important;
    background: rgba(255, 200, 87, 0.12) !important;
}
[data-testid="collapsedControl"] span,
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapsedControl"] span,
[data-testid="baseButton-headerNoPadding"] span,
button[kind="header"] span,
header button span {
    font-size: 0.95rem !important;
    visibility: visible !important;
    display: inline !important;
}

/* ══════════════════════════════════════════════════════════════
   SCROLLBAR
   ══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0, 255, 159, 0.15); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 255, 159, 0.3); }

/* ══════════════════════════════════════════════════════════════
   FORM ELEMENTS
   ══════════════════════════════════════════════════════════════ */
.stForm {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--space-lg) !important;
}
[data-testid="stFormSubmitButton"] > button {
    background: var(--primary) !important;
    color: var(--bg-deep) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 2px !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    padding: 10px 24px !important;
    transition: all var(--transition-fast) !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    box-shadow: 0 0 30px var(--primary-glow) !important;
    transform: translateY(-1px) !important;
}

/* ══════════════════════════════════════════════════════════════
   RESPONSIVE — Mobile
   ══════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .cyber-header h1 {
        font-size: 1.6rem !important;
        letter-spacing: 3px !important;
    }
    .cyber-header .subtitle {
        font-size: 0.65rem !important;
        letter-spacing: 1.5px !important;
    }
    .main .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 1rem !important;
    }
    .msg-user { max-width: 95% !important; padding: 10px 14px !important; }
    .msg-bot, .attack-card, .news-card {
        max-width: 100% !important;
        padding: 14px 16px !important;
        font-size: 0.82rem !important;
    }
    .welcome-card { padding: var(--space-md) !important; }
    .radar { width: 80px !important; height: 80px !important; }
    [data-testid="stMetricValue"] { font-size: 1rem !important; }
}

/* ══════════════════════════════════════════════════════════════
   SIDEBAR TEXT COLOR OVERRIDE
   ══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] * {
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] .sidebar-title {
    color: var(--primary) !important;
    font-family: 'Orbitron', monospace !important;
}
</style>

<!-- Background overlays -->
<div class="grid-bg"></div>
<div class="vignette"></div>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  IMPORTS (after streamlit setup)
# ════════════════════════════════════════════════════════════════
from config import GROQ_API_KEY, NEWS_API_KEY, TOP_K

# ════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ════════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()
if "assistant" not in st.session_state:
    st.session_state.assistant = None      # assistant object
if "pipeline_ready" not in st.session_state:
    st.session_state.pipeline_ready = False
if "top_k" not in st.session_state:
    st.session_state.top_k = TOP_K
if "logs" not in st.session_state:
    st.session_state.logs = [
        {"msg": "Initializing tactical interface...", "type": "system", "ts": "00:00:00"},
        {"msg": "Secure connection established.", "type": "info", "ts": "00:00:01"},
    ]
if "threat_level" not in st.session_state:
    st.session_state.threat_level = 15  # Percent (Low)


def add_log(msg: str, log_type: str = "info"):
    """Add a new timestamped log to the session state logs."""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.insert(0, {"msg": msg, "type": log_type, "ts": timestamp})
    st.session_state.logs = st.session_state.logs[:20]  # Keep last 20


# ════════════════════════════════════════════════════════════════
#  PIPELINE LOADER (cached across reruns)
# ════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_pipeline(top_k: int):
    """Load RAG pipeline once and cache it. Reuses FAISS index if available."""
    from rag_pipeline import RAGPipeline
    from assistant import CybersecurityAssistant

    rag = RAGPipeline()
    rag.initialize()
    retriever = rag.get_retriever(k=top_k)
    assistant = CybersecurityAssistant(retriever)
    return assistant, rag


# ════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════
def detect_message_type(query: str, response: str) -> str:
    """Classify the response type for badge display."""
    q = query.lower()
    news_words = ["today", "recent", "latest", "news", "incident", "breach", "happened", "current"]
    if any(w in q for w in news_words):
        return "news"
    attack_words = ["attack type:", "what to do:", "explanation:"]
    if any(w in response.lower() for w in attack_words):
        return "alert"
    return "rag"


def stream_text(text: str, placeholder, delay: float = 0.005):
    """Simulate smooth streaming/typewriter effect for bot responses."""
    displayed = ""
    # Stream in small groups to reduce flicker and improve performance
    chunk_size = 3
    for i in range(0, len(text), chunk_size):
        displayed += text[i:i+chunk_size]
        placeholder.markdown(
            f'<div class="msg-bot">{displayed}▌</div>',
            unsafe_allow_html=True
        )
        time.sleep(delay)
    # Final render without cursor
    placeholder.markdown(
        f'<div class="msg-bot">{displayed}</div>',
        unsafe_allow_html=True
    )


def render_message(role: str, content: str, msg_type: str = "rag"):
    """Render a single chat message."""
    if role == "user":
        st.markdown(f'<div class="msg-user">{content}</div>', unsafe_allow_html=True)
    else:
        badge_map = {
            "rag":   '<span class="badge badge-rag">KNOWLEDGE BASE</span>',
            "news":  '<span class="badge badge-news">LIVE INTEL</span>',
            "alert": '<span class="badge badge-alert">THREAT DETECTED</span>',
        }
        badge = badge_map.get(msg_type, badge_map["rag"])
        css_class = "attack-card" if msg_type == "alert" else "msg-bot"
        st.markdown(
            f'{badge}<br><div class="{css_class}">{content}</div>',
            unsafe_allow_html=True
        )


def render_cyber_loader(message: str = "SCANNING KNOWLEDGE MATRIX"):
    """Render a cyber-themed loading indicator."""
    return f"""
    <div class="cyber-loader">
        <div class="loader-dots">
            <div class="loader-dot"></div>
            <div class="loader-dot"></div>
            <div class="loader-dot"></div>
        </div>
        <div class="loader-bar"></div>
        <div class="loader-text">// {message}...</div>
    </div>
    """


# ════════════════════════════════════════════════════════════════
#  SIDEBAR — TACTICAL PANEL
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-title">🛡 QUANTX TACTICAL</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── THREAT LEVEL ──
    level = st.session_state.threat_level
    if level < 30:
        t_color = "#00FF9F"
        t_label = "LOW"
        t_gradient = "linear-gradient(90deg, #00FF9F, #00CC7A)"
        t_label_bg = "rgba(0, 255, 159, 0.1)"
    elif level < 60:
        t_color = "#FFC857"
        t_label = "ELEVATED"
        t_gradient = "linear-gradient(90deg, #00FF9F, #FFC857)"
        t_label_bg = "rgba(255, 200, 87, 0.1)"
    else:
        t_color = "#FF3D5A"
        t_label = "CRITICAL"
        t_gradient = "linear-gradient(90deg, #FFC857, #FF3D5A)"
        t_label_bg = "rgba(255, 61, 90, 0.1)"

    st.markdown(f"""
    <div class="threat-panel">
        <div class="threat-header">
            <span class="threat-label">THREAT LEVEL</span>
            <span class="threat-value" style="color:{t_color}; background:{t_label_bg};">{t_label}</span>
        </div>
        <div class="threat-bar-track">
            <div class="threat-bar-fill" style="
                width: {level}%;
                background: {t_gradient};
                box-shadow: 0 0 12px {t_color}44;
            ">
                <div style="position:absolute; right:0; top:0; width:20px; height:100%; background: {t_color}; filter:blur(4px); opacity:0.5;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RADAR ──
    st.markdown("""
    <div class="radar-box">
        <div class="radar">
            <div class="radar-ring radar-ring-1"></div>
            <div class="radar-ring radar-ring-2"></div>
            <div class="radar-center"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SYSTEM STATUS ──
    if st.session_state.pipeline_ready:
        st.markdown("""
        <div class="status-indicator">
            <span class="status-dot"></span>
            <span class="status-text">SYSTEM ONLINE</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── SYSTEM LOGS ──
    st.markdown('<div class="sidebar-title">// SYSTEM LOGS</div>', unsafe_allow_html=True)

    log_html_parts = []
    for log_entry in st.session_state.logs:
        if isinstance(log_entry, dict):
            log_type = log_entry.get("type", "info")
            log_msg = log_entry.get("msg", "")
            log_ts = log_entry.get("ts", "")
        else:
            # Legacy string format fallback
            log_msg = str(log_entry)
            log_type = "info"
            if "[ALERT" in log_msg or "[ERROR" in log_msg:
                log_type = "error"
            elif "[WARN" in log_msg:
                log_type = "warn"
            elif "[SYSTEM" in log_msg:
                log_type = "system"
            log_ts = ""

        css_class = f"log-{log_type}"
        ts_html = f'<span class="log-timestamp">{log_ts}</span>' if log_ts else ''
        log_html_parts.append(f'<div class="log-line {css_class}">{ts_html}{log_msg}</div>')

    log_html = "".join(log_html_parts)
    st.markdown(f'<div class="log-panel">{log_html}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── SETTINGS ──
    st.markdown('<div class="sidebar-title">// SETTINGS</div>', unsafe_allow_html=True)

    # Streaming toggle
    streaming = st.toggle("Typewriter Effect", value=True)

    # RAG toggle
    use_rag = st.toggle("Enable RAG (Knowledge Base)", value=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── QUICK INTEL ──
    st.markdown('<div class="sidebar-title">// QUICK INTEL</div>', unsafe_allow_html=True)

    quick_queries = [
        "What is phishing?",
        "How does ransomware work?",
        "Explain SQL injection",
        "What is a DDoS attack?",
        "I clicked a suspicious link",
        "Latest cyber news",
    ]

    for qq in quick_queries:
        if st.button(f"› {qq}", key=f"quick_{qq}", use_container_width=True):
            st.session_state["pending_query"] = qq

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    if st.button("⟳ CLEAR TERMINAL", use_container_width=True):
        st.session_state.messages = []
        save_chat_history([])
        add_log("Terminal cleared by operator.", "system")
        st.rerun()


# ════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="cyber-header">
    <h1>🛡 QUANTX AI</h1>
    <div class="subtitle">Real-Time Threat Intelligence & Cybersecurity Advisor</div>
    <div class="header-rule"></div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="secure-bar">SECURE CHANNEL ESTABLISHED — ENCRYPTED SESSION ACTIVE</div>',
    unsafe_allow_html=True
)


# ════════════════════════════════════════════════════════════════
#  PIPELINE INIT
# ════════════════════════════════════════════════════════════════
if not GROQ_API_KEY:
    st.markdown("""
    <div class="attack-card">
    <b>[ERROR] GROQ_API_KEY not found.</b><br><br>
    Add your key to the <code>.env</code> file:<br>
    <code>GROQ_API_KEY=your_key_here</code><br><br>
    Get a free key at: https://console.groq.com/keys
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state.pipeline_ready:
    loader_placeholder = st.empty()
    loader_placeholder.markdown(render_cyber_loader("INITIALIZING NEURAL CORE"), unsafe_allow_html=True)

    try:
        assistant, rag = load_pipeline(st.session_state.top_k)
        st.session_state.assistant = assistant
        st.session_state.pipeline_ready = True
        add_log("Neural core initialized successfully.", "info")
        loader_placeholder.empty()
    except ValueError as e:
        loader_placeholder.empty()
        st.markdown(f"""
        <div class="attack-card">
        <b>[CRITICAL] Knowledge base error:</b><br>{str(e)}<br><br>
        Add PDF or TXT files to the <code>data/</code> folder and restart.
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    except Exception as e:
        loader_placeholder.empty()
        st.markdown(f"""
        <div class="attack-card">
        <b>[ERROR] Initialization failed:</b><br>{str(e)}
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    st.rerun()  # Refresh to show ONLINE status


# ════════════════════════════════════════════════════════════════
#  MAIN TABS — Chat & System Analysis
# ════════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["💬 CHAT & INTEL", "🔍 SYSTEM ANALYSIS"])

with tab1:
    # ── Chat History ──
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">SYSTEM READY — AWAITING OPERATOR INPUT</div>
            <div>Welcome, operator. I am your cybersecurity intelligence assistant.</div>
            <br>
            <div class="capability">Explain any cybersecurity attack or concept</div>
            <div class="capability">Identify attack types from your scenario descriptions</div>
            <div class="capability">Suggest immediate protective actions</div>
            <div class="capability">Fetch real-time cybersecurity news & incidents</div>
            <br>
            <div class="hint">Type your query below or select from the sidebar →</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            render_message(msg["role"], msg["content"], msg.get("type", "rag"))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Chat Input ──
    if "pending_query" in st.session_state:
        user_input = st.session_state.pop("pending_query")
    else:
        user_input = st.chat_input("Enter query — describe a scenario, ask a question, or request news...")

    if user_input:
        assistant = st.session_state.assistant

        # Threat level logic (random fluctuation + increase on specific keywords)
        import random
        st.session_state.threat_level = min(95, max(10, st.session_state.threat_level + random.randint(-5, 8)))
        if any(w in user_input.lower() for w in ["hack", "attack", "breach", "malware", "ransomware"]):
            st.session_state.threat_level = min(100, st.session_state.threat_level + 15)
            add_log(f"Suspicious pattern detected in query.", "warn")
        else:
            add_log(f"Processing operator query...", "info")

        # Store user message
        st.session_state.messages.append({"role": "user", "content": user_input, "type": "user"})
        render_message("user", user_input)

        # Determine type
        news_words = ["today", "recent", "latest", "news", "incident", "breach", "happened", "current"]
        is_news = any(w in user_input.lower() for w in news_words)

        # Show cyber loader
        loader_slot = st.empty()
        loader_msg = "SCANNING KNOWLEDGE MATRIX" if use_rag else "PROCESSING VIA LLM"
        loader_slot.markdown(render_cyber_loader(loader_msg), unsafe_allow_html=True)

        try:
            response = assistant.respond(user_input, use_rag=use_rag)
            add_log("Response generated successfully.", "info")
        except Exception as e:
            response = f"[ERROR] Query failed: {str(e)}\n\nIf this is a quota error, please wait or use a new API key."
            add_log(f"Error generating response.", "error")

        loader_slot.empty()

        # Determine message type for display
        msg_type = detect_message_type(user_input, response)

        # Store assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "type": msg_type
        })
        save_chat_history(st.session_state.messages)

        # Render response with optional streaming
        if streaming:
            placeholder = st.empty()
            stream_text(response, placeholder, delay=0.005)
            placeholder.empty()

        render_message("assistant", response, msg_type)
        st.rerun()


with tab2:
    st.markdown('<div class="sidebar-title" style="font-size:0.85rem; margin-bottom:12px;">// SYSTEM VULNERABILITY SCAN</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style='color: var(--text-secondary, #8A9B8F); font-size: 0.85rem; font-family: Inter, sans-serif; line-height: 1.7; margin-bottom: 20px;'>
        Enter your system details to receive a static vulnerability analysis without executing local system scans.
        This keeps your device fully private and runs smoothly via the AI CPU pipeline.
    </p>
    """, unsafe_allow_html=True)

    with st.form("sys_analysis_form"):
        os_val = st.text_input("Operating System", placeholder="e.g., Windows 10, macOS Sonoma, Ubuntu 22.04")
        browser_val = st.text_input("Primary Browser", placeholder="e.g., Chrome v120, Firefox, Safari")
        av_val = st.text_input("Antivirus / Security Software", placeholder="e.g., Windows Defender, None")
        activity_val = st.text_area(
            "Recent Suspicious Activity",
            placeholder="e.g., 'Computer runs exceptionally slow, weird popups, missing files...'"
        )

        analyze_btn = st.form_submit_button("⚡ Run Analysis")

    if analyze_btn:
        if not os_val or not browser_val:
            st.error("Please provide at least your Operating System and Browser.")
        else:
            analysis_loader = st.empty()
            analysis_loader.markdown(render_cyber_loader("ANALYZING SYSTEM PARAMETERS"), unsafe_allow_html=True)

            analysis_result = st.session_state.assistant.analyze_system(os_val, browser_val, av_val, activity_val)

            analysis_loader.empty()
            add_log("System analysis completed.", "info")

            st.markdown(
                f'<span class="badge badge-alert">VULNERABILITY REPORT</span><br>'
                f'<div class="msg-bot" style="border-left-color: var(--accent);">{analysis_result}</div>',
                unsafe_allow_html=True
            )
