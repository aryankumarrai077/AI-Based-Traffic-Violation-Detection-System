"""
modules/sidebar.py
-------------------
Renders the sidebar that appears identically on every authenticated page:
logo, navigation buttons, quick system status, and logout.
"""

import streamlit as st
from config import APP_SHORT_NAME, NAV_ITEMS
import ai_engine


def render():
    with st.sidebar:
        st.markdown(f'<div class="sidebar-logo">🚦🎥 {APP_SHORT_NAME}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-sub">No-Entry & Wrong-Way Detection</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)

        current_page = st.session_state.get("page", "Dashboard")
        for label, icon in NAV_ITEMS:
            is_active = current_page == label
            btn_label = f"{icon}  {label}"
            if st.button(btn_label, key=f"nav_{label}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.page = label
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-label">System Status</div>', unsafe_allow_html=True)

        status = ai_engine.get_engine_status()
        for module, state in status.items():
            color = "green" if state in ("Active", "Connected") else "red"
            st.markdown(
                f'<div style="font-size:12px; margin-bottom:4px; color:#c7ccd4;">'
                f'<span class="dot dot-{color}"></span>{module}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:12px; color:#9aa4b2;">Logged in as<br>'
            f'<b style="color:#e6e9ef;">{st.session_state.get("full_name","Administrator")}</b><br>'
            f'{st.session_state.get("role","Administrator")}</div>',
            unsafe_allow_html=True,
        )

        if st.button("🚪 Logout", use_container_width=True):
            for key in ("authenticated", "username", "full_name", "role", "page"):
                st.session_state.pop(key, None)
            st.rerun()
