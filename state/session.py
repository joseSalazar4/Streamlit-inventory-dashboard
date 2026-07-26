from __future__ import annotations

import streamlit as st

# =============================================================================
# SESSION STATE
# =============================================================================
def init_state() -> None:
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("expanded_phase", "")
    st.session_state.setdefault("validation", {})
    st.session_state.setdefault("pending_uploads", {})
    st.session_state.setdefault("authenticated_user", None)
    st.session_state.setdefault("admission_progress", None)
    st.session_state.setdefault("auth_notice", "")
    st.session_state.setdefault("auth_view", "sign_in")
    st.session_state.setdefault("pending_auth_user", None)
    st.session_state.setdefault("pending_auth_progress", None)
    st.session_state.setdefault("pending_auth_email", "")
    st.session_state.setdefault("password_change_token", "")

