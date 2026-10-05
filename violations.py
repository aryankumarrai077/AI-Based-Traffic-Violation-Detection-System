"""
modules/violations.py
----------------------
Search, filter, review and manage detected traffic violations
(No-Entry and Wrong-Way Driving).
"""

import streamlit as st
import pandas as pd

import database
from components import page_header, metric_card, card_start, card_end, badge_html


def render():
    page_header("Traffic Violations", "Review and manage detected no-entry and wrong-way violations")

    violations = database.get_violations()

    # ---------------- TOP METRICS ----------------
    total = len(violations)
    today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
    today_count = sum(1 for v in violations if v["date"] == today_str)
    pending = sum(1 for v in violations if v["status"] == "Pending")
    confirmed = sum(1 for v in violations if v["status"] == "Confirmed")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Violations", total, sub_status="Info", status_color="blue")
    with c2:
        metric_card("Today's Violations", today_count, sub_status="Warning", status_color="yellow")
    with c3:
        metric_card("Pending Review", pending, sub_status="Pending", status_color="yellow")
    with c4:
        metric_card("Confirmed Violations", confirmed, sub_status="Confirmed", status_color="green")

    st.write("")

    # ---------------- FILTERS ----------------
    card_start("Filters")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        cameras = ["All"] + sorted({v["camera"] for v in violations})
        camera_filter = st.selectbox("Camera", cameras)
    with f2:
        locations = ["All"] + sorted({v["location"] for v in violations})
        location_filter = st.selectbox("Location", locations)
    with f3:
        types = ["All"] + sorted({v["violation_type"] for v in violations})
        type_filter = st.selectbox("Violation Type", types)
    with f4:
        status_filter = st.selectbox("Status", ["All", "Pending", "Confirmed", "Dismissed"])

    f5, f6 = st.columns([2, 2])
    with f5:
        date_filter = st.date_input("Date", value=None)
    with f6:
        search_id = st.text_input("Search Vehicle ID", placeholder="e.g. 7")
    card_end()

    # ---------------- APPLY FILTERS ----------------
    filtered = violations
    if camera_filter != "All":
        filtered = [v for v in filtered if v["camera"] == camera_filter]
    if location_filter != "All":
        filtered = [v for v in filtered if v["location"] == location_filter]
    if type_filter != "All":
        filtered = [v for v in filtered if v["violation_type"] == type_filter]
    if status_filter != "All":
        filtered = [v for v in filtered if v["status"] == status_filter]
    if date_filter:
        filtered = [v for v in filtered if v["date"] == str(date_filter)]
    if search_id:
        filtered = [v for v in filtered if search_id.strip() == str(v["vehicle_id"])]

    # ---------------- VIOLATION TABLE ----------------
    card_start(f"Violation Records ({len(filtered)})")
    df = pd.DataFrame(
        [
            {
                "ID": v["id"],
                "Vehicle ID": v["vehicle_id"],
                "Violation": v["violation_type"],
                "Location": v["location"],
                "Camera": v["camera"],
                "Date": v["date"],
                "Time": v["time"],
                "Confidence": f'{v["confidence"]*100:.0f}%',
                "Status": v["status"],
            }
            for v in filtered
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True, height=320)
    card_end()

    # ---------------- DETAIL PANEL ----------------
    card_start("Violation Detail")
    ids = [v["id"] for v in filtered] or [v["id"] for v in violations]
    selected_id = st.selectbox("Select a Violation ID to inspect", ids)
    selected = next((v for v in violations if v["id"] == selected_id), None)

    if selected:
        d1, d2 = st.columns([1, 1.3])
        with d1:
            st.markdown(
                """
                <div style="background:#0e1117; border:1px dashed #2a313d; border-radius:10px;
                            height:220px; display:flex; align-items:center; justify-content:center;
                            color:#6b7280; font-size:13px;">
                    📷 Evidence image placeholder<br>(real captures save to /evidence via Live Monitoring)
                </div>
                """,
                unsafe_allow_html=True,
            )
        with d2:
            color = "green" if selected["status"] == "Confirmed" else ("red" if selected["status"] == "Dismissed" else "yellow")
            st.markdown(
                f"""
                <div style="font-size:14px; line-height:2.1;">
                <b>Vehicle ID:</b> {selected['vehicle_id']}<br>
                <b>Violation Type:</b> {selected['violation_type']}<br>
                <b>Camera:</b> {selected['camera']}<br>
                <b>Location:</b> {selected['location']}<br>
                <b>Date / Time:</b> {selected['date']} {selected['time']}<br>
                <b>Detection Confidence:</b> {selected['confidence']*100:.0f}%<br>
                <b>Status:</b> {badge_html(selected['status'], color)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        a1, a2, a3, a4 = st.columns(4)
        with a1:
            st.button("✅ Confirm Violation", use_container_width=True, key="confirm_btn")
        with a2:
            st.button("❌ Dismiss Violation", use_container_width=True, key="dismiss_btn")
        with a3:
            st.button("💾 Save Evidence", use_container_width=True, key="save_btn")
        with a4:
            st.download_button(
                "⬇ Export Record",
                data=pd.DataFrame([selected]).to_csv(index=False),
                file_name=f"{selected['id']}.csv",
                mime="text/csv",
                use_container_width=True,
            )
    card_end()

    # ---------------- RECENT EVIDENCE GRID ----------------
    card_start("Recent Evidence")
    grid = st.columns(4)
    for col in grid:
        with col:
            st.markdown(
                """
                <div style="background:#0e1117; border:1px dashed #2a313d; border-radius:10px;
                            height:110px; display:flex; align-items:center; justify-content:center;
                            color:#6b7280; font-size:12px;">📷 Evidence</div>
                """,
                unsafe_allow_html=True,
            )
    card_end()
