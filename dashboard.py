"""
modules/dashboard.py
---------------------
Main overview page: KPI cards, violation trend chart, camera status,
recent violations table, AI system status, and quick actions.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import database
import ai_engine
from components import page_header, metric_card, card_start, card_end, badge_html


def render():
    page_header(
        "AI Traffic Violation Dashboard",
        "Real-time overview of no-entry and wrong-way driving violations",
        status_text="AI SYSTEM ONLINE",
        status_color="green",
    )

    violations = database.get_violations()
    metrics = database.get_dashboard_metrics(violations)

    # ---------------- TOP METRIC CARDS ----------------
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Total Vehicles Detected",
            f'{metrics["total_vehicles_detected"]:,}',
            sub_status="Active", status_color="green", trend=4.2,
        )
    with c2:
        metric_card(
            "Total No-Entry Violations",
            metrics["total_no_entry"],
            sub_status="Warning", status_color="red",
        )
    with c3:
        metric_card(
            "Total Wrong-Way Violations",
            metrics["total_wrong_way"],
            sub_status="Warning", status_color="red",
        )
    with c4:
        metric_card(
            "Pending Reviews",
            metrics["pending_reviews"],
            sub_status="Needs Action", status_color="yellow",
        )

    st.write("")

    # ---------------- MAIN TWO-COLUMN SECTION ----------------
    left, right = st.columns([2, 1.1])

    with left:
        card_start("Violation Overview — Last 7 Days")
        trend = database.get_weekly_violation_trend()
        df = pd.DataFrame(trend)

        fig = go.Figure()
        colors = {
            "No-Entry Violation": "#ef4444",
            "Wrong-Way Violation": "#f59e0b",
        }
        for col in df.columns[1:]:
            fig.add_trace(go.Bar(x=df["day"], y=df[col], name=col, marker_color=colors.get(col, "#9aa4b2")))

        fig.update_layout(
            barmode="stack",
            template="plotly_dark",
            plot_bgcolor="#161b22",
            paper_bgcolor="#161b22",
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)
        card_end()

    with right:
        card_start("Camera Status")
        cameras = database.get_cameras()
        for cam in cameras:
            color = "green" if cam["status"] == "Online" else "red"
            st.markdown(
                f"""
                <div class="camera-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="camera-name">{cam['name']} — {cam['location']}</div>
                        {badge_html(cam['status'], color)}
                    </div>
                    <div class="camera-meta">Allowed direction: {cam['allowed_direction']} • FPS: {cam['fps']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        card_end()

    # ---------------- RECENT VIOLATIONS TABLE ----------------
    card_start("Recent Violations")
    recent = violations[:8]
    table_df = pd.DataFrame(
        [
            {
                "Violation ID": v["id"],
                "Vehicle ID": v["vehicle_id"],
                "Violation Type": v["violation_type"],
                "Location": v["location"],
                "Time": f'{v["date"]} {v["time"]}',
                "Status": v["status"],
            }
            for v in recent
        ]
    )
    st.dataframe(table_df, use_container_width=True, hide_index=True)
    card_end()

    # ---------------- AI SYSTEM STATUS ----------------
    card_start("AI System Status")
    status = ai_engine.get_engine_status()
    cols = st.columns(len(status))
    for col, (module, state) in zip(cols, status.items()):
        color = "green" if state in ("Active", "Connected") else "red"
        with col:
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div style="font-size:13px; color:#9aa4b2;">{module}</div>'
                f'<div style="margin-top:6px;">{badge_html(state, color)}</div></div>',
                unsafe_allow_html=True,
            )
    card_end()

    # ---------------- QUICK ACTIONS ----------------
    st.write("")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("🎥 Open Live Monitoring", use_container_width=True):
            st.session_state.page = "Live Monitoring"
            st.rerun()
    with q2:
        if st.button("🚫 View Violations", use_container_width=True):
            st.session_state.page = "Violations"
            st.rerun()
    with q3:
        if st.button("📈 View Reports", use_container_width=True):
            st.session_state.page = "Reports & Analytics"
            st.rerun()
