from __future__ import annotations

from html import escape
import logging
import re
from typing import Any, Dict, Iterable, Tuple

import streamlit as st

from api.cas_api import document_download_url, document_template_download_url
from auth.session_cookie import sign_out_current_user
from models.file_rule import FileRule
from validators.files import (
    process_uploaded_file,
    submit_uploaded_files,
    uploader_key,
    validation_key,
)


REMOTE_FILE_STATUSES = {
    "approved",
    "pending_review",
    "needs_replacement",
    "available_for_download",
}
LOGGER = logging.getLogger(__name__)
SUPPORT_URL = "https://wa.me/4915231897485"
NAME_PART_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)


def format_display_name(value: object) -> str:
    name = " ".join(str(value or "").split())

    def normalize_part(match: re.Match[str]) -> str:
        part = match.group(0)
        if part.islower() or part.isupper():
            return part.capitalize()
        return part

    return NAME_PART_PATTERN.sub(normalize_part, name)


def phase_status(phase: Dict[str, Any]) -> Tuple[str, str]:
    remote_status = str(phase.get("status") or "")
    if remote_status == "approved":
        return "completed", "Completed"
    if remote_status == "needs_replacement":
        return "missing", "Requires attention"
    if remote_status == "pending_review":
        return "review", "In review"
    if remote_status == "waiting_for_cas":
        return "waiting", "Waiting for CAS"

    uploadable = [rule for rule in phase["files"] if rule.can_student_upload]
    if not uploadable:
        return "completed", "Available"
    results = [
        st.session_state.validation.get(validation_key(phase["id"], rule.key), {})
        for rule in uploadable
    ]
    completed = sum(
        1
        for rule, result in zip(uploadable, results)
        if result.get("storage_status") == "saved" or rule.status in REMOTE_FILE_STATUSES
    )
    if completed == len(uploadable):
        return "completed", "Completed"
    if any(result.get("ok") is False for result in results):
        return "missing", "Requires attention"
    if any(result.get("storage_status") == "ready_to_submit" for result in results):
        return "ready", "Ready to submit"
    return "pending", "Pending"


def progress_metrics(phases: Iterable[Dict[str, Any]]) -> Tuple[int, int]:
    done = 0
    total = 0
    for phase in phases:
        for rule in phase["files"]:
            if not rule.can_student_upload:
                continue
            total += 1
            result = st.session_state.validation.get(validation_key(phase["id"], rule.key), {})
            if result.get("storage_status") == "saved" or rule.status in REMOTE_FILE_STATUSES:
                done += 1
    return done, total


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-box">
                <div class="brand-logo-image" aria-label="CAS logo"></div>
                <div>
                    <div class="brand-title">CAS</div>
                    <div class="brand-subtitle">DOCUMENT PORTAL</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        st.button(
            "Dashboard",
            key="nav_dashboard",
            icon=":material/dashboard:",
            width="stretch",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button(
            "Sign out",
            key="nav_sign_out",
            icon=":material/logout:",
            width="stretch",
        ):
            sign_out_current_user()
        render_sidebar_help()


def render_sidebar_help() -> None:
    with st.container(key="sidebar_help_card"):
        st.markdown(
            """
            <div class="sidebar-help-copy">
                <div class="stat-title">Need help?</div>
                <div class="stat-meta">Contact support if you need help with a document.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(
            "Contact support",
            SUPPORT_URL,
            icon=":material/support_agent:",
            type="tertiary",
            width="content",
        )


def render_mobile_help() -> None:
    with st.container(key="mobile_help"):
        st.link_button(
            "Need help?",
            SUPPORT_URL,
            icon=":material/support_agent:",
            type="tertiary",
            width="content",
        )


def render_topbar() -> None:
    user = st.session_state.get("authenticated_user") or {}
    name = escape(format_display_name(user.get("full_name") or user.get("username") or "there"))
    st.markdown(
        f"""
        <div class="greeting">
            <h1>Hello, {name}.</h1>
            <p>Welcome back. Here is the status of your admission process.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_user_identity() -> None:
    user = st.session_state.get("authenticated_user") or {}
    name = escape(format_display_name(user.get("full_name") or user.get("username") or "Student"))
    email = escape(str(user.get("email") or ""))
    st.markdown(
        f"""
        <div class="dashboard-user">
            <div class="dashboard-brand-mark" aria-label="CAS logo"></div>
            <div class="dashboard-user-name">{name}</div>
            <div class="dashboard-user-email">{email}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress_card(phases: list[Dict[str, Any]]) -> None:
    done, total = progress_metrics(phases)
    percentage = 0 if total == 0 else round((done / total) * 100)
    progress = st.session_state.get("admission_progress") or {}
    current_phase_id = str((progress.get("student") or {}).get("current_phase_id") or "")
    current_phase = next(
        (phase["number"] for phase in phases if str(phase["id"]) == current_phase_id),
        None,
    )
    if current_phase is None:
        current_phase = next(
            (phase["number"] for phase in phases if phase_status(phase)[0] != "completed"),
            len(phases),
        )

    st.markdown(
        f"""
        <div class="glass-card progress-card">
            <div class="progress-head">
                <div class="progress-title">Your admission progress</div>
                <div class="status-chip status-ready">Phase {current_phase} of {len(phases)}</div>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{percentage}%;"></div>
            </div>
            <div class="progress-meta">
                <div class="tiny">{done} of {total} student files received.</div>
                <div class="progress-number">{percentage}%</div>
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


def allowed_type_label(allowed_types: Iterable[str]) -> str:
    labels: list[str] = []
    for extension in allowed_types:
        label = "JPG" if extension.lower() in {"jpg", "jpeg"} else extension.upper()
        if label not in labels:
            labels.append(label)
    return " / ".join(labels)


def render_document_uploader(phase_id: str, rule: FileRule) -> None:
    result_key = validation_key(phase_id, rule.key)
    result = st.session_state.validation.get(result_key)
    type_label = allowed_type_label(rule.allowed_types)
    status_text = {
        "approved": "Approved",
        "pending_review": "Pending review",
        "needs_replacement": "Replacement requested",
    }.get(rule.status)

    with st.container(key=f"upload_item_{phase_id}_{rule.key}"):
        st.markdown(
            f"""
            <div class="upload-summary">
                <div class="upload-title-row">
                    <div class="stat-title">{escape(rule.label)}</div>
                    <span class="file-chip">{escape(type_label)}</span>
                </div>
                <div class="upload-divider"></div>
                <p>{escape(rule.description)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if status_text and not result:
            st.info(status_text, icon=":material/info:")

        st.file_uploader(
            f"Upload {rule.label}",
            type=list(rule.allowed_types),
            key=uploader_key(phase_id, rule.key),
            help=f"Maximum 40 MB. Allowed types: {type_label}.",
            max_upload_size=40,
            label_visibility="collapsed",
            on_change=process_uploaded_file,
            args=(phase_id, rule),
            width="stretch",
        )

        if result:
            st.caption(
                f"Selected: {result.get('file_name', 'file')} "
                f"({format_file_size(int(result.get('file_size') or 0))})"
            )
            if result.get("storage_status") == "saved":
                st.success(result["message"])
            elif result.get("storage_status") == "submitting":
                st.info("Submitting file...")
            elif result.get("ok"):
                st.info(result["message"])
            else:
                st.error(result["message"])


def _download_rules(phase: Dict[str, Any]) -> list[FileRule]:
    rules = [
        rule
        for rule in phase["files"]
        if rule.flow_type == "external_link_only"
        or rule.template_scope in {"global", "student_specific"}
    ]
    return sorted(
        rules,
        key=lambda rule: (len(rule.label.strip()), rule.label.casefold()),
    )


def _render_download_button(phase_id: str, rule: FileRule) -> None:
    key = f"download_{phase_id}_{rule.key}"
    if rule.flow_type == "external_link_only":
        st.link_button(
            rule.label,
            rule.external_url or "https://hubspot.com",
            key=key,
            icon=":material/open_in_new:",
            width="stretch",
        )
        return
    if rule.template_scope == "global":
        if rule.template_available is False:
            st.button(
                rule.label,
                key=key,
                icon=":material/download:",
                disabled=True,
                help="This template is not available yet.",
                width="stretch",
            )
            return
        st.link_button(
            rule.label,
            document_template_download_url(rule.key, scope="global"),
            key=key,
            icon=":material/download:",
            width="stretch",
        )
        return
    if rule.document_id:
        st.link_button(
            rule.label,
            document_download_url(rule.document_id),
            key=key,
            icon=":material/download:",
            width="stretch",
        )
        return
    st.button(
        rule.label,
        key=key,
        icon=":material/download:",
        disabled=True,
        help="This file is not available yet.",
        width="stretch",
    )


def render_phase_downloads(phase: Dict[str, Any]) -> None:
    rules = _download_rules(phase)
    if not rules:
        return
    with st.expander(
        "Templates",
        key=f"phase_downloads_{phase['id']}",
        icon=":material/download:",
    ):
        st.caption("Open external forms or download files provided by CAS.")
        for row_start in range(0, len(rules), 3):
            row_rules = rules[row_start : row_start + 3]
            columns = st.columns(len(row_rules), gap="small")
            for column, rule in zip(columns, row_rules):
                with column:
                    _render_download_button(str(phase["id"]), rule)


def _phase_ready_documents(phase: Dict[str, Any]) -> list[FileRule]:
    ready: list[FileRule] = []
    for rule in phase["files"]:
        key = validation_key(phase["id"], rule.key)
        result = st.session_state.validation.get(key, {})
        if (
            rule.can_student_upload
            and result.get("ok") is True
            and result.get("storage_status") != "saved"
            and key in st.session_state.pending_uploads
        ):
            ready.append(rule)
    return ready


def render_phase_submit(phase: Dict[str, Any], placement: str) -> None:
    uploadable = [rule for rule in phase["files"] if rule.can_student_upload]
    if not uploadable:
        return
    ready_rules = _phase_ready_documents(phase)
    with st.container(key=f"phase_submit_bar_{placement}_{phase['id']}"):
        if st.button(
            f"Submit ready files ({len(ready_rules)})",
            key=f"submit_phase_{placement}_{phase['id']}",
            icon=":material/cloud_upload:",
            type="primary",
            disabled=not ready_rules,
            help="Submit the files you selected.",
            width="stretch",
        ):
            try:
                with st.spinner(f"Submitting {len(ready_rules)} files..."):
                    submit_uploaded_files(str(phase["id"]), ready_rules)
            except Exception:
                LOGGER.exception("Phase file submission failed for %s", phase["id"])
                for rule in ready_rules:
                    result = st.session_state.validation.get(
                        validation_key(phase["id"], rule.key),
                        {},
                    )
                    if result.get("storage_status") == "submitting":
                        result["storage_status"] = "ready_to_submit"
                st.error("Files could not be submitted. Please try again.")
            else:
                st.rerun()


def is_phase_unlocked(phases: list[Dict[str, Any]], phase_index: int) -> bool:
    progress = st.session_state.get("admission_progress") or {}
    current_phase_id = str((progress.get("student") or {}).get("current_phase_id") or "")
    current_phase_index = next(
        (
            index
            for index, item in enumerate(phases)
            if str(item["id"]) == current_phase_id
        ),
        0,
    )
    return phase_index <= current_phase_index


def render_phase_header(
    phases: list[Dict[str, Any]],
    phase: Dict[str, Any],
    phase_index: int,
) -> None:
    status, status_label = phase_status(phase)
    phase_id = str(phase["id"])
    unlocked = is_phase_unlocked(phases, phase_index)
    active = unlocked and st.session_state.expanded_phase == phase_id
    if unlocked:
        chip_text = status_label if status != "pending" else "Open phase"
        status_class = {
            "completed": "completed",
            "missing": "missing",
            "review": "ready",
            "waiting": "locked",
            "ready": "ready",
        }.get(status, "ready")
        action_icon = (
            ":material/keyboard_arrow_up:"
            if active
            else ":material/keyboard_arrow_down:"
        )
    else:
        chip_text = "Locked"
        status_class = "locked"
        action_icon = ":material/lock:"

    with st.container(key=f"phase_header_{phase_id}"):
        st.markdown(
            f"""
            <div class="phase-card phase-tone-{phase['number']} {'active' if active else ''}">
                <div class="phase-head">
                    <div class="phase-left">
                        <div class="phase-badge">
                            <span class="material-symbols-rounded">{phase["icon"]}</span>
                        </div>
                        <div>
                            <p class="phase-title">{phase["number"]}. {escape(str(phase["title"]))}</p>
                            <p class="phase-desc">{escape(str(phase["subtitle"]))}</p>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            chip_text,
            key=f"phase_action_{status_class}_{phase_id}",
            icon=action_icon,
            disabled=not unlocked,
            help=(
                ("Close phase" if active else "Open phase")
                if unlocked
                else "CAS will unlock this phase after approving the current phase."
            ),
        ):
            st.session_state.expanded_phase = "" if active else phase_id
            st.rerun()


def render_phase_uploads(phase: Dict[str, Any]) -> None:
    render_phase_downloads(phase)
    uploadable = [rule for rule in phase["files"] if rule.can_student_upload]
    if not uploadable:
        return
    with st.expander(
        "Files to upload",
        key=f"phase_uploads_{phase['id']}",
        icon=":material/upload_file:",
    ):
        render_phase_submit(phase, "top")
        for row_start in range(0, len(uploadable), 3):
            row_rules = uploadable[row_start : row_start + 3]
            columns = st.columns(len(row_rules), gap="medium")
            for column, rule in zip(columns, row_rules):
                with column:
                    render_document_uploader(str(phase["id"]), rule)
        render_phase_submit(phase, "bottom")


def render_phase_card(
    phases: list[Dict[str, Any]],
    phase: Dict[str, Any],
    phase_index: int,
) -> None:
    render_phase_header(phases, phase, phase_index)
    if (
        is_phase_unlocked(phases, phase_index)
        and st.session_state.expanded_phase == str(phase["id"])
    ):
        render_phase_uploads(phase)
