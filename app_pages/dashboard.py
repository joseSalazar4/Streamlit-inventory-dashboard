from __future__ import annotations

import streamlit as st

from config.process import STAGES
from ui.process import render_stage_card, render_status_panel, render_topbar


def dashboard_page() -> None:
    render_topbar()
    st.write("")
    render_status_panel()
    st.write("")
    st.markdown("## Process Steps")
    for stage in STAGES:
        render_stage_card(stage)
