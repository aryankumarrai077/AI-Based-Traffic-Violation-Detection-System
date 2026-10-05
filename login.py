"""
modules/login.py
-----------------
Renders the login screen. On success it sets st.session_state.authenticated
and reruns the app so app.py shows the dashboard + sidebar.
"""

import streamlit as st
from config import APP_NAME, APP_SHORT_NAME, DEMO_USERS


def render():
    # Center the login card using column ratios.
    st.markdown(
        """
        <style>
        .login-wrapper { display:flex; justify-content:center; margin-top:60px; }
        .login-card {
            background-color:#161b22;
            border:1px solid #232a35;
            border-radius:16px;
            padding:36px 40px;
            width:100%;
            max-width:420px;
            box-shadow:0 0 30px rgba(0,0,0,0.35);
        }
        .login-icon { font-size:42px; text-align:center; margin-bottom:6px;}
        .login-title { text-align:center; font-size:22px; font-weight:700; color:#ffffff;}
        .login-desc { text-align:center; font-size:13px; color:#9aa4b2; margin-bottom:22px;}
        .login-footer { text-align:center; font-size:12px; color:#6b7280; margin-top:16px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.3, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="login-icon">🚦🎥</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="login-title">{APP_SHORT_NAME}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="login-desc">{APP_NAME}<br>AI-based CCTV monitoring & violation detection</div>',
            unsafe_allow_html=True,
        )

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        login_clicked = st.button("Login", use_container_width=True)

        if login_clicked:
            user = DEMO_USERS.get(username.strip())
            if user and user["password"] == password:
                st.session_state.authenticated = True
                st.session_state.username = username.strip()
                st.session_state.full_name = user["full_name"]
                st.session_state.role = user["role"]
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.markdown('<div class="login-footer">🔒 Authorized personnel only</div>', unsafe_allow_html=True)
        with st.expander("Demo credentials"):
            st.caption("admin / admin123  •  officer / officer123")
        st.markdown("</div>", unsafe_allow_html=True)
