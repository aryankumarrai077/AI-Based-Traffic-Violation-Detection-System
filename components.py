"""
components.py
-------------
Small reusable rendering helpers so every page produces consistent
looking cards, badges and status dots instead of repeating raw HTML.
"""

import streamlit as st

STATUS_COLOR = {
    "Online": "green",
    "Active": "green",
    "Connected": "green",
    "Confirmed": "green",
    "Offline": "red",
    "Critical": "red",
    "Dismissed": "red",
    "Warning": "yellow",
    "Pending": "yellow",
    "Info": "blue",
    "Running": "blue",
    "Ready": "blue",
}


def badge(text, color=None):
    """Renders a small colored pill badge. Color auto-detected from text if not given."""
    color = color or STATUS_COLOR.get(text, "gray")
    st.markdown(f'<span class="badge badge-{color}">{text}</span>', unsafe_allow_html=True)


def badge_html(text, color=None):
    """Returns badge HTML as a string (for embedding inside tables/cards)."""
    color = color or STATUS_COLOR.get(text, "gray")
    return f'<span class="badge badge-{color}">{text}</span>'


def status_dot_html(text, color=None):
    color = color or STATUS_COLOR.get(text, "gray")
    return f'<span class="dot dot-{color}"></span>{text}'


def page_header(title, subtitle, status_text=None, status_color="green"):
    """Standard page header used at the top of every page."""
    col1, col2 = st.columns([4, 1.4])
    with col1:
        st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    if status_text:
        with col2:
            st.markdown(
                f'<div style="text-align:right; padding-top:14px;">'
                f'<span class="dot dot-{status_color}"></span>'
                f'<span style="font-weight:600; color:#e6e9ef;">{status_text}</span></div>',
                unsafe_allow_html=True,
            )
    st.markdown("<hr>", unsafe_allow_html=True)


def metric_card(label, value, sub_status=None, status_color="blue", trend=None):
    """A KPI card with a big number, label, status badge and optional trend."""
    trend_html = ""
    if trend is not None:
        cls = "metric-trend-up" if trend >= 0 else "metric-trend-down"
        arrow = "▲" if trend >= 0 else "▼"
        trend_html = f'<span class="{cls}">{arrow} {abs(trend)}%</span>'

    status_html = ""
    if sub_status:
        status_html = f'<span class="badge badge-{status_color}">{sub_status}</span>'

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
                {status_html}{trend_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_start(title=None):
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def card_end():
    st.markdown("</div>", unsafe_allow_html=True)
