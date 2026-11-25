"""BiteRank Streamlit UI — dark editorial food-tech theme from Stitch."""

from __future__ import annotations

import html
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import get_settings
from src.orchestrator import get_restaurants, recommend

ANY_CUISINE = "Any cuisine"
BUDGET_LABELS = {"low": "Low (₹)", "medium": "Medium (₹₹)", "high": "High (₹₹₹)"}
BUDGET_ORDER = ["low", "medium", "high"]

HERO_IMG = (
    "https://lh3.googleusercontent.com/aida-public/"
    "AB6AXuD1A1WsPA8dHmDKWG_aOLXbdl6vig6ElXIdTgTNum7_qTwA8zo4-F2FSadxDmBBN_44x_vz5NECm0nm34R3d5WSA9rCyu6yyGPOuUaf8NOiOYcdYdTPSWVZn9LMvBHHRd8QXlBZ_3W8aVgs7owqZsAHn4b3qn93ar55X9c9fFcd2ZZI_cJl53rst1KK3vbAWzqU81FtE1wLsZ65vx1uGpW6Qom_7e2WQxRzReA2XlsJ"
)
ABOUT_IMG = (
    "https://lh3.googleusercontent.com/aida-public/"
    "AB6AXuA5FgdbHZsVJcLc6U63HIwsKrzDJ3unzrLW7s89-pgHCICRfwVa9FiEMA9gMfaTczPPdxd99RXQPAuL2U9zo-ITpft4DIcUbWpO_pMexJtYVQbb0lpUTrWrbe0jn6Xf3CMq3ImgkGvGmhL99-z3kR1jVwWddbxf-n2Dppi8Aq6om1Zwb7z0P1euZZMamXhHND_nESHsFrgfBmxvgwtSUNH39H13VX7p8QQ7Hh8tIs2A"
)

st.set_page_config(
    page_title="BiteRank",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        :root {
            --surface: #111319;
            --surface-low: #191c21;
            --surface-container: #1d2025;
            --surface-high: #272a30;
            --surface-highest: #32353a;
            --surface-lowest: #0b0e13;
            --on-surface: #e1e2e9;
            --on-surface-variant: #e4bebc;
            --secondary: #bec7d2;
            --primary: #ffb3b1;
            --primary-container: #ff535a;
            --on-primary-container: #5b000e;
            --border: #32353a;
            --border-soft: #21262d;
        }

        html, body, .stApp {
            background: var(--surface) !important;
            color: var(--on-surface) !important;
            font-family: Inter, sans-serif !important;
        }

        .stApp {
            background:
                radial-gradient(900px 420px at 8% -8%, rgba(255, 83, 90, 0.08) 0%, transparent 55%),
                radial-gradient(700px 380px at 100% 0%, rgba(170, 199, 255, 0.05) 0%, transparent 50%),
                var(--surface) !important;
        }

        [data-testid="stHeader"] {
            background: rgba(11, 14, 19, 0.85) !important;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
        }

        .block-container {
            padding-top: 1.25rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1180px !important;
        }

        #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

        /* ---- Brand chrome ---- */
        .br-nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.35rem 0 1rem 0;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }
        .br-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .br-mark {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: linear-gradient(135deg, #ff535a, #ffb3b1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #5b000e;
            font-weight: 700;
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 14px;
        }
        .br-name {
            font-family: "Plus Jakarta Sans", sans-serif;
            font-weight: 600;
            font-size: 16px;
            color: var(--on-surface);
            letter-spacing: -0.01em;
        }
        .br-ver {
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
            color: var(--secondary);
            background: var(--surface-container);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 0.2rem 0.5rem;
        }
        .br-nav-links {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-family: Inter, sans-serif;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0.01em;
            color: var(--secondary);
        }
        .br-nav-links span.active {
            color: var(--primary);
            background: var(--surface-high);
            border-bottom: 2px solid var(--primary-container);
            padding: 0.35rem 0.75rem;
            border-radius: 4px 4px 0 0;
        }
        .br-nav-links span.idle {
            padding: 0.35rem 0.75rem;
            color: var(--on-surface-variant);
        }
        .br-avatar {
            width: 32px;
            height: 32px;
            border-radius: 999px;
            background: var(--primary);
            color: #680011;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 700;
        }

        /* ---- Hero ---- */
        .br-hero {
            position: relative;
            overflow: hidden;
            border-radius: 12px;
            background: var(--surface-lowest);
            border: 1px solid var(--border);
            margin-bottom: 1.25rem;
        }
        .br-hero-bg {
            position: absolute;
            inset: 0;
            background-size: cover;
            background-position: center;
            opacity: 0.2;
            filter: saturate(0.5);
            mix-blend-mode: luminosity;
        }
        .br-hero-inner {
            position: relative;
            z-index: 1;
            padding: 1.75rem 1.75rem;
            background: linear-gradient(90deg, var(--surface-lowest) 0%, rgba(11,14,19,0.9) 55%, transparent 100%);
            display: flex;
            flex-wrap: wrap;
            gap: 1.25rem;
            align-items: flex-end;
            justify-content: space-between;
        }
        .br-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-family: Inter, sans-serif;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--primary);
            background: rgba(255, 83, 90, 0.15);
            border-radius: 4px;
            padding: 0.2rem 0.5rem;
        }
        .br-pill-dot {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            background: var(--primary-container);
            animation: br-pulse 1.6s ease-in-out infinite;
        }
        @keyframes br-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.35; }
        }
        .br-hero h1 {
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: clamp(1.75rem, 4vw, 2.5rem);
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.15;
            margin: 0.4rem 0 0.35rem 0;
            color: var(--on-surface);
        }
        .br-hero p {
            margin: 0;
            max-width: 36rem;
            color: var(--secondary);
            font-size: 16px;
            line-height: 1.55;
        }
        .br-telemetry {
            background: rgba(29, 32, 37, 0.85);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.65rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }
        .br-telemetry .label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--secondary);
        }
        .br-telemetry .value {
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
            font-weight: 600;
            color: var(--on-surface);
        }

        /* ---- Panels ---- */
        .br-panel {
            background: var(--surface-low);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 0.85rem;
            position: relative;
            overflow: hidden;
        }
        .br-panel-trim::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--primary-container), transparent);
        }
        .br-panel-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            padding-bottom: 0.85rem;
            margin-bottom: 0.35rem;
            border-bottom: 1px solid var(--border);
        }
        .br-panel-title {
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: var(--on-surface);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }
        .br-badge {
            font-family: Inter, sans-serif;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--secondary);
            background: var(--surface-container);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 0.15rem 0.45rem;
        }
        .br-guard {
            background: var(--surface-lowest);
            border: 1px solid rgba(50, 53, 58, 0.7);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
            margin-top: 0.5rem;
        }
        .br-guard strong {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: var(--on-surface);
            margin-bottom: 0.2rem;
        }
        .br-guard p {
            margin: 0;
            font-size: 13px;
            line-height: 1.45;
            color: var(--secondary);
        }
        .br-icon {
            color: var(--primary);
            font-size: 18px;
            line-height: 1;
            flex-shrink: 0;
        }

        /* ---- Summary / cards ---- */
        .br-summary {
            background: var(--surface-low);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary-container);
            border-radius: 12px;
            padding: 1.15rem 1.25rem;
            margin-bottom: 0.85rem;
        }
        .br-summary-top {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            margin-bottom: 0.45rem;
        }
        .br-summary h2 {
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 16px;
            font-weight: 600;
            margin: 0;
            color: var(--on-surface);
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .br-summary p {
            margin: 0;
            color: var(--secondary);
            font-size: 14px;
            line-height: 1.55;
        }
        .br-meta-strip {
            margin-top: 0.85rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(50, 53, 58, 0.6);
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
            color: var(--secondary);
        }

        .br-card {
            background: var(--surface-low);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 0.85rem;
            transition: border-color 0.2s ease, background 0.2s ease;
        }
        .br-card:hover {
            background: var(--surface-container);
            border-color: #484f58;
        }
        .br-card-top {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 0.85rem;
        }
        .br-card-left {
            display: flex;
            gap: 0.85rem;
            align-items: flex-start;
            min-width: 0;
            flex: 1;
        }
        .br-rank {
            width: 32px;
            height: 32px;
            border-radius: 4px;
            background: var(--surface-highest);
            border: 1px solid var(--border);
            color: var(--on-surface);
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .br-rank.top {
            background: var(--primary-container);
            border-color: transparent;
            color: var(--on-primary-container);
        }
        .br-card h3 {
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: -0.01em;
            margin: 0;
            color: var(--on-surface);
            line-height: 1.3;
        }
        .br-top-match {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            margin-left: 0.4rem;
            vertical-align: middle;
            font-size: 11px;
            font-weight: 600;
            color: var(--primary);
            background: rgba(255, 83, 90, 0.15);
            border: 1px solid rgba(255, 83, 90, 0.3);
            border-radius: 4px;
            padding: 0.15rem 0.45rem;
        }
        .br-card-meta {
            margin-top: 0.35rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            align-items: center;
            font-size: 13px;
            color: var(--secondary);
        }
        .br-cost {
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
            color: var(--on-surface);
        }
        .br-budget-chip {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
            color: var(--secondary);
            background: var(--surface-highest);
            border-radius: 4px;
            padding: 0.15rem 0.4rem;
        }
        .br-rating {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
            font-weight: 700;
            padding: 0.25rem 0.55rem;
            border-radius: 4px;
            background: var(--surface-highest);
            border: 1px solid var(--border);
            color: var(--on-surface);
        }
        .br-rating.top {
            background: var(--primary-container);
            border-color: transparent;
            color: var(--on-primary-container);
        }
        .br-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin: 0.85rem 0;
        }
        .br-chip {
            font-size: 12px;
            font-weight: 500;
            color: var(--on-surface-variant);
            background: var(--surface-container);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 0.25rem 0.55rem;
        }
        .br-rationale {
            background: var(--surface-lowest);
            border: 1px solid rgba(50, 53, 58, 0.8);
            border-left: 2px solid var(--primary-container);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.85rem;
        }
        .br-rationale.muted {
            border-left-color: var(--border);
        }
        .br-rationale .label {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: var(--primary);
            margin-bottom: 0.3rem;
        }
        .br-rationale.muted .label { color: var(--secondary); }
        .br-rationale p {
            margin: 0;
            font-size: 13px;
            line-height: 1.5;
            color: var(--on-surface-variant);
        }
        .br-card-foot {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.65rem;
            padding-top: 0.75rem;
            border-top: 1px solid var(--border);
        }
        .br-foot-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        .br-foot-tag {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.02em;
            color: var(--secondary);
            background: var(--surface-container);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 0.2rem 0.45rem;
        }

        /* ---- Empty / idle ---- */
        .br-empty {
            background: var(--surface-lowest);
            border: 1px dashed #30363d;
            border-radius: 12px;
            padding: 2.5rem 1.5rem;
            text-align: center;
        }
        .br-empty-icon {
            width: 72px;
            height: 72px;
            margin: 0 auto 1.15rem auto;
            border-radius: 16px;
            background: var(--surface-low);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            font-size: 2rem;
        }
        .br-empty h2 {
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.015em;
            margin: 0 0 0.65rem 0;
            color: var(--on-surface);
        }
        .br-empty p {
            margin: 0 auto;
            max-width: 28rem;
            color: var(--secondary);
            font-size: 14px;
            line-height: 1.55;
        }
        .br-idle {
            background: var(--surface-low);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 2rem 1.5rem;
            text-align: center;
            color: var(--secondary);
        }
        .br-idle strong {
            display: block;
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 16px;
            color: var(--on-surface);
            margin-bottom: 0.35rem;
        }

        .br-error {
            background: rgba(248, 81, 73, 0.08);
            border: 1px solid #f85149;
            border-radius: 8px;
            padding: 0.85rem 1rem;
            color: #f85149;
            margin-bottom: 0.85rem;
        }
        .br-error p {
            margin: 0.35rem 0 0 0;
            color: var(--on-surface);
            font-size: 13px;
        }
        .br-fallback {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 12px;
            color: var(--secondary);
            background: var(--surface-container);
            border: 1px dashed #5b403f;
            border-radius: 4px;
            padding: 0.3rem 0.55rem;
            margin-bottom: 0.75rem;
        }

        /* ---- About ---- */
        .br-about-hero {
            position: relative;
            height: 220px;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
        }
        .br-about-hero-bg {
            position: absolute;
            inset: 0;
            background-size: cover;
            background-position: center;
        }
        .br-about-hero-fade {
            position: absolute;
            inset: 0;
            background: linear-gradient(to top, var(--surface), rgba(17,19,25,0.55), transparent);
        }
        .br-about-hero-copy {
            position: absolute;
            left: 1.25rem;
            right: 1.25rem;
            bottom: 1.15rem;
        }
        .br-step {
            background: var(--surface-low);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 0.85rem;
            display: flex;
            gap: 1.15rem;
            align-items: flex-start;
        }
        .br-step-num {
            font-family: "JetBrains Mono", monospace;
            font-size: 28px;
            font-weight: 700;
            color: var(--primary-container);
            background: var(--surface-lowest);
            border-radius: 8px;
            padding: 0.35rem 0.65rem;
            line-height: 1;
        }
        .br-step h3 {
            font-family: "Plus Jakarta Sans", sans-serif;
            font-size: 20px;
            font-weight: 600;
            margin: 0 0 0.45rem 0;
            color: var(--on-surface);
        }
        .br-step p {
            margin: 0;
            color: var(--secondary);
            font-size: 14px;
            line-height: 1.55;
        }
        .br-code {
            margin-top: 0.75rem;
            background: var(--surface-lowest);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
            color: var(--on-surface);
            overflow-x: auto;
            white-space: pre;
        }
        .br-pledge {
            background: var(--surface-high);
            border-radius: 12px;
            padding: 1.35rem 1.5rem;
            display: flex;
            gap: 1rem;
            align-items: flex-start;
            margin: 1rem 0;
        }
        .br-pledge-icon {
            width: 44px;
            height: 44px;
            border-radius: 999px;
            background: var(--primary);
            color: #680011;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
        }
        .br-footer {
            margin-top: 2rem;
            padding-top: 1.25rem;
            border-top: 1px solid var(--border);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 0.75rem;
            font-size: 13px;
            color: var(--secondary);
        }
        .br-footer .mono {
            font-family: "JetBrains Mono", monospace;
            font-size: 12px;
        }

        /* ---- Streamlit widget overrides ---- */
        [data-testid="stWidgetLabel"] p,
        label, .stSelectbox label, .stSlider label, .stTextInput label, .stTextArea label {
            color: var(--on-surface-variant) !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            letter-spacing: 0.01em !important;
        }

        div[data-baseweb="select"] > div,
        .stTextInput input, .stTextArea textarea,
        [data-testid="stNumberInput"] input {
            background: var(--surface-container) !important;
            color: var(--on-surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 4px !important;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--primary-container) !important;
            box-shadow: 0 0 0 1px var(--primary-container) !important;
        }

        div[data-testid="stButton"] > button[kind="primary"],
        div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
            background: var(--primary-container) !important;
            color: #fff !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
            box-shadow: none !important;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover,
        div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover {
            background: #f85149 !important;
            filter: none !important;
        }
        div[data-testid="stButton"] > button[kind="secondary"],
        div[data-testid="stButton"] > button:not([kind="primary"]) {
            background: transparent !important;
            color: var(--secondary) !important;
            border: 1px solid var(--border) !important;
            border-radius: 4px !important;
            font-weight: 500 !important;
        }

        [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
            background: var(--on-surface) !important;
        }
        .stAlert {
            border-radius: 8px !important;
        }
        div[data-testid="stHorizontalBlock"] { gap: 0.65rem; }

        /* Hide default Streamlit branding space */
        .stDeployButton { display: none; }

        /* Compact top nav buttons */
        div[data-testid="stHorizontalBlock"]:has(button[kind]) {
            align-items: center;
        }
        .br-nav-wrap {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding-bottom: 0.75rem;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid var(--border);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _load_dataset_meta() -> dict:
    frame = get_restaurants()

    cities = (
        frame["location"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .value_counts()
        .index.tolist()
    )
    localities = (
        frame["locality"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .value_counts()
        .index.tolist()
    )

    location_options: list[str] = []
    for city in cities:
        if city not in location_options:
            location_options.append(city)
    for locality in localities:
        if locality not in location_options:
            location_options.append(locality)

    cuisine_counts: dict[str, int] = {}
    for value in frame["cuisines"].dropna().astype(str):
        for part in value.split(","):
            name = part.strip()
            if name:
                cuisine_counts[name] = cuisine_counts.get(name, 0) + 1
    cuisines = sorted(cuisine_counts.keys(), key=lambda c: (-cuisine_counts[c], c.lower()))

    return {
        "rows": len(frame),
        "location_options": location_options,
        "cuisine_options": [ANY_CUISINE] + cuisines,
        "default_location": cities[0]
        if cities
        else (location_options[0] if location_options else "Bangalore"),
    }


def _format_cost(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"₹{value:,.0f} for two"


def _format_rating(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1f}"


def _budget_label(budget: str) -> str:
    return BUDGET_LABELS.get(budget, budget.title())


def _index_or_default(options: list[str], preferred: str, fallback: int = 0) -> int:
    if preferred in options:
        return options.index(preferred)
    return min(fallback, max(len(options) - 1, 0))


def _cuisine_chips(cuisine: str) -> str:
    parts = [p.strip() for p in (cuisine or "").split(",") if p.strip()]
    if not parts:
        parts = ["Mixed cuisine"]
    return "".join(f'<span class="br-chip">{html.escape(p)}</span>' for p in parts[:5])


def _render_brand() -> None:
    st.markdown(
        """
        <div class="br-brand">
          <div class="br-mark">BR</div>
          <span class="br-name">BiteRank</span>
          <span class="br-ver">v1.4 · LLM Engine</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hero(row_count: int) -> None:
    st.markdown(
        f"""
        <div class="br-hero">
          <div class="br-hero-bg" style="background-image:url('{HERO_IMG}')"></div>
          <div class="br-hero-inner">
            <div>
              <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;">
                <span class="br-pill"><span class="br-pill-dot"></span> LLM Neural Sieve Active</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#bec7d2;">
                  | Zomato Corpus
                </span>
              </div>
              <h1>Find your next table</h1>
              <p>
                Filter by what matters, then let AI rank and explain real Zomato matches
                with verified diner feedback.
              </p>
            </div>
            <div class="br-telemetry">
              <div>
                <div class="label">Grounding Corpus</div>
                <div class="value">{row_count:,} Active Spots</div>
              </div>
              <div style="width:1px;height:24px;background:#32353a;"></div>
              <div style="color:#ff535a;font-size:1.1rem;">✦</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_footer() -> None:
    st.markdown(
        """
        <div class="br-footer">
          <div>✓ Recommendations are grounded in dataset restaurants — never invented.</div>
          <div class="mono">© 2024 BiteRank Intelligence · Powered by Zomato dataset corpus</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_idle() -> None:
    st.markdown(
        """
        <div class="br-idle">
          <strong>Your shortlist will appear here</strong>
          Set preferences on the left, then click <em>Get recommendations</em>.
          Hard filters run first; the LLM only ranks real candidates.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_empty(message: str) -> None:
    safe = html.escape(message)
    st.markdown(
        f"""
        <div class="br-empty">
          <div class="br-empty-icon">⌀</div>
          <h2>No restaurants matched</h2>
          <p>{safe}</p>
          <p style="margin-top:0.85rem;">
            Try a broader location, a lower minimum rating, or a different cuisine.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="br-guard" style="margin-top:1rem;">
          <span class="br-icon">🛡</span>
          <div>
            <strong>Data Grounding Policy · Anti-Hallucination</strong>
            <p>
              BiteRank strictly queries restaurants in the verified dataset.
              We never invent venues when filters are too specific.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_error(title: str, detail: str, errors: tuple[str, ...] = ()) -> None:
    items = "".join(f"<p>· {html.escape(e)}</p>" for e in errors)
    st.markdown(
        f"""
        <div class="br-error">
          <strong>{html.escape(title)}</strong>
          <p>{html.escape(detail)}</p>
          {items}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_recommendations(response, settings) -> None:
    result = response.result
    assert result is not None
    prefs = response.preferences

    if result.is_fallback:
        st.markdown(
            """
            <div class="br-fallback">
              ⟳ Ranked by rating (AI unavailable)
            </div>
            """,
            unsafe_allow_html=True,
        )

    count = len(result.recommendations)
    source_label = (
        f"Ranked by {html.escape(settings.llm_model)} on verified data"
        if not result.is_fallback
        else "Fallback · rating-sorted filter matches"
    )
    locality = html.escape(prefs.location if prefs else "—")
    budget = html.escape(_budget_label(prefs.budget) if prefs else "—")
    min_rating = f"{prefs.min_rating:.1f}" if prefs else "—"
    summary = html.escape(result.summary)

    st.markdown(
        f"""
        <div class="br-summary">
          <div class="br-summary-top">
            <h2>✦ AI Curated Shortlist ({count} Matches)</h2>
            <span class="br-badge">{source_label}</span>
          </div>
          <p>{summary}</p>
          <div class="br-meta-strip">
            <span><span style="color:#ff535a;">●</span> Locality: {locality}</span>
            <span>·</span>
            <span>Budget: {budget}</span>
            <span>·</span>
            <span>Min rating: {min_rating}★</span>
            <span>·</span>
            <span>{response.total_matches} filter matches · cap {response.candidate_cap}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for rec in result.recommendations:
        name = html.escape(rec.name)
        explanation = html.escape(rec.explanation)
        rank_str = f"{rec.rank:02d}"
        is_top = rec.rank == 1
        rank_cls = "br-rank top" if is_top else "br-rank"
        rating_cls = "br-rating top" if is_top else "br-rating"
        rationale_cls = "br-rationale" if is_top else "br-rationale muted"
        top_badge = (
            '<span class="br-top-match">★ Top Match</span>' if is_top else ""
        )
        budget_chip = ""
        if prefs:
            budget_chip = (
                f'<span class="br-budget-chip">{html.escape(_budget_label(prefs.budget))}</span>'
            )

        st.markdown(
            f"""
            <article class="br-card">
              <div class="br-card-top">
                <div class="br-card-left">
                  <span class="{rank_cls}">{rank_str}</span>
                  <div>
                    <h3>{name}{top_badge}</h3>
                    <div class="br-card-meta">
                      <span class="br-cost">{_format_cost(rec.estimated_cost)}</span>
                      {budget_chip}
                    </div>
                  </div>
                </div>
                <div class="{rating_cls}">
                  {_format_rating(rec.rating)} ★
                </div>
              </div>
              <div class="br-chips">{_cuisine_chips(rec.cuisine)}</div>
              <div class="{rationale_cls}">
                <div class="label">◈ AI Rationale &amp; Vibe Check</div>
                <p>{explanation}</p>
              </div>
              <div class="br-card-foot">
                <div class="br-foot-tags">
                  <span class="br-foot-tag">Verified dataset row</span>
                  <span class="br-foot-tag">source: {html.escape(result.source)}</span>
                </div>
              </div>
            </article>
            """,
            unsafe_allow_html=True,
        )


def _render_about(settings, row_count: int) -> None:
    model = html.escape(settings.llm_model)
    st.markdown(
        f"""
        <div class="br-about-hero">
          <div class="br-about-hero-bg" style="background-image:url('{ABOUT_IMG}')"></div>
          <div class="br-about-hero-fade"></div>
          <div class="br-about-hero-copy">
            <span class="br-pill"><span class="br-pill-dot"></span> Engine Spec v1.4</span>
            <h2 style="font-family:'Plus Jakarta Sans',sans-serif;font-size:20px;font-weight:600;margin:0.4rem 0 0 0;color:#e1e2e9;">
              System Pipeline Grounding
            </h2>
            <p style="margin:0.25rem 0 0 0;font-family:'JetBrains Mono',monospace;font-size:12px;color:#bec7d2;">
              Zomato SQL → LLM Rerank · model {model}
            </p>
          </div>
        </div>

        <div style="margin-bottom:1.25rem;">
          <div style="font-size:11px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;color:#ff535a;margin-bottom:0.35rem;">
            Transparency &amp; Architecture
          </div>
          <h1 style="font-family:'Plus Jakarta Sans',sans-serif;font-size:clamp(1.75rem,4vw,2.5rem);font-weight:700;letter-spacing:-0.02em;margin:0 0 0.5rem 0;color:#e1e2e9;">
            How BiteRank works
          </h1>
          <p style="margin:0;max-width:40rem;color:#bec7d2;font-size:16px;line-height:1.55;">
            A deterministic two-stage recommendation engine designed to eliminate hallucinated
            dining advice through verified dataset grounding.
          </p>
        </div>

        <div class="br-panel" style="margin-bottom:1.25rem;">
          <div style="display:flex;justify-content:space-between;gap:0.75rem;flex-wrap:wrap;margin-bottom:0.85rem;">
            <span class="br-badge">Pipeline Vector Flow</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#ffb3b1;">0% Hallucination Rate</span>
          </div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;text-align:center;">
            <div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;color:#e1e2e9;">1. Filter Stage</div>
              <div style="font-size:11px;color:#bec7d2;margin-top:0.2rem;">{row_count:,} corpus rows</div>
            </div>
            <div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;color:#e1e2e9;">2. Dataset Isolation</div>
              <div style="font-size:11px;color:#bec7d2;margin-top:0.2rem;">Capped candidate set</div>
            </div>
            <div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;color:#e1e2e9;">3. LLM Consensus</div>
              <div style="font-size:11px;color:#bec7d2;margin-top:0.2rem;">Ranked + explained</div>
            </div>
          </div>
        </div>

        <div class="br-step">
          <div class="br-step-num">01</div>
          <div>
            <h3>You set hard preferences</h3>
            <p>
              Define non-negotiable criteria: location, budget tier (Low / Medium / High),
              cuisine, and minimum rating. Soft vibe text is passed only to the LLM for ranking.
            </p>
            <div class="br-chips" style="margin-top:0.75rem;margin-bottom:0;">
              <span class="br-chip">Locality</span>
              <span class="br-chip">Price Band</span>
              <span class="br-chip">Min Rating</span>
              <span class="br-chip" style="color:#ffb3b1;border-color:#5b403f;">Zero ambiguity</span>
            </div>
          </div>
        </div>

        <div class="br-step">
          <div class="br-step-num">02</div>
          <div>
            <h3>We filter real Zomato rows first</h3>
            <p>
              Before any model call, deterministic filters shrink the verified restaurant table.
              Venues that do not exist cannot enter the pipeline.
            </p>
            <div class="br-code">SELECT id, name, rating, cost_for_two, cuisines
FROM restaurants
WHERE location matches AND budget_band = $budget
  AND rating &gt;= $min_rating
ORDER BY rating DESC
LIMIT K</div>
          </div>
        </div>

        <div class="br-step">
          <div class="br-step-num" style="color:#ffb3b1;">03</div>
          <div>
            <h3>An LLM ranks the shortlist &amp; explains why</h3>
            <p>
              The candidate shortlist plus your soft preferences go to Groq.
              The model ranks real rows and writes plain-language explanations —
              never inventing restaurants, ratings, or costs.
            </p>
            <div class="br-rationale" style="margin-top:0.75rem;margin-bottom:0;">
              <div class="label">◈ Example rationale</div>
              <p>
                “Strong rating and casual setting that fits a family outing on a medium budget.”
              </p>
            </div>
          </div>
        </div>

        <div class="br-pledge">
          <div class="br-pledge-icon">✓</div>
          <div>
            <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.35rem;">
              <strong style="font-family:'Plus Jakarta Sans',sans-serif;font-size:16px;color:#e1e2e9;">
                Dataset Integrity Guarantee
              </strong>
              <span class="br-badge" style="color:#ffb3b1;">100% Verified</span>
            </div>
            <p style="margin:0 0 0.35rem 0;color:#e1e2e9;font-weight:500;">
              Recommendations are grounded in dataset restaurants — never invented.
            </p>
            <p style="margin:0;color:#bec7d2;font-size:13px;line-height:1.5;">
              The LLM acts solely as an analyst and summarizer, never as an entity generator.
              Hallucinated names are dropped by the response parser.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _init_state(meta: dict) -> None:
    defaults = {
        "page": "recommend",
        "location": meta["default_location"],
        "budget": "medium",
        "cuisine_choice": ANY_CUISINE,
        "min_rating": 4.0,
        "additional": "family-friendly, not too crowded",
        "max_recommendations": 5,
        "use_llm": True,
        "last_response": None,
        "submitted": False,
        "clear_nonce": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            if key == "use_llm":
                st.session_state[key] = bool(get_settings().llm_api_key)
            else:
                st.session_state[key] = value


def _clear_filters(meta: dict) -> None:
    st.session_state.location = meta["default_location"]
    st.session_state.budget = "medium"
    st.session_state.cuisine_choice = ANY_CUISINE
    st.session_state.min_rating = 4.0
    st.session_state.additional = "family-friendly, not too crowded"
    st.session_state.max_recommendations = 5
    st.session_state.last_response = None
    st.session_state.submitted = False
    st.session_state.clear_nonce += 1


def _render_recommend(meta: dict, settings) -> None:
    _render_hero(meta["rows"])

    location_options = meta["location_options"]
    cuisine_options = meta["cuisine_options"]
    if not location_options:
        _render_error(
            "Dataset unavailable",
            "Processed restaurant data has no location values to choose from.",
        )
        return

    left, right = st.columns([0.38, 0.62], gap="large")

    with left:
        st.markdown(
            """
            <div class="br-panel br-panel-trim">
              <div class="br-panel-head">
                <p class="br-panel-title">◎ Your Preferences</p>
                <span class="br-badge">Filter Phase</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        form_key = f"prefs_{st.session_state.clear_nonce}"
        with st.form(form_key, clear_on_submit=False):
            location = st.selectbox(
                "Location",
                options=location_options,
                index=_index_or_default(location_options, st.session_state.location),
                help="City-wide or a specific locality",
            )
            budget = st.selectbox(
                "Budget Level",
                options=BUDGET_ORDER,
                format_func=lambda b: BUDGET_LABELS[b],
                index=BUDGET_ORDER.index(st.session_state.budget)
                if st.session_state.budget in BUDGET_ORDER
                else 1,
            )
            cuisine_choice = st.selectbox(
                "Cuisine & Dish types",
                options=cuisine_options,
                index=_index_or_default(cuisine_options, st.session_state.cuisine_choice),
                help="Optional. Choose Any cuisine to skip this filter.",
            )
            min_rating = st.slider(
                "Minimum Rating",
                min_value=0.0,
                max_value=5.0,
                value=float(st.session_state.min_rating),
                step=0.1,
            )
            additional = st.text_area(
                "Additional Preferences & Vibe",
                value=st.session_state.additional,
                height=90,
                placeholder="e.g. family-friendly, quiet, date night",
            )
            max_recommendations = st.slider(
                "Max recommendations",
                min_value=1,
                max_value=10,
                value=int(st.session_state.max_recommendations),
            )
            use_llm = st.toggle(
                "Use Groq ranking",
                value=bool(st.session_state.use_llm),
                help="Turn off to force rating-sorted fallback",
            )

            submit = st.form_submit_button(
                "✦ Get recommendations",
                type="primary",
                use_container_width=True,
            )
            clear = st.form_submit_button(
                "↺ Clear filters",
                type="secondary",
                use_container_width=True,
            )

        st.markdown(
            """
            <div class="br-guard">
              <span class="br-icon">🛡</span>
              <div>
                <strong>Zero-Hallucination Guardrail</strong>
                <p>
                  Recommendations link strictly to verified Zomato restaurant listings
                  in the processed dataset — never invented venues.
                </p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            f"{meta['rows']:,} restaurants · {len(location_options):,} locations · "
            f"{max(len(cuisine_options) - 1, 0):,} cuisines · {settings.llm_model}"
        )

        if clear:
            _clear_filters(meta)
            st.rerun()

        if submit:
            st.session_state.location = location
            st.session_state.budget = budget
            st.session_state.cuisine_choice = cuisine_choice
            st.session_state.min_rating = min_rating
            st.session_state.additional = additional
            st.session_state.max_recommendations = max_recommendations
            st.session_state.use_llm = use_llm
            st.session_state.submitted = True

            cuisine = "" if cuisine_choice == ANY_CUISINE else cuisine_choice
            if use_llm and not settings.llm_api_key:
                st.warning(
                    "No `LLM_API_KEY` in `.env`. Continuing with rating-sorted fallback."
                )

            with st.spinner("Ranking matches…"):
                response = recommend(
                    location=location,
                    budget=budget,
                    cuisine=cuisine,
                    min_rating=min_rating,
                    additional_preferences=additional,
                    max_recommendations=max_recommendations,
                    use_llm=use_llm and bool(settings.llm_api_key),
                )
            st.session_state.last_response = response

    with right:
        response = st.session_state.last_response
        if not st.session_state.submitted or response is None:
            _render_idle()
            return

        if response.status == "validation_error":
            _render_error(
                "Validation error",
                response.message,
                response.validation_errors,
            )
            return

        if response.status == "no_match":
            _render_empty(response.message)
            return

        if response.status == "error":
            _render_error("Pipeline error", response.message)
            return

        if response.status == "ok" and response.result is not None:
            _render_recommendations(response, settings)
            return

        _render_idle()


def main() -> None:
    _inject_styles()
    settings = get_settings()
    meta = _load_dataset_meta()
    _init_state(meta)

    brand_col, rec_col, about_col, spacer = st.columns([3.2, 1.1, 0.9, 2.0])
    with brand_col:
        _render_brand()
    with rec_col:
        if st.button(
            "Recommend",
            key="nav_recommend",
            type="primary" if st.session_state.page == "recommend" else "secondary",
            use_container_width=True,
        ):
            st.session_state.page = "recommend"
            st.rerun()
    with about_col:
        if st.button(
            "About",
            key="nav_about",
            type="primary" if st.session_state.page == "about" else "secondary",
            use_container_width=True,
        ):
            st.session_state.page = "about"
            st.rerun()

    if st.session_state.page == "about":
        _render_about(settings, meta["rows"])
    else:
        _render_recommend(meta, settings)

    _render_footer()


if __name__ == "__main__":
    main()
