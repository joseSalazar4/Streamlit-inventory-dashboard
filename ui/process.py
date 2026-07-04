from __future__ import annotations

from typing import Any, Dict, Tuple

import streamlit as st

from config.process import STAGES
from models.file_rule import FileRule
from validators.pdf import finish_uploaded_file, process_uploaded_file, uploader_key, validation_key


def stage_status(stage: Dict[str, Any]) -> Tuple[str, str]:
    status_list = [
        st.session_state.validation.get((stage["id"], rule.key), {}).get("ok")
        for rule in stage["files"]
    ]
    if all(value is True for value in status_list):
        return "completed", "Completed"
    if any(value is False for value in status_list):
        return "missing", "Requires attention"
    return "locked", "Pending"


def progress_metrics() -> Tuple[int, int]:
    total = done = 0
    for stage in STAGES:
        for rule in stage["files"]:
            total += 1
            result = st.session_state.validation.get((stage["id"], rule.key))
            if result and result.get("ok") is True:
                done += 1
    return done, total


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-box">
                <div class="brand-logo">CAS</div>
                <div>
                    <div class="brand-title">CAS</div>
                    <div class="brand-subtitle">DOCUMENT PORTAL</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button("Dashboard", key="nav_dashboard"):
            st.session_state.page = "Dashboard"
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Sign out", key="nav_sign_out"):
            st.session_state.authenticated_user = None
            st.session_state.page = "Dashboard"
            st.rerun()


def render_topbar() -> None:
    user = st.session_state.get("authenticated_user") or {}
    name = user.get("full_name") or user.get("username") or "there"
    st.markdown(
        f"""
        <div class="greeting">
            <h1>Hello, {name}.</h1>
            <p>Welcome back. Here's the status of your process.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_panel() -> None:
    done, total = progress_metrics()
    pct = 0 if total == 0 else round((done / total) * 100)
    current_step = len(STAGES) if done == total else min(done // 3 + 1, len(STAGES))

    left, right = st.columns([8, 4], gap="large", vertical_alignment="top")
    with left:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="progress-head">
                    <div class="stat-title">Your Process Progress</div>
                    <div class="status-chip status-ready">Step {current_step} of {len(STAGES)}</div>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{pct}%;"></div>
                </div>
                <div class="progress-meta">
                    <div class="tiny">Please upload all required documents to move forward.</div>
                    <div class="progress-number">{pct}%</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="soft-card">
                <div class="stat-title">Need Help?</div>
                <div class="stat-meta">Contact support if you need help with a document.</div>
                <div style="margin-top:.9rem;">
                    <a href="https://www.facebook.com/cascostarica1" target="_blank" style="text-decoration:none;">
                        <button class="support-link">Contact support</button>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def format_file_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def render_document_uploader(stage_id: int, rule: FileRule) -> None:
    result_key = validation_key(stage_id, rule.key)
    result = st.session_state.validation.get(result_key)
    fields = rule.required_fields or ["No specific text fields required"]

    st.markdown(
        f"""
        <div class="upload-card">
            <div class="stat-title">{rule.label}</div>
            <div class="tiny upload-description">{rule.description}</div>
            <div class="upload-meta">
                <div class="tiny"><b>Required information:</b></div>
                <ul>{''.join([f'<li>{field.replace("_", " ")}</li>' for field in fields])}</ul>
                <div class="tiny"><b>Format:</b> PDF</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result:
        file_size = format_file_size(result.get("file_size", 0))
        st.caption(f"Loaded: {result['file_name']} ({file_size})")
        progress_bar = st.progress(
            result.get("progress", 10),
            text=result.get("message", "Preparing PDF..."),
        )
        if result.get("processing"):
            result = finish_uploaded_file(stage_id, rule, progress_bar)
    else:
        st.caption("Waiting for PDF")
        st.progress(0, text="Select a PDF to begin")

    st.file_uploader(
        f"Upload {rule.label}",
        type=["pdf"],
        key=uploader_key(stage_id, rule.key),
        label_visibility="collapsed",
        on_change=process_uploaded_file,
        args=(stage_id, rule),
    )

    if result:
        if result["ok"]:
            st.success(result["message"])
        else:
            st.error(result["message"])


def is_stage_unlocked(stage_id: int) -> bool:
    if stage_id == 1:
        return True

    previous_stage = STAGES[stage_id - 2]
    status, _ = stage_status(previous_stage)
    return status == "completed"


def render_stage_header(stage: Dict[str, Any]) -> None:
    stage_id = stage["id"]
    status, _ = stage_status(stage)
    active = st.session_state.expanded_stage == stage_id
    unlocked = is_stage_unlocked(stage_id)

    if status == "completed":
        chip_text = "Completed"
        status_class = "status-completed"
    elif unlocked:
        chip_text = "Ready to upload"
        status_class = "status-ready"
    else:
        chip_text = "Locked"
        status_class = "status-locked"

    left, right = st.columns([11, 1], vertical_alignment="center")
    with left:
        st.markdown(
            f"""
            <div class="stage-card {'active' if active else ''}">
                <div class="stage-head">
                    <div class="stage-left">
                        <div class="stage-badge">{stage["icon"]}</div>
                        <div>
                            <p class="stage-title">{stage_id}. {stage["title"]}</p>
                            <p class="stage-desc">{stage["subtitle"]}</p>
                        </div>
                    </div>
                    <span class="status-chip {status_class}">{chip_text}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        if st.button(
            ">",
            key=f"toggle_{stage_id}",
            disabled=not unlocked,
            help="Open stage" if unlocked else "Complete the previous step first",
        ):
            st.session_state.expanded_stage = 0 if active else stage_id


def render_stage_uploads(stage: Dict[str, Any]) -> None:
    stage_id = stage["id"]
    st.markdown(
        """
        <div class="rule-box">
            <div class="stat-title" style="margin-bottom:.3rem;">Upload 3 files for this step</div>
            <div class="tiny">Each PDF is checked against the document rules for this stage.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(3, gap="medium")
    for column, rule in zip(columns, stage["files"]):
        with column:
            render_document_uploader(stage_id, rule)
    st.write("")


def render_stage_card(stage: Dict[str, Any]) -> None:
    render_stage_header(stage)
    if st.session_state.expanded_stage == stage["id"]:
        render_stage_uploads(stage)
