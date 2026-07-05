from __future__ import annotations

import streamlit as st

from config.process import STAGES
from ui.process import render_progress_card, render_stage_card, render_topbar


def dashboard_page() -> None:
    with st.container(key="dashboard_header"):
        intro, brand = st.columns([7, 3], gap="large", vertical_alignment="center")
        with intro:
            render_topbar()
            render_progress_card()
        with brand:
            st.markdown('<div class="dashboard-brand-mark" aria-label="CAS logo"></div>', unsafe_allow_html=True)
    st.markdown("## Process Steps")
    for stage in STAGES:
        render_stage_card(stage)
