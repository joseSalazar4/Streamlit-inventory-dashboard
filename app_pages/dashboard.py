from __future__ import annotations

import os

import streamlit as st

from api.cas_api import CasApiError, get_admission_progress
from config.process import phases_from_progress
from ui.process import (
    render_phase_card,
    render_progress_card,
    render_topbar,
    render_user_identity,
)


def _load_progress() -> dict | None:
    progress = st.session_state.get("admission_progress")
    if progress:
        return progress
    user = st.session_state.get("authenticated_user") or {}
    if user.get("is_test_user") and not os.environ.get("CAS_TEST_STUDENT_ID", "").strip():
        return None
    student_id = str(user.get("student_id") or "")
    if not student_id:
        return None
    try:
        progress = get_admission_progress(student_id)
    except CasApiError:
        return None
    st.session_state.admission_progress = progress
    return progress


def dashboard_page() -> None:
    phases = phases_from_progress(_load_progress())
    with st.container(key="dashboard_header"):
        intro, brand = st.columns([7, 3], gap="large", vertical_alignment="center")
        with intro:
            render_topbar()
            render_progress_card(phases)
        with brand:
            render_user_identity()
    st.markdown("## Admission phases")
    for phase_index, phase in enumerate(phases):
        render_phase_card(phases, phase, phase_index)
