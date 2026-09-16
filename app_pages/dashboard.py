from __future__ import annotations

import os
import time

import streamlit as st

from api.cas_api import CasApiError, get_admission_progress
from config.i18n import de
from config.process import phases_from_progress
from ui.process import (
    render_phase_card,
    render_portal_help,
    render_progress_card,
    render_topbar,
    render_user_identity,
)


def _load_progress() -> dict | None:
    cached_progress = st.session_state.get("admission_progress")
    cached_at = float(st.session_state.get("admission_progress_cached_at") or 0)
    if cached_progress and time.time() - cached_at < 60:
        return cached_progress

    user = st.session_state.get("authenticated_user") or {}
    if user.get("is_test_user") and not os.environ.get("CAS_TEST_STUDENT_ID", "").strip():
        return cached_progress
    student_id = str(user.get("student_id") or "")
    if not student_id:
        return cached_progress
    try:
        progress = get_admission_progress(student_id)
    except CasApiError:
        return cached_progress
    st.session_state["admission_progress"] = progress
    st.session_state["admission_progress_cached_at"] = time.time()
    return progress


def _render_phase_list(phases: list[dict]) -> None:
    st.markdown(de("## Fases de admisión", "## Phasen der Aufnahme"))
    for phase_index, phase in enumerate(phases):
        render_phase_card(phases, phase, phase_index)


def dashboard_page() -> None:
    phases = phases_from_progress(_load_progress())
    with st.container(key="dashboard_header"):
        intro, brand = st.columns([7, 3], gap="large", vertical_alignment="center")
        with intro:
            render_topbar()
            render_progress_card(phases)
        with brand:
            render_user_identity()
    render_portal_help()
    _render_phase_list(phases)
