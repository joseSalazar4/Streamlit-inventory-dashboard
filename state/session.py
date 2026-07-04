from __future__ import annotations

import streamlit as st

# =============================================================================
# SESSION STATE
# =============================================================================
def init_state() -> None:
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("expanded_stage", 0)
    st.session_state.setdefault("validation", {})
    st.session_state.setdefault("pending_uploads", {})
    st.session_state.setdefault("authenticated_user", None)
    st.session_state.setdefault("auth_step", "signup")
    st.session_state.setdefault("pending_signup", None)
    st.session_state.setdefault("email_challenge", None)

