"""
modules/reports.py
-------------------
Analytics dashboards: trend charts, distribution charts, AI performance
stats, a report table, and CSV export.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import database
from components import page_header, metric_card, card_start, card_end


PLOTLY_DARK_LAYOUT = dict(
    template="plotly_dark",
    plot_bgcolor="#161b22",
    paper_bgcolor="#161b22",
    margin=dict(l=10, r=10, t=30, b=10),
)


def render():
    page_header("Reports & Analytics", "Analyze parking violations and AI detection performance")

    # ---------------- DATE RANGE ----------------
    range_option = st.radio(
        "Date Range", ["Today", "Last 7 Days", "Last 30 Days", "Custom Date Range"], horizontal=True
    )
    days_map = {"Today": 1, "Last 7 Days": 7, "Last 30 Days": 30}
    if range_option == "Custom Date Range":
        c1, c2 = st.columns(2)
        with c1:
            st.date_input("From")
        with c2:
            st.date_input("To")
        days = 14
    else:
        days = days_map[range_option]

    violations = database.get_violations(n=150)
    report_rows = database.get_reports_table(days=max(days, 2))

    # ---------------- TOP METRICS ----------------
    total_violations = sum(r["Violations"] for r in report_rows)
    avg_per_day = round(total_violations / len(report_rows), 1)
    location_counts = pd.Series([v["location"] for v in violations]).value_counts()
    type_counts = pd.Series([v["violation_type"] for v in violations]).value_counts()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Violations", total_violations, sub_status="Info", status_color="blue")
    with c2:
        metric_card("Avg Violations / Day", avg_per_day, sub_status="Info", status_color="blue")
    with c3:
        metric_card("Most Violated Location", location_counts.idxmax(), sub_status="Alert", status_color="red")
    with c4:
        metric_card("Most Common Violation", type_counts.idxmax(), sub_status="Info", status_color="yellow")

    st.write("")

    # ---------------- CHARTS ROW 1 ----------------
    ch1, ch2 = st.columns(2)
    with ch1:
        card_start("Violations Over Time")
        df_time = pd.DataFrame(report_rows)
        fig = px.line(df_time, x="Date", y="Violations", markers=True, color_discrete_sequence=["#3b82f6"])
        fig.update_layout(**PLOTLY_DARK_LAYOUT, height=300)
        st.plotly_chart(fig, use_container_width=True)
        card_end()

    with ch2:
        card_start("Violations By Location")
        df_loc = location_counts.reset_index()
        df_loc.columns = ["Location", "Violations"]
        fig = px.bar(df_loc, x="Location", y="Violations", color="Location",
                     color_discrete_sequence=["#3b82f6", "#22c55e", "#f59e0b", "#ef4444"])
        fig.update_layout(**PLOTLY_DARK_LAYOUT, height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        card_end()

    # ---------------- CHARTS ROW 2 ----------------
    ch3, ch4 = st.columns(2)
    with ch3:
        card_start("Violation Type Distribution")
        df_type = type_counts.reset_index()
        df_type.columns = ["Violation Type", "Count"]
        fig = go.Figure(data=[go.Pie(
            labels=df_type["Violation Type"], values=df_type["Count"], hole=0.55,
            marker=dict(colors=["#ef4444", "#f59e0b", "#3b82f6", "#9aa4b2"]),
        )])
        fig.update_layout(**PLOTLY_DARK_LAYOUT, height=300)
        st.plotly_chart(fig, use_container_width=True)
        card_end()

    with ch4:
        card_start("Camera Performance (Violations Detected)")
        cam_counts = pd.Series([v["camera"] for v in violations]).value_counts().reset_index()
        cam_counts.columns = ["Camera", "Violations"]
        fig = px.bar(cam_counts, x="Camera", y="Violations", color="Camera",
                     color_discrete_sequence=["#3b82f6", "#22c55e", "#f59e0b", "#ef4444"])
        fig.update_layout(**PLOTLY_DARK_LAYOUT, height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        card_end()

    # ---------------- AI PERFORMANCE ----------------
    card_start("AI Performance")
    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        metric_card("Vehicle Detection Accuracy", "96.4%", status_color="green")
    with p2:
        metric_card("Plate Recognition Rate", "91.2%", status_color="green")
    with p3:
        metric_card("Avg Detection Confidence", "94.0%", status_color="green")
    with p4:
        metric_card("Avg Processing FPS", "28", status_color="blue")
    with p5:
        metric_card("Total Frames Processed", "1.24M", status_color="blue")
    card_end()

    # ---------------- REPORT TABLE ----------------
    card_start("Daily Report Table")
    df_report = pd.DataFrame(report_rows)
    st.dataframe(df_report, use_container_width=True, hide_index=True)
    card_end()

    # ---------------- EXPORT ----------------
    e1, e2 = st.columns(2)
    with e1:
        st.download_button(
            "⬇ Download CSV",
            data=df_report.to_csv(index=False),
            file_name="parking_violation_report.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with e2:
        if st.button("📄 Generate Report", use_container_width=True):
            st.success("Report generated (demo). Connect a PDF/export pipeline for a formatted document.")
