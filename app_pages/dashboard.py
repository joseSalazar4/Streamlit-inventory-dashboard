from __future__ import annotations

import streamlit as st

from config.process import STAGES
from ui.process import render_progress_card, render_stage_card, render_topbar


def dashboard_page() -> None:
    with st.container(key="dashboard_header"):
        intro, progress = st.columns([5, 4], gap="large", vertical_alignment="top")
        with intro:
            render_topbar()
        with progress:
            render_progress_card()
    st.markdown("## Process Steps")
    for stage in STAGES:
        render_stage_card(stage)
