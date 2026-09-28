"""
app.py
------
Entry point for the AI-Powered Illegal Parking Detection System dashboard.

Run with:
    streamlit run app.py

Responsibilities:
    1. Configure the page (title, icon, wide layout).
    2. Load global CSS.
    3. Gate access behind a login screen.
    4. Render the persistent sidebar + route to the selected page.
"""

import streamlit as st

from config import APP_NAME, APP_SHORT_NAME
from styles import load_css
from modules import login, sidebar, dashboard, live_monitoring, violations, cameras, reports, settings

st.set_page_config(
    page_title=f"{APP_SHORT_NAME} | Admin Dashboard",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# ------------------------------------------------------------------
# SESSION STATE DEFAULTS
# ------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ------------------------------------------------------------------
# ROUTING
# ------------------------------------------------------------------
PAGE_RENDERERS = {
    "Dashboard": dashboard.render,
    "Live Monitoring": live_monitoring.render,
    "Violations": violations.render,
    "Cameras": cameras.render,
    "Reports & Analytics": reports.render,
    "Settings": settings.render,
}

if not st.session_state.authenticated:
    login.render()
else:
    sidebar.render()
    current_page = st.session_state.get("page", "Dashboard")
    renderer = PAGE_RENDERERS.get(current_page, dashboard.render)
    renderer()
