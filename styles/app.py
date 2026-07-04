from __future__ import annotations

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cas-green: #1b5936;
            --cas-green-dark: #103b25;
            --cas-green-soft: #e7f3e7;
            --cas-green-hover: #d9ecd9;
            --cas-green-border: #b9d8b9;
            --cas-page: #f7f3ea;
            --cas-card: rgba(255,255,255,.82);
        }

        *, *::before, *::after { box-sizing:border-box; }
        html, body, [class*="css"] { font-family:"Inter","Segoe UI",Arial,sans-serif; }
        .stApp { background:var(--cas-page); color:var(--cas-green-dark); }
        #MainMenu, footer { visibility:hidden; }
        header[data-testid="stHeader"] { background:transparent; }
        .block-container { max-width:1320px; padding-top:2.75rem; padding-bottom:1rem; }

        section[data-testid="stSidebar"] {
            background:linear-gradient(180deg, #fbf7ef 0%, #f0eadf 65%, #eaf3e8 100%);
            border-right:1px solid rgba(16,59,37,.08);
        }
        section[data-testid="stSidebar"] > div { padding-top:1rem; }
        .brand-box { display:flex; align-items:center; gap:12px; padding:12px 10px 22px; }
        .brand-logo {
            width:44px; height:44px; border-radius:12px; background:var(--cas-green);
            color:white; display:grid; place-items:center; font-size:.78rem; font-weight:800;
        }
        .brand-title { font-size:1.35rem; font-weight:800; letter-spacing:.08em; color:#1a4d33; }
        .brand-subtitle { margin-top:3px; font-size:.78rem; letter-spacing:.14em; color:rgba(26,77,51,.75); }
        div[data-testid="stSidebar"] .stButton > button {
            width:100%; border-radius:12px; border:1px solid rgba(46,125,74,.12);
            background:rgba(255,255,255,.9); color:#2b5f3a; padding:.72rem .9rem;
            text-align:left; font-weight:700;
        }
        div[data-testid="stSidebar"] .stButton > button:hover,
        .nav-active button {
            background:var(--cas-green-soft) !important;
            border-color:var(--cas-green-border) !important;
            color:var(--cas-green-dark) !important;
        }

        .glass-card, .soft-card {
            border-radius:14px; padding:1.1rem; box-shadow:0 10px 24px rgba(57,57,57,.06);
            border:1px solid rgba(21,79,49,.09);
        }
        .glass-card { background:rgba(255,255,255,.74); }
        .soft-card { background:rgba(233,240,228,.82); }
        .stat-title { font-size:1.02rem; font-weight:800; color:#194833; margin-bottom:.45rem; }
        .stat-meta, .tiny { color:rgba(24,63,43,.76); }
        .tiny { font-size:.84rem; }

        .greeting h1 { margin:0; font-size:2rem; line-height:1.15; color:#14432b; }
        .greeting p { margin:.25rem 0 0; color:rgba(20,67,43,.76); font-size:1rem; }
        .progress-head, .progress-meta {
            display:flex; align-items:center; justify-content:space-between; gap:1rem;
        }
        .progress-track {
            height:12px; margin:.9rem 0 .5rem; background:#e7eadf;
            border-radius:999px; overflow:hidden;
        }
        .progress-fill { height:100%; background:linear-gradient(90deg, #1d5a39 0%, #134228 100%); }
        .progress-number { font-weight:800; color:#18402a; }
        .support-link {
            width:100%; border:0; border-radius:12px; padding:.8rem .9rem;
            background:white; color:#134228; font-weight:800; cursor:pointer;
            box-shadow:0 8px 18px rgba(0,0,0,.05);
        }

        .st-key-auth_shell {
            width:min(100%, 560px) !important;
            max-width:560px !important;
            margin:0 auto !important;
            padding:0 .25rem !important;
        }
        .auth-brand { display:flex; align-items:center; gap:.8rem; margin:.1rem 0 .35rem; }
        .auth-logo {
            width:44px; height:44px; border-radius:12px; background:var(--cas-green);
            color:white; display:grid; place-items:center; font-size:.82rem; font-weight:800;
        }
        .auth-title { color:var(--cas-green-dark); font-size:1.05rem; font-weight:800; line-height:1.2; }
        .auth-subtitle { color:rgba(16,59,37,.62); font-size:.82rem; margin-top:.1rem; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background:rgba(255,255,255,.68) !important;
            border:1px solid rgba(21,79,49,.14) !important;
            border-radius:14px !important;
            box-shadow:0 12px 30px rgba(16,59,37,.06) !important;
        }
        [data-testid="stTextInput"] label,
        [data-testid="stTextInput"] label p {
            color:var(--cas-green-dark) !important;
            font-weight:700 !important;
        }
        [data-testid="stTextInput"] [data-baseweb="input"] {
            background:#fffdf8 !important;
            border:1px solid rgba(21,79,49,.28) !important;
            border-radius:10px !important;
            min-height:42px !important;
            box-shadow:none !important;
        }
        [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
            border-color:var(--cas-green) !important;
            box-shadow:0 0 0 2px rgba(27,89,54,.12) !important;
        }
        [data-testid="stTextInput"] input {
            color:var(--cas-green-dark) !important;
            -webkit-text-fill-color:var(--cas-green-dark) !important;
            caret-color:var(--cas-green-dark) !important;
            min-height:42px !important;
        }
        [data-testid="stRadio"] [role="radiogroup"] {
            display:grid; grid-template-columns:1fr 1fr; gap:.5rem;
        }
        [data-testid="stRadio"] label {
            border:1px solid var(--cas-green-border); border-radius:10px; padding:.55rem .7rem;
            background:rgba(255,255,255,.76);
        }

        .stage-card {
            background:var(--cas-card); border:1px solid rgba(17,61,39,.10);
            border-radius:14px; padding:1rem; margin-bottom:.85rem;
            box-shadow:0 8px 20px rgba(57,57,57,.05);
        }
        .stage-card.active { border-color:rgba(21,79,49,.48); box-shadow:0 10px 24px rgba(21,79,49,.08); }
        .stage-head { display:flex; justify-content:space-between; gap:1rem; align-items:center; }
        .stage-left { display:flex; gap:.85rem; align-items:center; }
        .stage-badge {
            width:48px; height:48px; border-radius:50%; background:#e1ead7;
            display:grid; place-items:center; color:#134228; font-weight:800; flex-shrink:0;
        }
        .stage-title { margin:0; font-size:1.03rem; color:#183f2b; font-weight:800; }
        .stage-desc { margin:.2rem 0 0; color:rgba(24,63,43,.78); font-size:.94rem; }
        .status-chip {
            display:inline-flex; align-items:center; border-radius:999px; padding:.32rem .7rem;
            font-size:.82rem; font-weight:800; border:1px solid transparent; white-space:nowrap;
        }
        .status-completed { background:#e0efde; color:var(--cas-green); border-color:#c0ddbd; }
        .status-missing { background:#fff0e7; color:#c85e22; border-color:#ffd1b7; }
        .status-locked { background:#fff5ee; color:#d97706; border-color:#fed7aa; }
        .status-ready { background:var(--cas-green-soft); color:var(--cas-green); border-color:var(--cas-green-border); }
        .rule-box {
            background:rgba(245,248,243,.95); border:1px dashed rgba(21,79,49,.16);
            border-radius:14px; padding:.85rem .9rem; margin-top:.75rem;
        }

        .upload-card {
            background:rgba(233,240,228,.82); border:1px solid rgba(21,79,49,.08);
            border-radius:14px; padding:1rem; min-height:210px; margin-top:.1rem;
            box-shadow:0 8px 20px rgba(57,57,57,.04); display:flex; flex-direction:column;
        }
        .upload-description { min-height:3.2rem; }
        .upload-meta { margin-top:auto; padding-top:.65rem; border-top:1px solid rgba(21,79,49,.11); }
        .upload-meta ul { margin:.3rem 0 .45rem 1.05rem; padding:0; }
        .upload-meta li { margin:.12rem 0; font-size:.82rem; color:rgba(24,63,43,.78); }
        .stFileUploader section {
            background:rgba(255,255,255,.85) !important; border-radius:14px !important;
            border:1px dashed rgba(21,79,49,.2) !important; padding:.7rem !important;
        }

        [data-testid="stMain"] .stButton > button,
        .stButton > button {
            border-radius:12px; border:1px solid var(--cas-green-border);
            background:var(--cas-green-soft); color:var(--cas-green);
            min-height:44px; font-weight:800; box-shadow:none;
        }
        [data-testid="stMain"] .stButton > button:hover,
        .stButton > button:hover {
            background:var(--cas-green-hover); border-color:#91be99;
        }
        [data-testid="stMain"] .stButton > button[data-testid="baseButton-primary"],
        [data-testid="stMain"] .stButton > button[kind="primary"] {
            background:var(--cas-green) !important;
            color:white !important;
            border-color:var(--cas-green) !important;
        }
        .stProgress > div > div > div > div { background-color:var(--cas-green) !important; }

        @media (max-width: 900px) {
            .block-container { padding:3.25rem .8rem 1.25rem; }
            .greeting h1 { font-size:1.55rem; }
            .progress-head, .progress-meta, .stage-head {
                align-items:flex-start; flex-direction:column; gap:.65rem;
            }
            .stage-left { align-items:flex-start; gap:.7rem; }
            .glass-card, .soft-card, .stage-card, .upload-card { padding:1rem; }
            .upload-card, .upload-description { min-height:0; }
            [data-testid="stRadio"] [role="radiogroup"] { grid-template-columns:1fr; }
        }
        @media (max-width: 700px) {
            div[data-testid="stHorizontalBlock"] { flex-direction:column !important; gap:.75rem !important; }
            div[data-testid="column"] { width:100% !important; flex:1 1 100% !important; }
            [data-testid="stMain"] .stButton > button { width:100% !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
