"""
modules/cameras.py
-------------------
Camera management: grid of camera cards, detail panel, and an
"add camera" form (placeholder for real OpenCV/RTSP connection).
"""

import streamlit as st

import database
from components import page_header, metric_card, card_start, card_end, badge_html


def render():
    page_header("Camera Management", "Monitor connected cameras and their operational status")

    cameras = database.get_cameras()
    total = len(cameras)
    online = sum(1 for c in cameras if c["status"] == "Online")
    offline = total - online
    with_alerts = 1  # placeholder demo value

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Cameras", total, sub_status="Info", status_color="blue")
    with c2:
        metric_card("Online Cameras", online, sub_status="Online", status_color="green")
    with c3:
        metric_card("Offline Cameras", offline, sub_status="Offline" if offline else "None", status_color="red" if offline else "green")
    with c4:
        metric_card("Cameras With Alerts", with_alerts, sub_status="Warning", status_color="yellow")

    st.write("")

    # ---------------- CAMERA GRID ----------------
    st.markdown('<div class="section-title">Camera Grid</div>', unsafe_allow_html=True)
    grid_cols = st.columns(2)
    selected_camera_id = st.session_state.get("selected_camera_id", cameras[0]["id"])

    for i, cam in enumerate(cameras):
        col = grid_cols[i % 2]
        with col:
            color = "green" if cam["status"] == "Online" else "red"
            st.markdown(
                f"""
                <div class="camera-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="camera-name">{cam['name']}</div>
                        {badge_html(cam['status'], color)}
                    </div>
                    <div class="camera-meta">📍 {cam['location']}</div>
                    <div class="camera-meta">Allowed direction: {cam['allowed_direction']} • FPS: {cam['fps']} • {cam['resolution']}</div>
                    <div class="camera-meta">No-Entry Zone: {cam['no_entry_zone_label']}</div>
                    <div class="camera-meta">Last activity: {cam['last_activity']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            b1, b2 = st.columns(2)
            with b1:
                if st.button("👁 View Camera", key=f"view_{cam['id']}", use_container_width=True):
                    st.session_state.selected_camera_id = cam["id"]
                    st.rerun()
            with b2:
                st.button("⚙ Settings", key=f"settings_{cam['id']}", use_container_width=True)

    st.write("")

    # ---------------- CAMERA DETAILS ----------------
    selected = next((c for c in cameras if c["id"] == st.session_state.get("selected_camera_id", cameras[0]["id"])), cameras[0])
    card_start(f"Camera Details — {selected['name']}")
    color = "green" if selected["status"] == "Online" else "red"
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(
            f"""
            <div style="font-size:14px; line-height:2.1;">
            <b>Camera ID:</b> {selected['id']}<br>
            <b>Location:</b> {selected['location']}<br>
            <b>Source:</b> {selected['source']}<br>
            <b>Camera Type:</b> {selected['camera_type']}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with d2:
        st.markdown(
            f"""
            <div style="font-size:14px; line-height:2.1;">
            <b>Resolution:</b> {selected['resolution']}<br>
            <b>FPS:</b> {selected['fps']}<br>
            <b>Allowed Direction:</b> {selected['allowed_direction']}<br>
            <b>No-Entry Zone:</b> {selected['no_entry_zone_label']}<br>
            <b>Connection Status:</b> {badge_html(selected['status'], color)}<br>
            <b>AI Detection:</b> {badge_html('Active','green') if selected['status']=='Online' else badge_html('Paused','red')}
            </div>
            """,
            unsafe_allow_html=True,
        )
    card_end()

    # ---------------- ADD CAMERA FORM ----------------
    card_start("Add New Camera")
    with st.form("add_camera_form", clear_on_submit=True):
        n1, n2 = st.columns(2)
        with n1:
            name = st.text_input("Camera Name", placeholder="e.g. Camera 05")
            source = st.text_input("Camera Source / IP / URL", placeholder="rtsp://192.168.1.20:554/stream1")
            allowed_direction = st.selectbox("Allowed Direction", ["UP", "DOWN", "LEFT", "RIGHT"])
        with n2:
            location = st.text_input("Camera Location", placeholder="e.g. Library Gate")
            resolution = st.selectbox("Resolution", ["1920x1080", "1280x720", "640x480"])
            no_entry_label = st.text_input("No-Entry Zone Description", placeholder="e.g. Staff-only entrance")
        camera_type = st.selectbox("Camera Type", ["IP Camera", "USB Webcam", "DVR Channel"])

        s1, s2 = st.columns(2)
        with s1:
            submitted = st.form_submit_button("➕ Add Camera", use_container_width=True)
        with s2:
            tested = st.form_submit_button("🔌 Test Connection", use_container_width=True)

        if submitted:
            st.success(f"Camera '{name or 'Unnamed'}' saved (demo mode — connect MySQL to persist).")
        if tested:
            st.info("Connection test placeholder — will use OpenCV `cv2.VideoCapture(source)` once wired to real hardware.")
    card_end()
