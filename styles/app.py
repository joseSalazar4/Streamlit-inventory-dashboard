from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


def _asset_data_uri(filename: str) -> str:
    path = Path(__file__).resolve().parent.parent / "assets" / filename
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def inject_css() -> None:
    nav_logo = _asset_data_uri("cas-logo-navbar.png")
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
        [data-testid="stAppDeployButton"] { display:none !important; }
        div[data-testid="stStatusWidget"],
        div[data-testid="stDecoration"] { display:none !important; }
        header[data-testid="stHeader"] { background:transparent; }
        [data-testid="stSidebarCollapsedControl"] {
            display:block !important;
            visibility:visible !important;
            opacity:1 !important;
            z-index:1000 !important;
        }
        [data-testid="stSidebarCollapsedControl"] button {
            background:rgba(255,253,248,.9) !important;
            border:1px solid rgba(21,79,49,.18) !important;
            border-radius:10px !important;
            color:var(--cas-green-dark) !important;
            box-shadow:0 8px 18px rgba(57,57,57,.05) !important;
        }
        .block-container { max-width:1320px; padding-top:2.75rem; padding-bottom:1rem; }

        section[data-testid="stSidebar"] {
            background:linear-gradient(180deg, #fbf7ef 0%, #f0eadf 65%, #eaf3e8 100%);
            border-right:1px solid rgba(16,59,37,.08);
        }
        section[data-testid="stSidebar"] > div { padding-top:1rem; }
        .brand-box { display:flex; align-items:center; gap:12px; padding:12px 10px 22px; }
        .brand-logo-image {
            width:58px; height:44px; flex-shrink:0;
            background-image:url("__CAS_NAV_LOGO__");
            background-position:center;
            background-repeat:no-repeat;
            background-size:contain;
        }
        .brand-title { font-size:1.35rem; font-weight:800; letter-spacing:.08em; color:#1a4d33; }
        .brand-subtitle { margin-top:3px; font-size:.78rem; letter-spacing:.14em; color:rgba(26,77,51,.75); }
        div[data-testid="stSidebar"] .stButton > button {
            width:100%; border-radius:0; border:0;
            background:transparent !important; color:#111111 !important; padding:.45rem .1rem;
            text-align:left; font-weight:700; box-shadow:none;
        }
        div[data-testid="stSidebar"] .stButton > button:hover,
        .nav-active button {
            background:transparent !important;
            border-color:transparent !important;
            color:#111111 !important;
            text-decoration:underline;
            text-underline-offset:4px;
        }
        [class*="st-key-sidebar_help_card"] {
            margin-top:clamp(3rem, 28vh, 14rem);
            padding:.9rem;
            border:1px solid rgba(21,79,49,.14);
            border-radius:14px;
            background:rgba(255,255,255,.58);
            box-shadow:0 10px 24px rgba(57,57,57,.05);
        }
        .sidebar-help-copy {
            padding:0 0 .65rem;
        }
        .sidebar-help-copy .stat-title { color:#111111; margin-bottom:.35rem; }
        .sidebar-help-copy .stat-meta {
            color:#2f3b34;
            font-size:.9rem;
            line-height:1.45;
        }
        div[data-testid="stSidebar"] [data-testid="stLinkButton"] a,
        div[data-testid="stSidebar"] .stLinkButton a {
            justify-content:flex-start;
            padding:.45rem .1rem;
            color:#111111 !important;
            background:transparent !important;
            border:0 !important;
            font-weight:800;
            text-decoration:underline;
            text-underline-offset:4px;
        }
        [data-testid="stSidebar"] [class*="st-key-sidebar_help_card"] [data-testid="stLinkButton"] a,
        [data-testid="stSidebar"] [class*="st-key-sidebar_help_card"] .stLinkButton a {
            justify-content:center;
            min-height:38px;
            padding:.45rem .72rem;
            border-radius:10px;
            color:#174b2e !important;
            background:#e9f3e8 !important;
            border:1px solid #cfdfcf !important;
            text-decoration:none;
            box-shadow:0 4px 10px rgba(16,59,37,.08);
        }
        [data-testid="stSidebar"] [class*="st-key-sidebar_help_card"] [data-testid="stLinkButton"] a:hover,
        [data-testid="stSidebar"] [class*="st-key-sidebar_help_card"] .stLinkButton a:hover {
            color:#123f29 !important;
            background:#dcebdc !important;
            border-color:#bad2bc !important;
        }
        [data-testid="stSidebar"] [class*="st-key-sidebar_help_card"] [data-testid="stLinkButton"],
        [data-testid="stSidebar"] [class*="st-key-sidebar_help_card"] .stLinkButton {
            display:flex;
            justify-content:center;
            width:100%;
        }
        [class*="st-key-mobile_help"] {
            display:none;
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

        .st-key-dashboard_header {
            max-width:1120px;
            margin-bottom:1.1rem;
        }
        .greeting h1 { margin:0; font-size:2rem; line-height:1.15; color:#14432b; }
        .greeting p { margin:.25rem 0 1rem; color:rgba(20,67,43,.76); font-size:1rem; }
        .dashboard-brand-mark {
            width:min(100%, 320px);
            height:82px;
            margin-left:auto;
            background-image:url("__CAS_NAV_LOGO__");
            background-position:center right;
            background-repeat:no-repeat;
            background-size:contain;
        }
        .dashboard-user { text-align:right; }
        .dashboard-user-name {
            margin-top:.35rem;
            color:#14432b;
            font-size:.95rem;
            font-weight:800;
        }
        .dashboard-user-email {
            color:rgba(20,67,43,.68);
            font-size:.8rem;
            overflow-wrap:anywhere;
        }
        .progress-card { padding:.95rem 1rem; max-width:760px; }
        .progress-head, .progress-meta {
            display:flex; align-items:center; justify-content:space-between; gap:1rem;
        }
        .progress-title {
            font-size:1.42rem;
            line-height:1.15;
            font-weight:900;
            color:#14432b;
        }
        .progress-track {
            width:100%;
            height:10px; margin:.8rem 0 .5rem; background:#e7eadf;
            border-radius:999px; overflow:hidden;
        }
        .progress-fill { height:100%; background:linear-gradient(90deg, #1d5a39 0%, #134228 100%); }
        .progress-number { font-weight:800; color:#18402a; }
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
            width:100%;
            border:1px solid var(--cas-green-border); border-radius:10px; padding:.55rem .7rem;
            background:rgba(255,255,255,.76);
            justify-content:center;
        }
        .st-key-forgot_password .stButton > button,
        .st-key-reset_back_to_signin .stButton > button,
        .st-key-reset_code_back_to_signin .stButton > button,
        .st-key-change_password_back_to_signin .stButton > button {
            min-height:32px !important;
            padding:.2rem .1rem !important;
            background:transparent !important;
            border:0 !important;
            color:#111111 !important;
            box-shadow:none !important;
            text-decoration:underline;
            text-underline-offset:4px;
        }

        .phase-card {
            background:linear-gradient(90deg, var(--phase-soft, rgba(255,255,255,.82)) 0, var(--cas-card) 18%);
            border:1px solid rgba(17,61,39,.10);
            border-left:5px solid var(--phase-accent, rgba(21,79,49,.28));
            border-radius:14px; padding:1rem; margin-bottom:.85rem;
            box-shadow:0 8px 20px rgba(57,57,57,.05);
        }
        .phase-card.active {
            border-color:rgba(21,79,49,.22);
            border-left-color:var(--phase-accent, var(--cas-green));
            box-shadow:0 10px 24px rgba(21,79,49,.08);
        }
        .phase-tone-1 { --phase-accent:#166534; --phase-soft:#eef8ec; }
        .phase-tone-2 { --phase-accent:#2563eb; --phase-soft:#eef5ff; }
        .phase-tone-3 { --phase-accent:#7c3aed; --phase-soft:#f5f0ff; }
        .phase-tone-4 { --phase-accent:#d97706; --phase-soft:#fff7ed; }
        .phase-tone-5 { --phase-accent:#be123c; --phase-soft:#fff1f3; }
        .phase-tone-6 { --phase-accent:#0f766e; --phase-soft:#ecfdf5; }
        .phase-head { display:flex; justify-content:space-between; gap:1rem; align-items:center; }
        .phase-left { display:flex; gap:.85rem; align-items:center; }
        .phase-badge {
            width:48px; height:48px; border-radius:50%; background:var(--phase-soft, #e1ead7);
            display:grid; place-items:center; color:var(--phase-accent, #134228); font-weight:800; flex-shrink:0;
        }
        .phase-badge .material-symbols-rounded {
            font-family:"Material Symbols Rounded";
            font-size:1.45rem;
            font-weight:700;
            line-height:1;
            font-style:normal;
            letter-spacing:normal;
            text-transform:none;
            font-feature-settings:"liga";
            font-variation-settings:"FILL" 0, "wght" 700, "GRAD" 0, "opsz" 24;
        }
        .phase-title { margin:0; font-size:1.03rem; color:#183f2b; font-weight:800; }
        .phase-desc { margin:.2rem 0 0; color:rgba(24,63,43,.78); font-size:.94rem; }
        .status-chip {
            display:inline-flex; align-items:center; border-radius:999px; padding:.32rem .7rem;
            font-size:.82rem; font-weight:800; border:1px solid transparent; white-space:nowrap;
        }
        .status-completed { background:#e0efde; color:var(--cas-green); border-color:#c0ddbd; }
        .status-missing { background:#fff0e7; color:#c85e22; border-color:#ffd1b7; }
        .status-locked { background:#fff5ee; color:#d97706; border-color:#fed7aa; }
        .status-ready { background:var(--cas-green-soft); color:var(--cas-green); border-color:var(--cas-green-border); }
        [class*="st-key-phase_header_"] { position:relative; }
        [class*="st-key-phase_header_"] .phase-card { padding-right:12.75rem; }
        [class*="st-key-phase_action_"] {
            position:absolute;
            right:1rem;
            top:1rem;
            z-index:3;
            width:10.5rem !important;
        }
        [class*="st-key-phase_action_"] .stButton {
            width:100% !important;
        }
        [class*="st-key-phase_action_"] .stButton > button {
            width:100% !important;
            min-width:100% !important;
            min-height:34px !important;
            padding:.32rem .7rem !important;
            border-radius:999px !important;
            box-shadow:none !important;
            font-size:.82rem !important;
            font-weight:800 !important;
            justify-content:center !important;
            line-height:1 !important;
            white-space:nowrap !important;
        }
        [class*="st-key-phase_action_"] .stButton > button [data-testid="stIconMaterial"] {
            margin-right:.1rem !important;
            font-size:1rem !important;
        }
        [class*="st-key-phase_action_ready_"] .stButton > button,
        [class*="st-key-phase_action_completed_"] .stButton > button {
            background:var(--cas-green-soft) !important;
            color:var(--cas-green) !important;
            border:1px solid var(--cas-green-border) !important;
        }
        [class*="st-key-phase_action_ready_"] .stButton > button:hover,
        [class*="st-key-phase_action_completed_"] .stButton > button:hover {
            background:var(--cas-green-hover) !important;
            border-color:#91be99 !important;
        }
        [class*="st-key-phase_action_locked_"] .stButton > button,
        [class*="st-key-phase_action_locked_"] .stButton > button:disabled {
            background:#fff5ee !important;
            color:#d97706 !important;
            border:1px solid #fed7aa !important;
            cursor:not-allowed !important;
            opacity:1 !important;
        }
        [class*="st-key-phase_action_locked_"] .stButton > button:hover {
            background:#fff5ee !important;
            border-color:#fed7aa !important;
        }

        [class*="st-key-upload_item_"] {
            background:linear-gradient(180deg, rgba(255,255,255,.94), rgba(240,247,236,.86));
            border:1px solid rgba(21,79,49,.14);
            border-left:8px solid rgba(27,89,54,.78);
            border-radius:14px;
            padding:.9rem .95rem 1rem;
            margin-top:.25rem;
            box-shadow:0 10px 22px rgba(57,57,57,.05);
        }
        .upload-title-row {
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:.75rem;
        }
        .upload-summary .stat-title {
            margin:0;
            color:#123f29;
            font-size:.98rem;
            line-height:1.25;
        }
        .file-chip {
            display:inline-flex;
            align-items:center;
            border-radius:999px;
            padding:.2rem .52rem;
            background:#fff5e7;
            color:#b45309;
            border:1px solid #fed7aa;
            font-size:.72rem;
            font-weight:900;
        }
        .upload-divider {
            height:1px;
            margin:.65rem 0 .55rem;
            background:linear-gradient(90deg, rgba(27,89,54,.28), rgba(27,89,54,.05));
        }
        .upload-summary ul {
            margin:.35rem 0 .8rem 1.05rem;
            padding:0;
            color:#375a48;
        }
        .upload-summary li {
            margin:.16rem 0;
            font-size:.84rem;
            line-height:1.35;
        }
        .upload-summary p {
            margin:.35rem 0 .8rem;
            color:#375a48;
            font-size:.84rem;
            line-height:1.4;
        }
        [class*="st-key-upload_item_"] .stFileUploader section,
        [class*="st-key-upload_item_"] [data-testid="stFileUploaderDropzone"] {
            background:#fffdf8 !important;
            border-radius:12px !important;
            border:1px dashed rgba(21,79,49,.24) !important;
            padding:.62rem !important;
            min-height:76px !important;
        }
        [class*="st-key-phase_downloads_"] {
            margin:.25rem 0 .35rem;
        }
        [class*="st-key-phase_uploads_"] {
            margin:.25rem 0 .7rem;
        }
        [class*="st-key-phase_downloads_"] details,
        [class*="st-key-phase_uploads_"] details {
            border:1px solid rgba(21,79,49,.18);
            border-radius:12px;
            background:rgba(255,255,255,.7);
            overflow:hidden;
        }
        [class*="st-key-phase_downloads_"] summary,
        [class*="st-key-phase_uploads_"] summary {
            color:#123f29;
            font-weight:800;
        }
        [class*="st-key-phase_submit_bar_"] {
            margin:.15rem 0 .85rem;
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

        /* Keep server-backed actions visibly busy and prevent accidental double clicks. */
        div[data-testid="stSpinner"] {
            position:fixed !important;
            inset:0 !important;
            z-index:10000 !important;
            display:flex !important;
            align-items:center !important;
            justify-content:center !important;
            width:100vw !important;
            height:100dvh !important;
            margin:0 !important;
            padding:1rem !important;
            color:var(--cas-green-dark) !important;
            background:rgba(247,243,234,.76) !important;
            backdrop-filter:blur(2px);
            -webkit-backdrop-filter:blur(2px);
            pointer-events:auto;
        }
        div[data-testid="stSpinner"] > div {
            width:auto !important;
            min-width:min(18rem, calc(100vw - 2rem));
            max-width:min(24rem, calc(100vw - 2rem));
            padding:.85rem 1rem !important;
            border:1px solid rgba(21,79,49,.18);
            border-radius:14px;
            background:#fffdf8;
            box-shadow:0 14px 36px rgba(16,59,37,.16);
            justify-content:center !important;
        }

        @media (min-width: 901px) {
            [class*="st-key-upload_item_"] {
                min-height:256px;
            }
        }
        @media (max-width: 900px) {
            .block-container { padding:3.25rem .8rem 1.25rem; }
            .greeting h1 { font-size:1.55rem; }
            .dashboard-brand-mark { display:none; }
            .progress-head, .progress-meta, .phase-head {
                align-items:flex-start; flex-direction:column; gap:.65rem;
            }
            .phase-left { align-items:flex-start; gap:.7rem; }
            .glass-card, .soft-card, .phase-card { padding:1rem; }
            .st-key-dashboard_header { max-width:none; }
            .progress-card { max-width:none; }
            .progress-track { width:100%; }
            [class*="st-key-upload_item_"] { min-height:0; }
            .dashboard-user { display:none; }
        }
        @media (max-width: 700px) {
            .stApp::before {
                content:"";
                position:fixed;
                top:0;
                left:0;
                right:0;
                height:58px;
                display:flex;
                align-items:center;
                justify-content:center;
                background-image:url("__CAS_NAV_LOGO__");
                background-position:center;
                background-repeat:no-repeat;
                background-size:133px auto;
                background-color:rgba(247,243,234,.96);
                border-bottom:1px solid rgba(16,59,37,.08);
                color:#111111;
                font-weight:900;
                letter-spacing:.08em;
                z-index:999;
                pointer-events:none;
            }
            .block-container {
                width:100%;
                max-width:34rem;
                margin:0 auto;
                padding:4.5rem 1rem 5.5rem !important;
            }
            .block-container > [data-testid="stVerticalBlock"] {
                gap:.85rem !important;
            }
            [data-testid="stSidebarCollapsedControl"] {
                z-index:1000 !important;
            }
            [data-testid="stSidebarCollapsedControl"] button {
                color:transparent !important;
                font-size:0 !important;
            }
            [data-testid="stSidebarCollapsedControl"] button > * {
                display:none !important;
            }
            [data-testid="stSidebarCollapsedControl"] button::before {
                content:"\\2630";
                color:var(--cas-green-dark);
                font-size:1.55rem;
                font-weight:900;
                line-height:1;
                display:block;
            }
            [data-testid="stHorizontalBlock"] {
                flex-direction:column !important;
                gap:.65rem !important;
            }
            [data-testid="stColumn"] {
                width:100% !important;
                min-width:0 !important;
                flex:1 1 100% !important;
            }
            .st-key-dashboard_header {
                width:100%;
                margin:0 0 .35rem;
            }
            .greeting {
                max-width:28rem;
                margin:0 auto;
                text-align:center;
            }
            .greeting h1 {
                padding:.45rem 0 .3rem !important;
                font-size:clamp(1.4rem, 6vw, 1.65rem);
                line-height:1.2;
                text-wrap:balance;
            }
            .greeting p {
                max-width:26rem;
                margin:0 auto .75rem;
                font-size:.94rem;
                line-height:1.45;
                text-wrap:balance;
            }
            .progress-card {
                width:100%;
                margin:0 auto;
                padding:.9rem;
            }
            .progress-head,
            .progress-meta {
                width:100%;
                flex-direction:row;
                align-items:center;
                gap:.55rem;
            }
            .progress-title {
                font-size:1.16rem;
                line-height:1.25;
            }
            .progress-track {
                margin:.7rem 0 .45rem;
            }
            .status-chip {
                padding:.26rem .55rem;
                font-size:.75rem;
            }
            [data-testid="stMain"] h2 {
                padding:.65rem 0 .4rem !important;
                font-size:1.65rem !important;
                line-height:1.2 !important;
            }
            [data-testid="stMain"] h4 {
                padding:.5rem 0 .2rem !important;
                font-size:1.2rem !important;
                line-height:1.25 !important;
            }
            [data-testid="stMain"] .stButton > button { width:100% !important; }
            [class*="st-key-phase_header_"] .phase-card {
                padding:.8rem;
                margin-bottom:.3rem;
            }
            .phase-left {
                align-items:center;
                gap:.65rem;
            }
            .phase-badge {
                width:42px;
                height:42px;
            }
            .phase-badge .material-symbols-rounded {
                font-size:1.25rem;
            }
            .phase-title {
                font-size:.94rem !important;
                line-height:1.3;
            }
            .phase-desc {
                margin-top:.12rem;
                font-size:.86rem !important;
                line-height:1.4;
            }
            [class*="st-key-phase_action_"] {
                position:static;
                transform:none;
                width:100% !important;
                margin:0 0 .7rem;
            }
            [class*="st-key-phase_action_"] .stButton > button {
                width:100% !important;
                min-width:100% !important;
                min-height:36px !important;
                padding:.28rem .56rem !important;
                font-size:.78rem !important;
            }
            [class*="st-key-phase_action_"] .stButton > button [data-testid="stIconMaterial"] {
                font-size:.9rem !important;
            }
            [class*="st-key-upload_item_"] {
                min-height:0;
                padding:.8rem;
                margin-top:.1rem;
                border-left-width:5px;
            }
            .upload-title-row { align-items:flex-start; }
            .upload-summary ul { margin-bottom:.6rem; }
            [class*="st-key-upload_item_"] .stFileUploader section,
            [class*="st-key-upload_item_"] [data-testid="stFileUploaderDropzone"] {
                min-height:64px !important;
                padding:.55rem !important;
                align-items:center !important;
                justify-content:center !important;
                text-align:center !important;
            }
            [class*="st-key-upload_item_"] [data-testid="stFileUploaderDropzoneInstructions"] {
                display:block !important;
                font-size:.78rem !important;
                line-height:1.25 !important;
                max-width:100% !important;
            }
            [class*="st-key-phase_submit_bar_top_"] {
                position:static;
                margin:.1rem 0 .65rem;
                padding:0;
                background:transparent;
                border-bottom:0;
            }
            [class*="st-key-sidebar_help_card"] {
                margin-top:1rem;
            }
            [class*="st-key-mobile_help"] {
                position:fixed;
                right:max(1rem, env(safe-area-inset-right));
                bottom:max(1rem, env(safe-area-inset-bottom));
                z-index:1200;
                display:block !important;
                width:auto !important;
                margin:0 !important;
            }
            [class*="st-key-mobile_help"] [data-testid="stLinkButton"] a,
            [class*="st-key-mobile_help"] .stLinkButton a {
                width:auto !important;
                min-height:46px;
                padding:.55rem .9rem;
                border:1px solid #bad2bc !important;
                border-radius:999px;
                color:#174b2e !important;
                background:#e9f3e8 !important;
                font-weight:800;
                text-decoration:none;
                box-shadow:0 10px 28px rgba(16,59,37,.2);
            }
            [class*="st-key-mobile_help"] [data-testid="stLinkButton"] a:hover,
            [class*="st-key-mobile_help"] .stLinkButton a:hover {
                color:#123f29 !important;
                background:#dcebdc !important;
                border-color:#91be99 !important;
            }
        }
        @media (max-width: 380px) {
            .progress-head {
                flex-direction:column;
                align-items:flex-start;
            }
        }
        </style>
        """.replace("__CAS_NAV_LOGO__", nav_logo),
        unsafe_allow_html=True,
    )
