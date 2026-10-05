"""
modules/settings.py
--------------------
System configuration: AI detection, zones & direction, cameras,
notifications, database, admin profile, and system info.
"""

import sys
import streamlit as st

import database
from config import APP_VERSION, AI_CONFIG, ALLOWED_DIRECTIONS
from components import page_header, card_start, card_end, badge_html


def render():
    page_header("System Settings", "Configure monitoring, AI detection, and administrator preferences")

    # ---------------- 1. AI DETECTION SETTINGS ----------------
    card_start("1. AI Detection Settings")
    a1, a2 = st.columns(2)
    with a1:
        st.checkbox("Enable Vehicle Detection", value=True)
        st.checkbox("Enable No-Entry Detection", value=True)
    with a2:
        st.checkbox("Enable Wrong-Way Detection", value=True)
        st.checkbox("Enable Evidence Capture", value=True)
    st.slider("Detection Confidence Threshold", 0.0, 1.0, AI_CONFIG["default_confidence_threshold"], 0.01)
    card_end()

    # ---------------- 2. ZONE & DIRECTION SETTINGS ----------------
    card_start("2. Zone & Direction Settings")
    cameras = database.get_cameras()
    z1, z2 = st.columns(2)
    with z1:
        st.selectbox("Camera", [c["name"] for c in cameras], key="zone_camera_select")
        st.selectbox("Allowed Direction", ALLOWED_DIRECTIONS)
        st.text_input("No-Entry Zone Description", value="Staff-only entrance")
    with z2:
        st.slider("Wrong-Way Consecutive-Frame Threshold", 1, 20, AI_CONFIG["wrong_way_frame_threshold"])
        st.slider("Movement Sensitivity (min pixels to register movement)", 1, 30, 8)
    st.caption("No-Entry zone shape is configured as a polygon in ai_engine.py for this prototype - "
               "a drag-to-draw zone editor is a good next feature to add.")
    card_end()

    # ---------------- 3. CAMERA SETTINGS ----------------
    card_start("3. Camera Settings")
    cameras = database.get_cameras()
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Default Camera", [c["name"] for c in cameras])
        st.selectbox("Resolution", ["1920x1080", "1280x720", "640x480"])
    with c2:
        st.slider("FPS", 10, 60, 30)
        st.number_input("Camera Timeout (seconds)", min_value=5, max_value=120, value=30)
    st.checkbox("Auto Reconnect on Disconnection", value=True)
    card_end()

    # ---------------- 4. NOTIFICATION SETTINGS ----------------
    card_start("4. Notification Settings")
    n1, n2 = st.columns(2)
    with n1:
        st.checkbox("Enable Violation Alerts", value=True)
        st.checkbox("Enable Sound Alert", value=False)
    with n2:
        st.checkbox("Enable Dashboard Notifications", value=True)
        st.checkbox("Enable Email Notifications", value=False)
    card_end()

    # ---------------- 5. DATABASE SETTINGS ----------------
    card_start("5. Database Settings")
    db_status = database.get_connection_status()
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f"**Database Status**<br>{badge_html('Connected' if db_status['connected'] else 'Offline')}", unsafe_allow_html=True)
    with d2:
        st.markdown(f"**Engine**<br>{db_status['engine']}", unsafe_allow_html=True)
    with d3:
        st.markdown(f"**Last Sync**<br>{db_status['last_sync']}", unsafe_allow_html=True)
    st.caption("Credentials are managed securely in config.py / environment variables — never shown here.")
    card_end()

    # ---------------- 6. ADMIN PROFILE ----------------
    card_start("6. Admin Profile")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            f"""
            <div style="line-height:2.1; font-size:14px;">
            <b>Name:</b> {st.session_state.get('full_name', 'System Administrator')}<br>
            <b>Role:</b> {st.session_state.get('role', 'Administrator')}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """
            <div style="line-height:2.1; font-size:14px;">
            <b>Email:</b> admin@parkguard.ai<br>
            <b>Last Login:</b> Today, 09:14 AM
            </div>
            """,
            unsafe_allow_html=True,
        )
    card_end()

    # ---------------- 7. SYSTEM INFORMATION ----------------
    card_start("7. System Information")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"**Application Version**<br>{APP_VERSION}", unsafe_allow_html=True)
        st.markdown(f"**Python Version**<br>{sys.version.split()[0]}", unsafe_allow_html=True)
    with s2:
        st.markdown(f"**Streamlit Version**<br>{st.__version__}", unsafe_allow_html=True)
        st.markdown(f"**YOLO Model**<br>{AI_CONFIG['yolo_model_path'].split('/')[-1]}", unsafe_allow_html=True)
    with s3:
        st.markdown("**OpenCV Version**<br>4.9.0 (planned)", unsafe_allow_html=True)
        st.markdown(f"**Database**<br>{badge_html('Connected')}", unsafe_allow_html=True)
    card_end()

    # ---------------- BOTTOM BUTTONS ----------------
    b1, b2 = st.columns(2)
    with b1:
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("Settings saved (demo mode — will persist to MySQL once connected).")
    with b2:
        if st.button("↩ Reset Settings", use_container_width=True):
            st.warning("Settings reset to default values (demo mode).")
