from __future__ import annotations

import html
import base64
import io
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).parent
DATA_PATH = APP_DIR / "Netflix.csv"
VIDEO_PATH = APP_DIR / "BG Video.mp4"
LOGO_IMAGE_PATH = APP_DIR / "Netflix-logo.jpg"
if not LOGO_IMAGE_PATH.exists():
    LOGO_IMAGE_PATH = APP_DIR / "Netfilx-logo.jpg"
FILTER_COLUMNS = (
    "Region",
    "Subscription_Plan",
    "Category",
    "Type",
    "Language",
    "Device",
    "Payment_Method",
)
FILTER_LABELS = {
    "Region": "Region",
    "Subscription_Plan": "Subscription plan",
    "Category": "Category",
    "Type": "Content type",
    "Language": "Language",
    "Device": "Device",
    "Payment_Method": "Payment method",
}
ACCENT = "#E50914"
INK = "#1D2735"
MUTED = "#778292"
GRID = "#E9EDF2"
PALETTE = [ACCENT, "#536B82", "#8BA2AF", "#C0CBD2", "#D5A36B", "#34495E"]


def image_data_uri(path: Path, mime_type: str) -> str:
    if not path.is_file():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


BACKGROUND_VIDEO_URI = image_data_uri(VIDEO_PATH, "video/mp4")
LOGO_IMAGE_URI = image_data_uri(LOGO_IMAGE_PATH, "image/jpeg")

st.set_page_config(
    page_title="Netflix Insights | Analytics",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="auto",
)
st.session_state.setdefault("professional_theme_enabled", True)

st.markdown(
    """
    <style>
    :root {
        --accent: #e50914;
        --accent-blue: #3b82f6;
        --ink: #f8fafc;
        --secondary: #cbd5e1;
        --muted: #94a3b8;
        --line: rgba(255, 255, 255, .08);
        --canvas: #0b0f14;
        --surface: #151b24;
        --elevated: #1a2230;
        --sidebar: #111827;
    }
    .stApp { background: var(--canvas); color: var(--ink); overflow-x: clip; }
    [data-testid="stAppViewContainer"] { position: relative; isolation: isolate; background: var(--canvas); color: var(--ink); }
    [data-testid="stMain"] { position: relative; z-index: 1; background: var(--canvas); color: var(--ink); }
    @keyframes background-drift {
        from { transform: scale(1.01) translate3d(0, 0, 0); }
        to { transform: scale(1.045) translate3d(-.35%, .25%, 0); }
    }
    @keyframes content-enter {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .block-container { max-width: 1520px; padding: 2rem 2.6rem 3.5rem; }
    h1, h2, h3, p, label, [data-testid="stMetricValue"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        letter-spacing: 0;
    }
    [data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stSidebar"] {
        position: relative; z-index: 2; background: var(--sidebar);
        border-right: 1px solid rgba(255, 255, 255, .07);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label { color: #f1f5f9; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: var(--secondary); }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: var(--elevated); border: 1px dashed #475569; border-radius: 9px;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small { color: #f8fafc !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        color: #f8fafc !important; background: #273346 !important; border-color: #475569 !important;
    }
    .source-card { margin: .85rem 0 1rem; padding: .9rem; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; }
    .source-label { margin: 0 0 .45rem; color: var(--secondary); font-size: .72rem; font-weight: 700; letter-spacing: .04em; }
    .source-kind { display: flex; align-items: center; gap: .45rem; color: var(--ink); font-size: .88rem; font-weight: 700; }
    .source-file { overflow-wrap: anywhere; margin: .22rem 0 0 1rem; color: var(--secondary); font-size: .8rem; }
    .source-count { margin: .45rem 0 0; color: var(--secondary); font-size: .76rem; }
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] > div > div,
    [data-testid="stSidebar"] [data-testid="stDateInput"] > div > div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        color: var(--ink); background: var(--surface); border-color: #344154; border-radius: 8px;
    }
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] input,
    [data-testid="stSidebar"] [data-testid="stDateInput"] input,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] input { color: var(--ink); }
    [data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div,
    [data-testid="stSidebar"] [data-baseweb="input"]:focus-within > div { border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent); }
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
        color: #f8fafc; background: var(--elevated); border: 1px solid #3a4658;
        border-radius: 8px; min-height: 2.55rem;
    }
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
        color: white; border-color: #56657a; background: #202b3b;
    }
    .hero {
        position: relative; display: grid; grid-template-columns: minmax(0, 1fr) auto;
        gap: 2rem; align-items: center; overflow: hidden; min-height: 232px;
        padding: 2rem 2.2rem; margin: .15rem 0 1.35rem;
        color: white; background: #172231;
        border: 1px solid #26384b; border-left: 4px solid var(--accent);
        border-radius: 14px; box-shadow: 0 12px 30px rgba(24, 38, 53, .16);
        animation: content-enter .7s ease-out both;
    }
    .hero::before {
        content: ""; position: absolute; inset: 0; z-index: 1; pointer-events: none;
        background: linear-gradient(105deg, rgba(18, 29, 42, .70) 0%, rgba(20, 34, 49, .38) 58%, rgba(22, 34, 48, .48) 100%);
    }
    .hero-video { position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; object-position: center 42%; pointer-events: none; }
    .hero > *:not(.hero-video) { position: relative; z-index: 2; }
    .brand-lockup { display: grid; grid-template-columns: 82px minmax(0, 1fr); align-items: center; gap: 1rem; }
    .logo-frame { display: grid; width: 82px; height: 82px; overflow: hidden; place-items: center; background: #050505; border: 1px solid #ffffff20; border-radius: 12px; box-shadow: 0 5px 18px #0005; animation: content-enter .7s .08s ease-out both; }
    .netflix-logo { display: block; width: 100%; height: 100%; object-fit: contain; transition: transform .35s ease; }
    .logo-frame:hover .netflix-logo { transform: scale(1.035); }
    .hero-kicker { display: flex; align-items: center; gap: .55rem; color: #c4ced9; font-size: .72rem; font-weight: 700; line-height: 1.4; text-transform: uppercase; text-shadow: 0 1px 4px #0009; }
    .hero-kicker-mark { width: 19px; height: 2px; background: var(--accent); }
    .hero-brand { margin: .65rem 0 0; color: white; font-size: 2rem; font-weight: 700; line-height: 1.15; text-shadow: 0 2px 8px #000a; animation: content-enter .7s .14s ease-out both; }
    .hero-title { margin: .14rem 0 .55rem; color: #d8e0e8; font-size: 1.08rem; font-weight: 550; text-shadow: 0 1px 5px #0009; animation: content-enter .7s .2s ease-out both; }
    .hero-copy { max-width: 720px; margin: 0; color: #e0e7ee; font-size: .91rem; line-height: 1.55; text-shadow: 0 1px 5px #0009; animation: content-enter .7s .28s ease-out both; }
    .hero-meta { display: flex; flex-direction: column; align-items: flex-end; gap: .7rem; min-width: 150px; }
    .hero-stat { color: white; font-size: 1.3rem; font-weight: 700; text-align: right; }
    .hero-stat span { display: block; margin-top: .12rem; color: #9eacbc; font-size: .68rem; font-weight: 600; text-transform: uppercase; white-space: nowrap; }
    .hero-period { width: fit-content; padding: .45rem .65rem; color: #d8e0e8; background: #ffffff0d; border: 1px solid #ffffff1b; border-radius: 6px; font-size: .76rem; white-space: nowrap; }
    .dataset-status { display: inline-flex; align-items: center; gap: .42rem; padding: .4rem .6rem; color: #d9e5dd; background: #5c99751b; border: 1px solid #83ba981e; border-radius: 20px; font-size: .7rem; }
    .dataset-status-dot { width: 7px; height: 7px; background: #76c295; border-radius: 50%; }
    .section-row { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; margin: 1.8rem 0 .85rem; }
    .section-title { margin: 0; color: var(--ink); font-size: 1.2rem; font-weight: 700; line-height: 1.3; }
    .section-note { margin: 0; color: var(--secondary); font-size: .8rem; }
    .breadcrumb { display: flex; align-items: center; gap: .5rem; margin: .25rem 0 .75rem; color: var(--muted); font-size: .76rem; }
    .breadcrumb-current { color: var(--secondary); font-weight: 650; }
    [data-testid="stSidebar"] [data-testid="stRadioOption"] {
        margin: .1rem 0; padding: .48rem .62rem; border-left: 2px solid transparent;
        border-radius: 7px; color: var(--secondary); transition: background .16s ease, color .16s ease, border-color .16s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadioOption"]:hover {
        color: #fff; background: rgba(255, 255, 255, .055);
    }
    [data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked) {
        color: #fff; background: rgba(229, 9, 20, .12); border-left-color: var(--accent); font-weight: 650;
    }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .8rem; margin: .6rem 0 1.35rem; }
    .kpi-card {
        min-width: 0; padding: 1rem 1.08rem .95rem; background: var(--surface);
        border: 1px solid var(--line); border-radius: 11px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, .18);
        transition: transform .2s ease, box-shadow .2s ease;
    }
    .kpi-card:hover { transform: translateY(-2px); border-color: rgba(148, 163, 184, .32); box-shadow: 0 10px 24px rgba(0, 0, 0, .28); }
    .kpi-top { display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
    .kpi-label { overflow: hidden; color: var(--secondary); font-size: .78rem; font-weight: 650; text-overflow: ellipsis; white-space: nowrap; }
    .kpi-mark { display: grid; flex: 0 0 auto; min-width: 29px; height: 29px; padding: 0 .28rem; place-items: center; color: #fca5a5; background: rgba(229, 9, 20, .14); border: 1px solid rgba(229, 9, 20, .22); border-radius: 8px; font-size: .62rem; font-weight: 750; }
    .kpi-value { overflow: hidden; margin: .5rem 0 .16rem; color: #f8fafc; font-size: 1.75rem; font-weight: 720; line-height: 1.1; text-overflow: ellipsis; white-space: nowrap; }
    .kpi-note { overflow: hidden; color: var(--muted); font-size: .74rem; text-overflow: ellipsis; white-space: nowrap; }
    .insight-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .75rem; margin-bottom: 1.5rem; }
    .insight-card { min-height: 92px; padding: .9rem 1rem; background: var(--surface); border: 1px solid var(--line); border-left: 3px solid transparent; border-radius: 10px; box-shadow: 0 5px 15px rgba(0, 0, 0, .14); transition: transform .2s ease, border-color .2s ease; }
    .insight-card--revenue { border-left-color: var(--accent); }
    .insight-card--rating { border-left-color: var(--accent-blue); }
    .insight-card--activity { border-left-color: #64748b; }
    .insight-card--customer { border-left-color: #2563eb; }
    .insight-card:hover { transform: translateY(-2px); border-color: rgba(148, 163, 184, .3); }
    .insight-label { margin: 0 0 .35rem; color: var(--secondary); font-size: .72rem; font-weight: 700; text-transform: uppercase; }
    .insight-value { margin: 0; color: var(--ink); font-size: 1rem; font-weight: 700; line-height: 1.35; }
    .insight-detail { margin: .2rem 0 0; color: var(--muted); font-size: .76rem; }
    .dataset-info-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .65rem; margin: .6rem 0 1.4rem; }
    .dataset-info-card { min-width: 0; padding: .85rem .9rem; background: var(--surface); border: 1px solid var(--line); border-radius: 9px; box-shadow: 0 4px 13px rgba(0, 0, 0, .12); }
    .dataset-info-label { margin: 0 0 .3rem; color: var(--secondary); font-size: .7rem; font-weight: 700; text-transform: uppercase; }
    .dataset-info-value { overflow: hidden; margin: 0; color: var(--ink); font-size: .94rem; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
    .panel-heading { margin: .05rem 0 .1rem; color: #f8fafc; font-size: 1rem; font-weight: 700; }
    .panel-caption { margin: 0 0 .7rem; color: var(--secondary); font-size: .78rem; line-height: 1.45; }
    [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .panel-heading):has(> [data-testid="stElementContainer"] [data-testid="stPlotlyChart"]) {
        background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
        box-shadow: 0 7px 20px rgba(0, 0, 0, .18);
        animation: content-enter .55s ease-out both;
    }
    [data-testid="stPlotlyChart"] { background: #f8fafc; border-radius: 8px; overflow: hidden; }
    [data-baseweb="tab-list"] { gap: .25rem; border-bottom: 1px solid var(--line); }
    [data-baseweb="tab"] { height: 3rem; padding: 0 .95rem; color: var(--secondary); font-size: .84rem; font-weight: 650; border-radius: 8px 8px 0 0; }
    [data-baseweb="tab"]:hover { color: #fff; background: rgba(255, 255, 255, .04); }
    [data-baseweb="tab"][aria-selected="true"] { color: #fff; background: rgba(229, 9, 20, .10); border-bottom: 2px solid var(--accent); }
    [data-testid="stDataFrame"] { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; }
    [data-testid="stExpander"] { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stDateInput"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
    [data-testid="stTextArea"] textarea {
        color: #f8fafc; background: var(--surface); border-color: #354154; border-radius: 8px;
    }
    [data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder { color: #94a3b8; }
    [data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] { color: #f8fafc; background: #1a2230; border: 1px solid #344154; }
    [data-baseweb="popover"] [role="option"]:hover, [data-baseweb="menu"] [role="option"]:hover { background: #273346; }
    [data-testid="stBaseButton-primary"] { color: #fff; background: var(--accent); border: 1px solid var(--accent); border-radius: 8px; }
    [data-testid="stBaseButton-primary"]:hover { color: #fff; background: #c90812; border-color: #c90812; }
    [data-testid="stBaseButton-secondary"] { color: #f1f5f9; background: var(--elevated); border: 1px solid #354154; border-radius: 8px; }
    [data-testid="stBaseButton-secondary"]:hover { color: #fff; background: #222d3d; border-color: #526178; }
    [data-testid="stBaseButton-primary"]:focus-visible, [data-testid="stBaseButton-secondary"]:focus-visible,
    [data-baseweb="select"]:focus-within, [data-baseweb="input"]:focus-within { outline: 2px solid var(--accent-blue); outline-offset: 2px; }
    .data-summary { color: var(--secondary); font-size: .8rem; }
    @media (max-width: 850px) {
        .block-container { padding: 1.3rem 1rem 2.5rem; }
        .hero { grid-template-columns: 1fr; gap: 1.2rem; padding: 1.5rem; min-height: 260px; }
        .hero-meta { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: .7rem 1rem; }
        .hero-stat { text-align: right; white-space: nowrap; }
        .hero-period { grid-column: 1 / -1; }
        .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        .brand-lockup { grid-template-columns: 70px minmax(0, 1fr); }
        .logo-frame { width: 70px; height: 70px; }
    }
    @media (max-width: 600px) {
        .hero { min-height: 0; gap: .9rem; padding: 1rem; }
        .brand-lockup { display: flex; flex-direction: column; align-items: flex-start; gap: .65rem; }
        .hero-brand { margin-top: .25rem; font-size: 1.45rem; line-height: 1.2; }
        .hero-title { font-size: .94rem; }
        .hero-copy { max-width: none; font-size: .78rem; line-height: 1.4; }
        .hero-meta { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: .45rem .55rem; min-width: 0; }
        .dataset-status { grid-column: 1 / -1; }
        .hero-stat { text-align: left; }
        .hero-period { max-width: 100%; overflow-wrap: anywhere; white-space: normal; }
        .hero-period--dataset { grid-column: 2; }
        .hero-period--range { display: none; }
        .logo-frame { width: 54px; height: 54px; border-radius: 9px; }
        .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; }
        .kpi-card { padding: .85rem .75rem; }
        .kpi-value { font-size: 1.35rem; }
        .insight-grid { grid-template-columns: 1fr; }
        .dataset-info-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .section-row { align-items: flex-start; flex-direction: column; gap: .2rem; }
        [data-baseweb="tab"] { padding: 0 .65rem; font-size: .74rem; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.professional_theme_enabled:
    st.markdown(
        """
        <style>
        :root {
            --ink: #0f172a;
            --secondary: #475569;
            --muted: #64748b;
            --line: #e2e8f0;
            --canvas: #f8fafc;
            --surface: #ffffff;
            --elevated: #f1f5f9;
            --sidebar: #f1f5f9;
            --accent-blue: #2563eb;
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            color: var(--ink); background: var(--canvas);
        }
        [data-testid="stSidebar"] { background: var(--sidebar); border-right-color: var(--line); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label { color: var(--ink); }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: var(--secondary); }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            background: #fff; border-color: #cbd5e1;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small { color: var(--ink) !important; }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
            color: #fff !important; background: var(--accent) !important; border-color: var(--accent) !important;
        }
        .source-card { background: #fff; border-color: var(--line); }
        .source-label, .source-file, .source-count { color: var(--secondary); }
        .source-kind { color: var(--ink); }
        [data-testid="stSidebar"] [data-testid="stMultiSelect"] > div > div,
        [data-testid="stSidebar"] [data-testid="stDateInput"] > div > div,
        [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
            color: var(--ink); background: #fff; border-color: #cbd5e1;
        }
        [data-testid="stSidebar"] [data-testid="stMultiSelect"] input,
        [data-testid="stSidebar"] [data-testid="stDateInput"] input,
        [data-testid="stSidebar"] [data-testid="stSelectbox"] input { color: var(--ink); }
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseButton-secondary"] {
            color: var(--ink); background: #fff; border-color: #cbd5e1;
        }
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stBaseButton-secondary"]:hover {
            color: var(--ink); background: #f1f5f9; border-color: #94a3b8;
        }
        [data-testid="stSidebar"] [data-testid="stRadioOption"] { color: var(--secondary); }
        [data-testid="stSidebar"] [data-testid="stRadioOption"]:hover { color: var(--ink); background: #e2e8f0; }
        [data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked) {
            color: var(--ink); background: rgba(229, 9, 20, .07); border-left-color: var(--accent); font-weight: 650;
        }
        .section-title, .kpi-value, .insight-value, .dataset-info-value { color: var(--ink); }
        .section-note, .kpi-label, .dataset-info-label { color: var(--secondary); }
        .breadcrumb-current { color: var(--ink); }
        .kpi-card, .insight-card, .dataset-info-card {
            color: var(--ink); background: #fff; border-color: var(--line);
            box-shadow: 0 4px 14px rgba(15, 23, 42, .06);
        }
        .insight-card--revenue { border-left-color: var(--accent); }
        .insight-card--rating { border-left-color: var(--accent-blue); }
        .insight-card--activity { border-left-color: #64748b; }
        .insight-card--customer { border-left-color: #2563eb; }
        .kpi-card:hover, .insight-card:hover {
            border-color: #cbd5e1; box-shadow: 0 8px 20px rgba(15, 23, 42, .10);
        }
        .kpi-note, .insight-detail { color: var(--muted); }
        .panel-heading { color: var(--ink); }
        .panel-caption { color: var(--secondary); }
        [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .panel-heading):has(> [data-testid="stElementContainer"] [data-testid="stPlotlyChart"]) {
            color: var(--ink); background: #fff; border-color: var(--line);
            box-shadow: 0 5px 16px rgba(15, 23, 42, .07);
        }
        [data-testid="stPlotlyChart"] { background: #fff; }
        [data-baseweb="tab"] { color: var(--secondary); }
        [data-baseweb="tab"]:hover { color: var(--ink); background: #f1f5f9; }
        [data-baseweb="tab"][aria-selected="true"] { color: var(--accent); background: rgba(229, 9, 20, .06); }
        [data-testid="stDataFrame"], [data-testid="stExpander"] {
            color: var(--ink); background: #fff; border-color: var(--line);
        }
        [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div, [data-testid="stTextArea"] textarea {
            color: var(--ink); background: #fff; border-color: #cbd5e1;
        }
        [data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder { color: var(--muted); }
        [data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] {
            color: var(--ink); background: #fff; border-color: var(--line);
        }
        [data-baseweb="popover"] [role="option"]:hover, [data-baseweb="menu"] [role="option"]:hover { background: #f1f5f9; }
        [data-testid="stBaseButton-primary"] { color: #fff; background: var(--accent); border-color: var(--accent); }
        [data-testid="stBaseButton-primary"]:hover { color: #fff; background: #c90812; border-color: #c90812; }
        .data-summary { color: var(--secondary); }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def parse_csv(csv_bytes: bytes) -> pd.DataFrame:
    try:
        data = pd.read_csv(io.BytesIO(csv_bytes))
    except UnicodeDecodeError:
        for encoding in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                data = pd.read_csv(io.BytesIO(csv_bytes), encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise
    for column in data.columns:
        if "date" in str(column).casefold():
            parsed = pd.to_datetime(data[column], errors="coerce")
            if parsed.notna().any():
                data[column] = parsed
    return data


def load_data(csv_path: str) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(path)
    return parse_csv(path.read_bytes())


def find_date_column(data: pd.DataFrame) -> str | None:
    for preferred in ("Watch_Date", "date_added"):
        if preferred in data.columns and pd.api.types.is_datetime64_any_dtype(data[preferred]):
            return preferred
    return next(
        (column for column in data.columns if pd.api.types.is_datetime64_any_dtype(data[column])),
        None,
    )


def numeric_column(data: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(data[column], errors="coerce")


def format_value(value: float, decimals: int = 0) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.{decimals}f}"


def format_file_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:,.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:,.1f} GB"


def reset_filter_state() -> None:
    clear_filter_state()
    st.rerun()


def clear_filter_state() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith(("filter_", "explorer_")):
            st.session_state.pop(key, None)


def restore_default_dataset() -> None:
    st.session_state.pop("dataset_upload", None)
    st.session_state.pop("allow_dataset_replacement", None)
    st.session_state.pop("_active_external_dataframe", None)
    st.session_state.pop("_active_dataset_signature", None)
    st.session_state.pop("_active_dataset_kind", None)
    clear_filter_state()


def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered = data.copy()
    available_filters = [column for column in FILTER_COLUMNS if column in data.columns]
    for column in data.columns:
        if column in available_filters:
            continue
        if pd.api.types.is_object_dtype(data[column]) or pd.api.types.is_string_dtype(data[column]):
            unique_count = data[column].nunique(dropna=True)
            if 1 < unique_count <= 35:
                available_filters.append(column)

    st.sidebar.markdown("## Filters")
    st.sidebar.caption("Refine every KPI, insight, and chart.")
    if st.sidebar.button("Reset filters", width="stretch", key="reset_filters"):
        reset_filter_state()

    for column in available_filters:
        options = sorted(data[column].dropna().astype(str).unique().tolist(), key=str.casefold)
        if not options:
            continue
        selected = st.sidebar.multiselect(
            FILTER_LABELS.get(column, str(column).replace("_", " ").title()),
            options,
            key=f"filter_{column}",
            placeholder="All values",
        )
        if selected:
            filtered = filtered[filtered[column].astype("string").isin(selected)]

    if "Rating" in data.columns:
        rating_values = pd.to_numeric(data["Rating"], errors="coerce").dropna()
        if not rating_values.empty and rating_values.min() != rating_values.max():
            if pd.api.types.is_integer_dtype(data["Rating"]):
                minimum_rating, maximum_rating = int(rating_values.min()), int(rating_values.max())
                rating_step = 1
            else:
                minimum_rating, maximum_rating = float(rating_values.min()), float(rating_values.max())
                rating_step = None
            rating_range = st.sidebar.slider(
                "Rating range",
                min_value=minimum_rating,
                max_value=maximum_rating,
                value=(minimum_rating, maximum_rating),
                step=rating_step,
                key="filter_rating_range",
            )
            filtered_ratings = pd.to_numeric(filtered["Rating"], errors="coerce")
            filtered = filtered.loc[filtered_ratings.between(*rating_range)]

    date_column = find_date_column(data)
    if date_column:
        dates = pd.to_datetime(data[date_column], errors="coerce")
        valid_dates = dates.dropna()
        if not valid_dates.empty:
            minimum = valid_dates.min().date()
            maximum = valid_dates.max().date()
            selected_range = st.sidebar.date_input(
                f"{date_column.replace('_', ' ').title()} range",
                value=(minimum, maximum),
                min_value=minimum,
                max_value=maximum,
                key="filter_watch_date",
            )
            if isinstance(selected_range, tuple) and len(selected_range) == 2:
                start_date, end_date = selected_range
                filtered_dates = pd.to_datetime(filtered[date_column], errors="coerce").dt.date
                filtered = filtered.loc[filtered_dates.between(start_date, end_date)]

    st.sidebar.markdown(
        f'<div class="data-summary">Showing <strong>{len(filtered):,}</strong> of {len(data):,} records</div>',
        unsafe_allow_html=True,
    )
    return filtered


def calculate_kpis(data: pd.DataFrame) -> list[tuple[str, str, str, str]]:
    cards: list[tuple[str, str, str, str]] = [
        ("Total records", format_value(len(data)), "Rows in the current filtered view", "N")
    ]
    customers = data["Customer_ID"].nunique() if "Customer_ID" in data.columns else None
    if customers is not None:
        cards.append(("Total customers", format_value(customers), "Unique customer IDs", "ID"))

    revenue: float | None = None
    if "Monthly_Revenue" in data.columns:
        revenue_value = numeric_column(data, "Monthly_Revenue").sum(min_count=1)
        revenue = float(revenue_value) if pd.notna(revenue_value) else None
        cards.append(("Recorded revenue", format_value(revenue_value), "Sum of Monthly_Revenue", "REV"))

    if revenue is not None and customers:
        cards.append(("Revenue per customer", format_value(revenue / customers, 2), "Recorded revenue / unique customers", "AVG"))
    if "Rating" in data.columns:
        average_rating = numeric_column(data, "Rating").mean()
        cards.append(("Average rating", format_value(average_rating, 2), "Mean score out of 5", "R"))
    if "Watch_Count" in data.columns:
        cards.append(("Watch count", format_value(numeric_column(data, "Watch_Count").sum(min_count=1)), "Total recorded plays", "PLAY"))
    if "Watch_Time_Minutes" in data.columns:
        minutes = numeric_column(data, "Watch_Time_Minutes").sum(min_count=1)
        cards.append(("Watch time", f"{format_value(minutes)} min", f"{format_value(minutes / 60, 1)} hours total", "MIN"))
    return cards


def create_monthly_revenue(data: pd.DataFrame) -> go.Figure | None:
    date_column = find_date_column(data)
    if "Monthly_Revenue" not in data.columns or date_column is None:
        return None
    dates = pd.to_datetime(data[date_column], errors="coerce")
    revenue = numeric_column(data, "Monthly_Revenue")
    valid = dates.notna() & revenue.notna()
    if not valid.any():
        return None
    chart_data = pd.DataFrame({"Month": dates.loc[valid].dt.to_period("M").dt.to_timestamp(), "Revenue": revenue.loc[valid]})
    chart_data = chart_data.groupby("Month", as_index=False)["Revenue"].sum().sort_values("Month")
    figure = px.line(chart_data, x="Month", y="Revenue", markers=True)
    figure.update_traces(line={"color": ACCENT, "width": 3}, marker={"size": 7}, hovertemplate="%{x|%b %Y}<br>Revenue: %{y:,.0f}<extra></extra>")
    figure.update_xaxes(tickformat="%b %Y", dtick="M1")
    return polish_chart(figure, height=330)


def create_bar_chart(data: pd.DataFrame, dimension: str, metric: str, title: str, *, limit: int = 12, color: str = ACCENT) -> go.Figure | None:
    if not {dimension, metric}.issubset(data.columns):
        return None
    values = numeric_column(data, metric)
    summary = values.groupby(data[dimension]).sum(min_count=1).dropna().sort_values(ascending=False).head(limit)
    if summary.empty:
        return None
    chart_data = summary.rename(metric).rename_axis(dimension).reset_index().sort_values(metric)
    figure = px.bar(chart_data, x=metric, y=dimension, orientation="h", text_auto=".2s", color_discrete_sequence=[color])
    figure.update_traces(hovertemplate=f"%{{y}}<br>{metric.replace('_', ' ')}: %{{x:,.0f}}<extra></extra>", marker_line_width=0)
    figure.update_layout(title=None, yaxis={"categoryorder": "total ascending"})
    return polish_chart(figure, height=max(285, min(410, 160 + len(chart_data) * 25)))


def create_revenue_charts(data: pd.DataFrame) -> dict[str, go.Figure]:
    charts: dict[str, go.Figure] = {}
    if "Monthly_Revenue" not in data.columns:
        return charts
    for dimension in ("Region", "Subscription_Plan", "Title"):
        figure = create_bar_chart(data, dimension, "Monthly_Revenue", dimension, limit=10)
        if figure is not None:
            charts[dimension] = figure
    revenue = numeric_column(data, "Monthly_Revenue").dropna()
    if not revenue.empty:
        distribution = pd.DataFrame({"Revenue per record": revenue})
        unique_values = distribution["Revenue per record"].nunique()
        figure = px.histogram(distribution, x="Revenue per record", nbins=min(12, max(5, unique_values)), color_discrete_sequence=["#536B82"])
        figure.update_traces(hovertemplate="Revenue: %{x:,.0f}<br>Records: %{y}<extra></extra>", marker_line_width=0)
        charts["Distribution"] = polish_chart(figure, height=315)
    monthly = create_monthly_revenue(data)
    if monthly is not None:
        charts["Month"] = monthly
    return charts


def create_rating_charts(data: pd.DataFrame) -> dict[str, go.Figure]:
    charts: dict[str, go.Figure] = {}
    if "Rating" not in data.columns:
        return charts
    ratings = numeric_column(data, "Rating")
    for dimension in ("Subscription_Plan", "Category"):
        if dimension not in data.columns:
            continue
        summary = ratings.groupby(data[dimension]).mean().dropna().sort_values(ascending=False)
        if summary.empty:
            continue
        chart_data = summary.rename("Average rating").rename_axis(dimension).reset_index().sort_values("Average rating")
        figure = px.bar(chart_data, x="Average rating", y=dimension, orientation="h", text_auto=".2f", color_discrete_sequence=[ACCENT])
        figure.update_traces(hovertemplate="%{y}<br>Average rating: %{x:.2f} / 5<extra></extra>", marker_line_width=0)
        charts[dimension] = polish_chart(figure, height=max(285, min(410, 160 + len(chart_data) * 25)))

    if "Type" in data.columns:
        by_type = ratings.groupby(data["Type"]).mean().dropna().sort_values(ascending=False)
        if not by_type.empty:
            chart_data = by_type.rename("Average rating").rename_axis("Type").reset_index()
            figure = px.bar(chart_data, x="Type", y="Average rating", text_auto=".2f", color_discrete_sequence=["#536B82"])
            figure.update_traces(hovertemplate="%{x}<br>Average rating: %{y:.2f} / 5<extra></extra>", marker_line_width=0)
            charts["Type"] = polish_chart(figure, height=315)

    distribution = ratings.dropna().value_counts().sort_index().rename_axis("Rating").rename("Records").reset_index()
    if not distribution.empty:
        figure = px.bar(distribution, x="Rating", y="Records", text="Records", color_discrete_sequence=["#536B82"])
        figure.update_traces(hovertemplate="Rating: %{x}<br>Records: %{y}<extra></extra>", marker_line_width=0)
        figure.update_xaxes(dtick=1)
        charts["Distribution"] = polish_chart(figure, height=315)
    return charts


def create_viewing_charts(data: pd.DataFrame) -> dict[str, go.Figure]:
    charts: dict[str, go.Figure] = {}
    for dimension, metric in (
        ("Category", "Watch_Count"),
        ("Device", "Watch_Time_Minutes"),
        ("Language", "Watch_Count"),
        ("Type", "Watch_Count"),
        ("Region", "Watch_Count"),
        ("Subscription_Plan", "Watch_Count"),
    ):
        figure = create_bar_chart(data, dimension, metric, dimension, limit=10, color="#536B82")
        if figure is not None:
            charts[dimension] = figure
    return charts


def create_subscription_mix(data: pd.DataFrame) -> go.Figure | None:
    if "Subscription_Plan" not in data.columns:
        return None
    if "Customer_ID" in data.columns:
        counts = data.groupby("Subscription_Plan")["Customer_ID"].nunique()
    else:
        counts = data["Subscription_Plan"].value_counts()
    mix = counts.rename_axis("Subscription plan").rename("Customers").reset_index()
    if mix.empty:
        return None
    figure = px.pie(mix, names="Subscription plan", values="Customers", hole=.72, color_discrete_sequence=[ACCENT, "#536B82", "#9DAAB7"])
    figure.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{value} customers (%{percent})<extra></extra>", marker={"line": {"color": "white", "width": 3}})
    figure.update_layout(showlegend=True, legend={"orientation": "h", "y": -.08, "x": .5, "xanchor": "center"})
    return polish_chart(figure, height=330)


def create_customer_analysis(data: pd.DataFrame) -> dict[str, go.Figure]:
    charts: dict[str, go.Figure] = {}
    if "Customer_ID" not in data.columns:
        return charts
    for dimension in ("Region", "Subscription_Plan"):
        if dimension not in data.columns:
            continue
        counts = data.groupby(dimension)["Customer_ID"].nunique().sort_values(ascending=False)
        chart_data = counts.rename("Customers").rename_axis(dimension).reset_index()
        figure = px.bar(chart_data.sort_values("Customers"), x="Customers", y=dimension, orientation="h", text="Customers", color_discrete_sequence=["#536B82"])
        figure.update_traces(hovertemplate="%{y}<br>Unique customers: %{x}<extra></extra>", marker_line_width=0)
        charts[dimension] = polish_chart(figure, height=max(285, min(410, 160 + len(chart_data) * 25)))

    if "Monthly_Revenue" in data.columns:
        group_columns = ["Customer_ID"]
        if "Customer_Name" in data.columns:
            group_columns.append("Customer_Name")
        top_customers = data.assign(_revenue=numeric_column(data, "Monthly_Revenue")).groupby(group_columns, dropna=False)["_revenue"].sum().nlargest(10).sort_values()
        if not top_customers.empty:
            labels = [str(index[-1] if isinstance(index, tuple) else index) for index in top_customers.index]
            chart_data = pd.DataFrame({"Customer": labels, "Recorded revenue": top_customers.values})
            figure = px.bar(chart_data, x="Recorded revenue", y="Customer", orientation="h", text_auto=".2s", color_discrete_sequence=[ACCENT])
            figure.update_traces(hovertemplate="%{y}<br>Recorded revenue: %{x:,.0f}<extra></extra>", marker_line_width=0)
            charts["Top customers"] = polish_chart(figure, height=350)
    return charts


def create_content_mix(data: pd.DataFrame) -> go.Figure | None:
    if "Type" not in data.columns:
        return None
    mix = data["Type"].dropna().value_counts().rename_axis("Content type").rename("Records").reset_index()
    if mix.empty:
        return None
    figure = px.pie(mix, names="Content type", values="Records", hole=.72, color_discrete_sequence=[ACCENT, "#536B82", "#9DAAB7"])
    figure.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{value} records (%{percent})<extra></extra>", marker={"line": {"color": "white", "width": 3}})
    figure.update_layout(showlegend=True, legend={"orientation": "h", "y": -.08, "x": .5, "xanchor": "center"})
    return polish_chart(figure, height=330)


def polish_chart(figure: go.Figure, *, height: int = 330) -> go.Figure:
    figure.update_layout(
        template="plotly_white",
        height=height,
        margin={"l": 8, "r": 16, "t": 14, "b": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Aptos, Segoe UI, sans-serif", "size": 11, "color": INK},
        colorway=PALETTE,
        hoverlabel={"bgcolor": "#172231", "font": {"color": "white", "size": 12}},
        uniformtext_minsize=9,
        uniformtext_mode="hide",
    )
    figure.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont={"color": MUTED})
    figure.update_yaxes(showgrid=False, zeroline=False, linecolor=GRID, tickfont={"color": MUTED})
    return figure


def generate_insights(data: pd.DataFrame) -> list[tuple[str, str, str]]:
    insights: list[tuple[str, str, str]] = []
    if {"Region", "Monthly_Revenue"}.issubset(data.columns):
        by_region = numeric_column(data, "Monthly_Revenue").groupby(data["Region"]).sum().dropna()
        if not by_region.empty:
            insights.append(("Revenue leader", str(by_region.idxmax()), f"{format_value(by_region.max())} recorded revenue"))
    if {"Category", "Rating"}.issubset(data.columns):
        by_category = numeric_column(data, "Rating").groupby(data["Category"]).mean().dropna()
        if not by_category.empty:
            insights.append(("Highest-rated category", str(by_category.idxmax()), f"{by_category.max():.2f} average rating"))
    if "Subscription_Plan" in data.columns:
        if "Customer_ID" in data.columns:
            plans = data.groupby("Subscription_Plan")["Customer_ID"].nunique().sort_values(ascending=False)
        else:
            plans = data["Subscription_Plan"].dropna().value_counts()
        if not plans.empty:
            insights.append(("Most common plan", str(plans.idxmax()), f"{format_value(plans.max())} customer records"))
    if {"Type", "Watch_Count"}.issubset(data.columns):
        by_type = numeric_column(data, "Watch_Count").groupby(data["Type"]).sum().dropna()
        if not by_type.empty:
            insights.append(("Most watched format", str(by_type.idxmax()), f"{format_value(by_type.max())} recorded plays"))
    if {"Device", "Watch_Count"}.issubset(data.columns):
        by_device = numeric_column(data, "Watch_Count").groupby(data["Device"]).sum().dropna()
        if not by_device.empty:
            insights.append(("Most active device", str(by_device.idxmax()), f"{format_value(by_device.max())} recorded plays"))
    if "Watch_Time_Minutes" in data.columns:
        minutes = numeric_column(data, "Watch_Time_Minutes").sum(min_count=1)
        if pd.notna(minutes):
            insights.append(("Total viewing time", f"{format_value(minutes / 60, 1)} hours", f"{format_value(minutes)} minutes recorded"))
    date_column = find_date_column(data)
    if date_column and "Monthly_Revenue" in data.columns:
        dates = pd.to_datetime(data[date_column], errors="coerce")
        revenue = numeric_column(data, "Monthly_Revenue")
        valid = dates.notna() & revenue.notna()
        if valid.any():
            by_month = revenue.loc[valid].groupby(dates.loc[valid].dt.to_period("M")).sum()
            if not by_month.empty:
                peak_month = by_month.idxmax().strftime("%b %Y")
                insights.append(("Peak revenue month", peak_month, f"{format_value(by_month.max())} recorded revenue"))
    return insights


def render_section(title: str, note: str) -> None:
    st.markdown(
        f'<div class="section-row"><h2 class="section-title">{html.escape(title)}</h2><p class="section-note">{html.escape(note)}</p></div>',
        unsafe_allow_html=True,
    )


def render_chart(title: str, caption: str, figure: go.Figure | None) -> None:
    if figure is None:
        return
    with st.container(border=True):
        st.markdown(
            f'<div class="panel-heading">{html.escape(title)}</div><div class="panel-caption">{html.escape(caption)}</div>',
            unsafe_allow_html=True,
        )
        chart_key = re.sub(r"[^a-z0-9]+", "_", f"{title}_{caption}".casefold()).strip("_")
        st.plotly_chart(figure, width="stretch", config={"displaylogo": False, "responsive": True}, key=f"chart_{chart_key}")


def render_hero(data: pd.DataFrame, dataset_name: str, source_kind: str) -> None:
    date_column = find_date_column(data)
    if date_column:
        dates = pd.to_datetime(data[date_column], errors="coerce").dropna()
    else:
        dates = pd.Series(dtype="datetime64[ns]")
    if dates.empty:
        period = "Date range unavailable"
    else:
        period = f"{dates.min():%b %Y} to {dates.max():%b %Y}"
    video_markup = ""
    if BACKGROUND_VIDEO_URI:
        video_markup = (
            f'<video class="hero-video" src="{BACKGROUND_VIDEO_URI}" '
            'autoplay="autoplay" muted="muted" loop="loop" playsinline="playsinline" preload="metadata" '
            'disablepictureinpicture aria-hidden="true" tabindex="-1"></video>'
        )
        logo_markup = ""
        if LOGO_IMAGE_URI:
                logo_markup = (
                        f'<div class="logo-frame"><img class="netflix-logo" src="{LOGO_IMAGE_URI}" '
                        'alt="Netflix logo"></div>'
                )
    hero = f"""
    <section class="hero">
            {video_markup}
            <div class="brand-lockup">
                {logo_markup}
                <div>
                    <div class="hero-kicker"><span class="hero-kicker-mark"></span> DATA ANALYTICS</div>
                    <div class="hero-brand">Netflix Data Analysis</div>
                    <div class="hero-title">Advanced Data Analytics Dashboard</div>
                    <p class="hero-copy">Explore revenue, customer behavior, audience ratings, and viewing patterns through interactive analytics.</p>
                </div>
      </div>
      <div class="hero-meta">
                <div class="dataset-status"><span class="dataset-status-dot"></span> {html.escape(source_kind)}</div>
                <div class="hero-stat">{len(data):,}<span>Records · {len(data.columns):,} columns</span></div>
                <div class="hero-period hero-period--dataset">{html.escape(dataset_name)}</div>
                <div class="hero-period hero-period--range">{html.escape(period)}</div>
      </div>
    </section>
    """
    st.markdown(hero, unsafe_allow_html=True)
    if BACKGROUND_VIDEO_URI:
        st.html(
            """
            <script>
            document.querySelectorAll("video.hero-video").forEach((video) => {
                video.defaultMuted = true;
                video.muted = true;
                video.volume = 0;
                video.play().catch(() => {});
            });
            </script>
            """,
            unsafe_allow_javascript=True,
        )


def render_kpis(data: pd.DataFrame) -> None:
    cards = calculate_kpis(data)
    if not cards:
        return
    card_html = []
    for label, value, note, mark in cards:
        card_html.append(
            f'<div class="kpi-card"><div class="kpi-top"><span class="kpi-label">{html.escape(label)}</span><span class="kpi-mark">{html.escape(mark)}</span></div><div class="kpi-value">{html.escape(value)}</div><div class="kpi-note">{html.escape(note)}</div></div>'
        )
    st.markdown(f'<section class="kpi-grid">{"".join(card_html)}</section>', unsafe_allow_html=True)


def render_insights(data: pd.DataFrame) -> None:
    insights = generate_insights(data)[:4]
    if not insights:
        return
    render_section("Key insights", "Calculated from the currently filtered records")
    cards = []
    for label, value, detail in insights:
        if "revenue" in label.casefold() or "month" in label.casefold():
            insight_type = "revenue"
        elif "rating" in label.casefold() or "category" in label.casefold():
            insight_type = "rating"
        elif "watch" in label.casefold() or "device" in label.casefold() or "viewing" in label.casefold():
            insight_type = "activity"
        else:
            insight_type = "customer"
        cards.append(
            f'<div class="insight-card insight-card--{insight_type}"><p class="insight-label">{html.escape(label)}</p><p class="insight-value">{html.escape(value)}</p><p class="insight-detail">{html.escape(detail)}</p></div>'
        )
    st.markdown(f'<section class="insight-grid">{"".join(cards)}</section>', unsafe_allow_html=True)


def render_dataset_info(data: pd.DataFrame, dataset_name: str) -> None:
    date_column = find_date_column(data)
    if date_column:
        dates = pd.to_datetime(data[date_column], errors="coerce").dropna()
    else:
        dates = pd.Series(dtype="datetime64[ns]")
    date_range = f"{dates.min():%b %d, %Y} - {dates.max():%b %d, %Y}" if not dates.empty else "Unavailable"
    last_date = f"{dates.max():%b %d, %Y}" if not dates.empty else "Unavailable"
    values = [
        ("Dataset", dataset_name),
        ("Total records", format_value(len(data))),
        ("Total columns", format_value(len(data.columns))),
        ("Date range", date_range),
        ("Missing values", format_value(data.isna().sum().sum())),
        ("Latest watch date", last_date),
    ]
    if "Region" in data.columns:
        values.append(("Regions", format_value(data["Region"].nunique(dropna=True))))
    if "Subscription_Plan" in data.columns:
        values.append(("Subscription plans", format_value(data["Subscription_Plan"].nunique(dropna=True))))
    cards = "".join(
        f'<div class="dataset-info-card"><p class="dataset-info-label">{html.escape(label)}</p><p class="dataset-info-value">{html.escape(value)}</p></div>'
        for label, value in values
    )
    st.markdown(f'<section class="dataset-info-grid">{cards}</section>', unsafe_allow_html=True)


def render_data_explorer(data: pd.DataFrame, complete_data: pd.DataFrame) -> None:
    render_section("Data Explorer", "Browse and analyze the complete filtered dataset")
    search = st.text_input(
        "Search records",
        placeholder="Search customer, title, region, or any field",
        label_visibility="collapsed",
        key="explorer_search",
    )
    result = data.copy()
    with st.expander("Filter by column", expanded=False):
        selected_columns = st.multiselect(
            "Choose one or more dataset columns",
            options=data.columns.tolist(),
            key="explorer_columns",
            placeholder="Select columns to filter",
        )
        for column in selected_columns:
            series = complete_data[column]
            if pd.api.types.is_datetime64_any_dtype(series):
                valid_dates = pd.to_datetime(series, errors="coerce").dropna()
                if valid_dates.empty:
                    continue
                selected_range = st.date_input(
                    f"{column} range",
                    value=(valid_dates.min().date(), valid_dates.max().date()),
                    min_value=valid_dates.min().date(),
                    max_value=valid_dates.max().date(),
                    key=f"explorer_date_{column}",
                )
                if isinstance(selected_range, tuple) and len(selected_range) == 2:
                    start, end = selected_range
                    date_values = pd.to_datetime(result[column], errors="coerce").dt.date
                    result = result.loc[date_values.between(start, end)]
            elif pd.api.types.is_numeric_dtype(series):
                values = pd.to_numeric(series, errors="coerce").dropna()
                if values.empty or values.min() == values.max():
                    continue
                if pd.api.types.is_integer_dtype(series):
                    lower, upper = int(values.min()), int(values.max())
                    selected_range = st.slider(column.replace("_", " "), lower, upper, (lower, upper), key=f"explorer_range_{column}")
                else:
                    lower, upper = float(values.min()), float(values.max())
                    selected_range = st.slider(column.replace("_", " "), lower, upper, (lower, upper), key=f"explorer_range_{column}")
                numeric_values = pd.to_numeric(result[column], errors="coerce")
                result = result.loc[numeric_values.between(*selected_range)]
            else:
                options = sorted(series.dropna().astype(str).unique().tolist(), key=str.casefold)
                if len(options) <= 40:
                    selected_values = st.multiselect(
                        f"{column.replace('_', ' ')} values",
                        options,
                        key=f"explorer_values_{column}",
                        placeholder="All values",
                    )
                    if selected_values:
                        result = result[result[column].astype("string").isin(selected_values)]
                else:
                    text_filter = st.text_input(f"{column.replace('_', ' ')} contains", key=f"explorer_text_{column}")
                    if text_filter.strip():
                        result = result[result[column].astype("string").str.contains(text_filter.strip(), case=False, na=False, regex=False)]

    if search.strip():
        searchable = result.astype("string")
        matches = searchable.apply(lambda column: column.str.contains(search.strip(), case=False, na=False, regex=False))
        result = result.loc[matches.any(axis=1)]

    st.caption(f"Showing {len(result):,} filtered records")
    column_config: dict[str, object] = {}
    if "Watch_Date" in result.columns:
        column_config["Watch_Date"] = st.column_config.DateColumn("Watch date", format="MMM D, YYYY")
    if "Monthly_Revenue" in result.columns:
        column_config["Monthly_Revenue"] = st.column_config.NumberColumn("Monthly revenue", format="%.2f")
    if "Rating" in result.columns:
        column_config["Rating"] = st.column_config.NumberColumn("Rating", format="%.1f")
    if "Watch_Time_Minutes" in result.columns:
        column_config["Watch_Time_Minutes"] = st.column_config.NumberColumn("Watch time (min)", format="%d")
    if "Watch_Count" in result.columns:
        column_config["Watch_Count"] = st.column_config.NumberColumn("Watch count", format="%d")

    st.dataframe(result, width="stretch", hide_index=True, height=540, column_config=column_config)
    render_section("Export data", "Download the currently filtered dataset or the complete source file")
    full_download, filtered_download = st.columns(2)
    with full_download:
        st.download_button(
            "Download complete CSV",
            data=complete_data.to_csv(index=False).encode("utf-8"),
            file_name="netflix_complete.csv",
            mime="text/csv",
            width="stretch",
        )
    with filtered_download:
        st.download_button(
            "Download filtered CSV",
            data=result.to_csv(index=False).encode("utf-8"),
            file_name="netflix_filtered.csv",
            mime="text/csv",
            width="stretch",
        )


def main() -> None:
    with st.sidebar:
        st.markdown("# Netflix Insights")
        st.caption("ANALYTICS WORKSPACE")
        st.markdown("### Navigation")
        active_page = st.radio(
            "Dashboard section",
            [
                "Overview",
                "Revenue Analytics",
                "Content & Ratings",
                "Viewing Behavior",
                "Customer Insights",
                "Data Explorer",
            ],
            key="dashboard_navigation",
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("### Appearance")
        theme_enabled = st.toggle(
            "Professional Theme",
            key="professional_theme_enabled",
            help="Switch between premium dark and clean light appearance.",
            width="stretch",
        )
        st.caption("Dark premium interface" if theme_enabled else "Clean light interface")
        st.divider()
        st.markdown("### Dataset")
        active_external_dataset = st.session_state.get("_active_dataset_kind") == "external"
        allow_replacement = True
        if active_external_dataset:
            allow_replacement = st.checkbox(
                "Allow dataset replacement",
                key="allow_dataset_replacement",
                help="Enable before selecting another CSV. The selected file becomes active for this session.",
            )
            st.caption("A new upload replaces the active external dataset.")
        st.caption("Upload a CSV file to analyze your own data.")
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=["csv"],
            key="dataset_upload",
            help="CSV files up to 500 MB are supported.",
            disabled=active_external_dataset and not allow_replacement,
        )
        st.caption("Maximum size: 500 MB  ·  Supported format: CSV")

    if uploaded_file is not None:
        if uploaded_file.size > 500 * 1024 * 1024:
            st.sidebar.error("File too large. The maximum supported size is 500 MB.")
            if DATA_PATH.is_file():
                st.sidebar.button("Use Default Dataset", width="stretch", key="restore_after_upload_error", on_click=restore_default_dataset)
            st.stop()
        dataset_name = Path(uploaded_file.name).name
        source_kind = "External dataset"
        source_signature = f"uploaded:{uploaded_file.file_id}:{dataset_name}:{uploaded_file.size}"
        if (
            st.session_state.get("_active_dataset_signature") == source_signature
            and "_active_external_dataframe" in st.session_state
        ):
            data = st.session_state["_active_external_dataframe"]
        else:
            csv_bytes = uploaded_file.getvalue()
            st.session_state.pop("_active_external_dataframe", None)
            try:
                with st.spinner("Importing dataset..."):
                    data = parse_csv(csv_bytes)
            except pd.errors.EmptyDataError:
                st.sidebar.error("Empty dataset. This CSV does not contain usable records.")
                if DATA_PATH.is_file():
                    st.sidebar.button("Use Default Dataset", width="stretch", key="restore_after_upload_error", on_click=restore_default_dataset)
                st.stop()
            except (OSError, pd.errors.ParserError, UnicodeDecodeError, ValueError):
                st.sidebar.error("Unable to read dataset. Check the CSV file and try again.")
                if DATA_PATH.is_file():
                    st.sidebar.button("Use Default Dataset", width="stretch", key="restore_after_upload_error", on_click=restore_default_dataset)
                st.stop()
            st.session_state["_active_external_dataframe"] = data
        file_size_bytes = uploaded_file.size
    else:
        dataset_name = DATA_PATH.name
        source_kind = "Default dataset"
        if not DATA_PATH.exists():
            st.error("Netflix.csv is missing and no CSV upload is selected.")
            st.info(f"Place Netflix.csv beside app.py at: {DATA_PATH}")
            st.stop()
        stat = DATA_PATH.stat()
        source_signature = f"local:{DATA_PATH.resolve()}:{stat.st_mtime_ns}:{stat.st_size}"
        try:
            data = load_data(str(DATA_PATH))
        except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError, ValueError):
            st.error("Netflix.csv could not be read. Check that the file is a valid, non-empty CSV.")
            st.stop()
        file_size_bytes = stat.st_size

    if st.session_state.get("_active_dataset_signature") != source_signature:
        clear_filter_state()
        st.session_state["_active_dataset_signature"] = source_signature
    st.session_state["_active_dataset_kind"] = "external" if uploaded_file is not None else "default"

    with st.sidebar:
        st.markdown(
            f'<section class="source-card"><p class="source-label">ACTIVE DATASET</p><div class="source-kind"><span class="dataset-status-dot"></span>{html.escape(source_kind)}</div><p class="source-file">{html.escape(dataset_name)}</p><p class="source-count">{len(data):,} records &nbsp;·&nbsp; {len(data.columns):,} columns</p><p class="source-size">File size: {format_file_size(file_size_bytes)}</p></section>',
            unsafe_allow_html=True,
        )
        if uploaded_file is not None:
            st.caption("Dataset imported successfully · active for this session")
            st.button("Use Default Dataset", width="stretch", key="use_default_dataset", on_click=restore_default_dataset)

    if data.empty:
        st.warning("The selected CSV contains no data rows.")
        st.stop()

    filtered = apply_filters(data)
    render_hero(data, dataset_name, source_kind)
    render_section("Portfolio overview", "Live metrics update with every filter")
    render_kpis(filtered)

    if filtered.empty:
        st.info("No data available for the selected filters.")
        st.button("Reset all filters", key="reset_empty_filters", on_click=reset_filter_state)
        st.stop()

    render_insights(filtered)
    st.markdown(
        f'<div class="breadcrumb"><span>Netflix Insights</span><span>/</span><span class="breadcrumb-current">{html.escape(active_page)}</span></div>',
        unsafe_allow_html=True,
    )

    revenue_charts = create_revenue_charts(filtered)
    rating_charts = create_rating_charts(filtered)
    viewing_charts = create_viewing_charts(filtered)
    customer_charts = create_customer_analysis(filtered)

    if active_page == "Overview":
        render_section("Performance at a glance", "Revenue performance and audience mix")
        first, second = st.columns(2, gap="large")
        with first:
            render_chart("Revenue by region", "Recorded Monthly_Revenue, grouped by region", revenue_charts.get("Region"))
        with second:
            render_chart("Monthly revenue trend", "Monthly_Revenue grouped by the month of Watch_Date", revenue_charts.get("Month"))
        content_mix = create_content_mix(filtered)
        plan_mix = create_subscription_mix(filtered)
        first, second = st.columns(2, gap="large")
        with first:
            render_chart("Content format mix", "Share of filtered customer records by content type", content_mix)
        with second:
            render_chart("Subscription distribution", "Unique customers across subscription plans", plan_mix)
        first, second = st.columns(2, gap="large")
        with first:
            render_chart("Average rating by category", "Mean Rating across content categories", rating_charts.get("Category"))
        with second:
            render_chart("Viewing activity by content type", "Total Watch_Count by content format", viewing_charts.get("Type"))
        render_section("Dataset information", "Source file and data quality at a glance")
        render_dataset_info(data, dataset_name)

    elif active_page == "Revenue Analytics":
        render_section("Revenue analytics", "Recorded Monthly_Revenue across the filtered dataset")
        first, second = st.columns(2, gap="large")
        with first:
            render_chart("Revenue by region", "Sum of Monthly_Revenue by region", revenue_charts.get("Region"))
        with second:
            render_chart("Monthly revenue trend", "Monthly revenue grouped by Watch_Date month", revenue_charts.get("Month"))
        first, second = st.columns(2, gap="large")
        with first:
            render_chart("Revenue by subscription plan", "Sum of Monthly_Revenue by plan", revenue_charts.get("Subscription_Plan"))
        with second:
            render_chart("Top titles by recorded revenue", "Highest contributing titles in the filtered records", revenue_charts.get("Title"))
        render_chart("Revenue distribution", "Distribution of per-record Monthly_Revenue values", revenue_charts.get("Distribution"))

    elif active_page == "Content & Ratings":
        render_section("Ratings and content", "Average scores and the distribution of submitted ratings")
        first, second = st.columns(2, gap="large")
        with first:
            render_chart("Average rating by subscription", "Mean Rating for each subscription plan", rating_charts.get("Subscription_Plan"))
        with second:
            render_chart("Average rating by category", "Mean Rating for each content category", rating_charts.get("Category"))
        first, second = st.columns(2, gap="large")
        with first:
            render_chart("Average rating by content type", "Mean Rating by Movie or TV Show", rating_charts.get("Type"))
        with second:
            render_chart("Rating distribution", "Number of filtered records at each rating value", rating_charts.get("Distribution"))

    elif active_page == "Viewing Behavior":
        render_section("Viewing behavior", "Playback activity across content, devices, regions, and plans")
        viewing_panels = (
            ("Category", "Watch count by category", "Sum of Watch_Count by category"),
            ("Device", "Viewing time by device", "Sum of Watch_Time_Minutes by device"),
            ("Language", "Watch count by language", "Top languages by recorded Watch_Count"),
            ("Type", "Watch count by content type", "Total plays by Movie or TV Show"),
            ("Region", "Regional viewing activity", "Total Watch_Count by region"),
            ("Subscription_Plan", "Viewing activity by plan", "Total Watch_Count by subscription plan"),
        )
        for start in range(0, len(viewing_panels), 2):
            columns = st.columns(2, gap="large")
            for offset, (key, title, caption) in enumerate(viewing_panels[start : start + 2]):
                with columns[offset]:
                    render_chart(title, caption, viewing_charts.get(key))

    elif active_page == "Customer Insights":
        render_section("Customer insights", "Customer distribution and recorded revenue contribution")
        first, second = st.columns(2, gap="large")
        with first:
            render_chart("Customers by region", "Unique Customer_ID values by region", customer_charts.get("Region"))
        with second:
            render_chart("Customers by subscription", "Unique customers by subscription plan", customer_charts.get("Subscription_Plan"))
        render_chart("Top customers by recorded revenue", "Monthly_Revenue grouped by customer ID", customer_charts.get("Top customers"))

    elif active_page == "Data Explorer":
        render_data_explorer(filtered, data)


if __name__ == "__main__":
    main()