from __future__ import annotations

import streamlit as st

from app_pages.auth import auth_page
from app_pages.dashboard import dashboard_page
from auth.session_cookie import render_cookie_update, restore_auth_session
from state.session import init_state
from styles.app import inject_css
from ui.process import render_sidebar


st.set_page_config(
    page_title="CAS",
    page_icon="CAS",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    inject_css()
    init_state()
    restore_auth_session()
    render_cookie_update()

    if not st.session_state.authenticated_user:
        auth_page()
        return

    render_sidebar()
    dashboard_page()


if __name__ == "__main__":
    main()
