from __future__ import annotations

import streamlit as st

from app_pages.auth import auth_page
from app_pages.dashboard import dashboard_page
from auth.session_cookie import render_cookie_update, restore_auth_session
from state.session import init_state
from styles.app import inject_css
from ui.process import render_mobile_help, render_sidebar


st.set_page_config(
    page_title="CAS",
    page_icon="CAS",
    layout="wide",
    initial_sidebar_state="auto",
)


def main() -> None:
    inject_css()
    init_state()
    restore_auth_session()
    render_cookie_update()

    user = st.session_state.authenticated_user
    if not user:
        auth_page()
        return

    render_sidebar()
    render_mobile_help()
    dashboard_page()


if __name__ == "__main__":
    main()
