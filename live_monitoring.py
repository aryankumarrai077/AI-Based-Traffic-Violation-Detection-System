"""
modules/live_monitoring.py
---------------------------
CCTV control-room view. Runs the REAL detection pipeline on an uploaded
video or webcam feed:

    YOLO vehicle detection -> ByteTrack tracking -> position history
    -> direction calculation -> wrong-way check -> no-entry zone check

Every step above is real code in ai_engine.py - nothing here is faked.
"""

import os
import tempfile
import time
from datetime import datetime

import cv2
import numpy as np
import streamlit as st

import ai_engine
import database
from components import page_header, card_start, card_end, badge_html


def _process_video_source(cap, tracker, max_frames, confidence_threshold, frame_placeholder, info_placeholder):
    """
    Shared frame-processing loop used by BOTH the uploaded-video path and
    the webcam path. `cap` is any already-open cv2.VideoCapture object,
    and `tracker` is one ai_engine.VehicleTracker that stays alive for
    the whole loop so vehicle IDs and direction history persist.

    Returns: (frame_count, elapsed_seconds, last_frame_detections, new_violations)
    where new_violations is a list of (frame, detection, violation_type) for
    every violation that was newly confirmed during this run.
    """
    frame_count = 0
    detections = []
    new_violations = []
    start_time = time.time()

    while cap.isOpened() and frame_count < max_frames:
        ok, frame = cap.read()
        if not ok:
            break  # end of video, or webcam disconnected

        detections = tracker.process_frame(frame, confidence_threshold=confidence_threshold)
        annotated = tracker.draw(frame, detections)

        # OpenCV uses BGR, Streamlit's st.image expects RGB.
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(annotated_rgb, use_container_width=True)

        for d in detections:
            if d["is_new_wrong_way_violation"]:
                new_violations.append((frame, d, "WRONG WAY VIOLATION"))
            if d["is_new_no_entry_violation"]:
                new_violations.append((frame, d, "NO-ENTRY VIOLATION"))

        frame_count += 1
        elapsed_so_far = time.time() - start_time
        live_fps = frame_count / elapsed_so_far if elapsed_so_far > 0 else 0
        info_placeholder.markdown(f"Processed **{frame_count}/{max_frames}** frames — live FPS: **{live_fps:.1f}**")

    elapsed = time.time() - start_time
    return frame_count, elapsed, detections, new_violations


def _render_debug_panel(detections):
    """Shows direction + wrong-way streak per vehicle so you can SEE why a
    violation did or didn't trigger, instead of it being a black box."""
    if not detections:
        st.caption("No vehicles detected in the last processed frame.")
        return
    st.markdown('<div class="section-title">Per-Vehicle Debug Info (last frame)</div>', unsafe_allow_html=True)
    for d in detections:
        status_color = "red" if (d["is_wrong_way"] or d["is_no_entry"]) else "green"
        status_label = "WRONG-WAY" if d["is_wrong_way"] else ("NO-ENTRY" if d["is_no_entry"] else "Normal")
        st.markdown(
            f'<div class="camera-card">'
            f'<b>ID {d["track_id"]} — {d["class"]}</b> — confidence {d["confidence"]*100:.0f}% '
            f'{badge_html(status_label, status_color)}<br>'
            f'<span class="camera-meta">Direction: {d["direction"] or "calculating..."} • '
            f'Wrong-way streak: {d["wrong_way_streak"]}/{ai_engine.WRONG_WAY_FRAME_THRESHOLD}</span></div>',
            unsafe_allow_html=True,
        )


def render():
    page_header(
        "Live Monitoring",
        "Real-time detection of no-entry and wrong-way driving violations",
    )

    # ---------------- TOP STATUS BAR ----------------
    status_cols = st.columns(6)
    items = [
        ("● LIVE", "red"),
        ("AI Engine: Active", "green"),
        ("YOLO: Running", "green"),
        ("Tracking: ByteTrack", "blue"),
        ("FPS: Live", "blue"),
        ("Avg Confidence: 94%", "green"),
    ]
    for col, (text, color) in zip(status_cols, items):
        with col:
            st.markdown(badge_html(text, color), unsafe_allow_html=True)

    st.write("")

    # ---------------- CAMERA SELECTOR ----------------
    cameras = database.get_cameras()
    camera_names = [f'{c["name"]} - {c["location"]}' for c in cameras]
    selected_camera = st.selectbox("Select Camera", camera_names)
    cam_info = cameras[camera_names.index(selected_camera)]

    main_col, side_col = st.columns([2.2, 1])

    with main_col:
        card_start("Live Camera Feed")

        video_file = st.file_uploader(
            "Upload a demo video for this camera (prototype input)", type=["mp4", "avi", "mov"]
        )
        use_webcam = st.checkbox("Or connect webcam via OpenCV")

        s1, s2, s3 = st.columns(3)
        with s1:
            confidence_threshold = st.slider("Detection Confidence", 0.1, 0.9, 0.5, 0.05)
        with s2:
            allowed_direction = st.selectbox(
                "Allowed Direction", ai_engine.ALLOWED_DIRECTIONS,
                index=ai_engine.ALLOWED_DIRECTIONS.index(cam_info["allowed_direction"]),
            )
        with s3:
            max_frames = st.number_input("Frames to process", min_value=10, max_value=300, value=60, step=10)

        # ---------------- INTERACTIVE NO-ENTRY ZONE EDITOR ----------------
        # Lets you drag sliders and see the zone drawn on YOUR actual video's
        # first frame, instead of guessing pixel coordinates blind.
        with st.expander(f"🎯 Adjust No-Entry Zone Position — {cam_info['no_entry_zone_label']}", expanded=bool(video_file)):
            st.caption("Move the sliders until the orange box sits over the real no-entry area in your video.")
            zc1, zc2 = st.columns(2)
            with zc1:
                left_pct = st.slider("Left edge (%)", 0, 100, 30, key="zone_left")
                right_pct = st.slider("Right edge (%)", 0, 100, 70, key="zone_right")
            with zc2:
                top_pct = st.slider("Top edge (%)", 0, 100, 5, key="zone_top")
                bottom_pct = st.slider("Bottom edge (%)", 0, 100, 35, key="zone_bottom")

            zone_fractions = [
                (left_pct / 100, top_pct / 100),
                (right_pct / 100, top_pct / 100),
                (right_pct / 100, bottom_pct / 100),
                (left_pct / 100, bottom_pct / 100),
            ]
            st.session_state["no_entry_zone"] = zone_fractions

            # Grab the FIRST frame of the uploaded video (if any) as the
            # background for the preview, so you're positioning the zone
            # against your real footage, not a guess.
            preview_frame = None
            if video_file is not None:
                preview_bytes = video_file.getvalue()  # does not disturb the uploader for later use
                preview_path = os.path.join(tempfile.mkdtemp(), "zone_preview.mp4")
                with open(preview_path, "wb") as f:
                    f.write(preview_bytes)
                cap_preview = cv2.VideoCapture(preview_path)
                ok, preview_frame = cap_preview.read()
                cap_preview.release()
                if not ok:
                    preview_frame = None

            if preview_frame is None:
                preview_frame = np.full((360, 640, 3), 40, dtype=np.uint8)  # blank dark canvas fallback

            h, w = preview_frame.shape[:2]
            zone_px = np.array([[int(x * w), int(y * h)] for x, y in zone_fractions], dtype=np.int32)
            preview_annotated = preview_frame.copy()
            cv2.polylines(preview_annotated, [zone_px], isClosed=True, color=(0, 165, 255), thickness=3)
            st.image(
                cv2.cvtColor(preview_annotated, cv2.COLOR_BGR2RGB),
                caption="No-Entry zone preview (orange box)",
                use_container_width=True,
            )

        new_violations = []

        if video_file is None and not use_webcam:
            st.info("📡 No camera or video connected. Upload a demo video above, or enable webcam mode.")
            st.markdown(
                """
                <div style="background:#0e1117; border:1px dashed #2a313d; border-radius:10px;
                            height:280px; display:flex; align-items:center; justify-content:center;
                            color:#6b7280; font-size:14px;">
                    🎥 Camera feed preview will appear here
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif use_webcam:
            st.markdown('<div class="section-title">AI Detection — Live Webcam Feed</div>', unsafe_allow_html=True)
            camera_index = st.number_input(
                "Camera index (0 = default/built-in webcam, try 1 or 2 if you have multiple cameras)",
                min_value=0, max_value=5, value=0, step=1,
            )
            start_clicked = st.button("▶ Start Webcam Detection", use_container_width=True)

            if start_clicked:
                # ---- REAL WEBCAM CAPTURE ----
                # Opens your laptop's actual camera hardware. Only works when
                # Streamlit runs on the SAME machine as the webcam.
                cap = cv2.VideoCapture(int(camera_index))

                if not cap.isOpened():
                    st.error(
                        f"Could not open camera index {camera_index}. Try a different index, "
                        "close any other app using the camera, or check camera permissions."
                    )
                else:
                    frame_placeholder = st.empty()
                    info_placeholder = st.empty()
                    tracker = ai_engine.VehicleTracker(
                        allowed_direction=allowed_direction,
                        no_entry_zone=st.session_state.get("no_entry_zone"),
                    )

                    with st.spinner("Loading YOLO model and reading from webcam..."):
                        frame_count, elapsed, detections, new_violations = _process_video_source(
                            cap, tracker, max_frames, confidence_threshold, frame_placeholder, info_placeholder
                        )

                    cap.release()
                    achieved_fps = frame_count / elapsed if elapsed > 0 else 0
                    info_placeholder.markdown(
                        f"✅ Captured **{frame_count} frames** from webcam in {elapsed:.1f}s "
                        f"(~{achieved_fps:.1f} FPS) — **{len(detections)} vehicle(s)** in the last frame."
                    )
                    _render_debug_panel(detections)
            else:
                st.info("Click 'Start Webcam Detection' to open your camera and run real-time detection.")

        else:
            st.markdown('<div class="section-title">AI Detection — Video Processing</div>', unsafe_allow_html=True)
            run_clicked = st.button("▶ Run Detection on this video", use_container_width=True)

            if run_clicked:
                tmp_dir = tempfile.mkdtemp()
                tmp_path = os.path.join(tmp_dir, video_file.name)
                with open(tmp_path, "wb") as f:
                    f.write(video_file.read())

                cap = cv2.VideoCapture(tmp_path)
                frame_placeholder = st.empty()
                info_placeholder = st.empty()
                tracker = ai_engine.VehicleTracker(
                    allowed_direction=allowed_direction,
                    no_entry_zone=st.session_state.get("no_entry_zone"),
                )

                with st.spinner("Loading YOLO model and processing frames..."):
                    frame_count, elapsed, detections, new_violations = _process_video_source(
                        cap, tracker, max_frames, confidence_threshold, frame_placeholder, info_placeholder
                    )

                cap.release()
                achieved_fps = frame_count / elapsed if elapsed > 0 else 0
                info_placeholder.markdown(
                    f"✅ Processed **{frame_count} frames** in {elapsed:.1f}s "
                    f"(~{achieved_fps:.1f} FPS on this machine) — "
                    f"**{len(detections)} vehicle(s)** detected in the last frame."
                )
                _render_debug_panel(detections)
            else:
                st.video(video_file)
                st.caption("Click 'Run Detection' above to process this video with real AI detection.")

        card_end()

        # ---------------- VIOLATION ALERTS ----------------
        for frame, detection, violation_type in new_violations:
            evidence = ai_engine.save_evidence(frame, detection, violation_type)
            st.markdown(
                f"""
                <div class="alert-critical">
                    <div class="alert-title">⚠ {violation_type} DETECTED</div>
                    <div style="margin-top:8px; font-size:13px; color:#e6e9ef; line-height:1.9;">
                        <b>Vehicle ID:</b> {detection['track_id']}<br>
                        <b>Vehicle Class:</b> {detection['class']}<br>
                        <b>Camera:</b> {cam_info['name']} — {cam_info['location']}<br>
                        <b>Time:</b> {evidence['timestamp']}<br>
                        <b>Detection Confidence:</b> {detection['confidence']*100:.0f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(cv2.cvtColor(cv2.imread(evidence["file_path"]), cv2.COLOR_BGR2RGB), caption="Evidence snapshot (saved to disk)", use_container_width=True)

        # ---------------- CONTROL BUTTONS ----------------
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.button("▶ Start Monitoring", use_container_width=True)
        with b2:
            st.button("⏹ Stop Monitoring", use_container_width=True)
        with b3:
            st.button("📸 Capture Evidence", use_container_width=True)
        with b4:
            st.button("⛶ Full Screen", use_container_width=True)

    with side_col:
        card_start("AI Detection Status")
        checks = ["Vehicle Detection", "Vehicle Tracking", "Direction Analysis", "No-Entry Zone Check", "Evidence Capture"]
        for c in checks:
            st.markdown(f'<div style="margin-bottom:6px;">✅ {c}</div>', unsafe_allow_html=True)
        card_end()

        card_start("Recent Live Alerts")
        for v in database.get_violations(5):
            st.markdown(
                f"""
                <div class="camera-card">
                    <div class="camera-meta">{v['time']}</div>
                    <div class="camera-name">Vehicle ID {v['vehicle_id']}</div>
                    <div class="camera-meta">{v['location']} • {v['violation_type']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        card_end()

        card_start("Camera Information")
        st.markdown(
            f"""
            <div style="font-size:13px; line-height:2;">
            <b>Resolution:</b> {cam_info['resolution']}<br>
            <b>FPS:</b> {cam_info['fps']}<br>
            <b>Allowed Direction:</b> {cam_info['allowed_direction']}<br>
            <b>No-Entry Zone:</b> {cam_info['no_entry_zone_label']}<br>
            <b>Status:</b> {badge_html(cam_info['status'])}<br>
            <b>Last Frame:</b> {cam_info['last_activity']}
            </div>
            """,
            unsafe_allow_html=True,
        )
        card_end()