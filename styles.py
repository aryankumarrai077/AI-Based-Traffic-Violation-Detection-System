"""
styles.py
---------
All custom CSS lives here and is injected once via st.markdown().
Keeping it centralized means every page looks consistent.
"""

import streamlit as st


def load_css():
    st.markdown(
        """
        <style>
        /* ---------------- GLOBAL ---------------- */
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }
        .stApp {
            background-color: #0e1117;
            color: #e6e9ef;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* ---------------- SIDEBAR ---------------- */
        section[data-testid="stSidebar"] {
            background-color: #10141b;
            border-right: 1px solid #232a35;
        }
        .sidebar-logo {
            font-size: 20px;
            font-weight: 700;
            color: #e6e9ef;
            padding: 6px 0 0 0;
        }
        .sidebar-sub {
            font-size: 12px;
            color: #9aa4b2;
            margin-bottom: 14px;
        }
        .sidebar-section-label {
            font-size: 11px;
            letter-spacing: 1px;
            color: #6b7280;
            text-transform: uppercase;
            margin: 14px 0 4px 4px;
        }

        /* ---------------- PAGE HEADER ---------------- */
        .page-title {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 2px;
        }
        .page-subtitle {
            font-size: 14px;
            color: #9aa4b2;
            margin-bottom: 6px;
        }

        /* ---------------- STATUS BADGES ---------------- */
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }
        .badge-green { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.4);}
        .badge-red { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.4);}
        .badge-yellow { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.4);}
        .badge-blue { background: rgba(59,130,246,0.15); color: #3b82f6; border: 1px solid rgba(59,130,246,0.4);}
        .badge-gray { background: rgba(156,163,175,0.15); color: #9ca3af; border: 1px solid rgba(156,163,175,0.4);}

        .dot { height:9px; width:9px; border-radius:50%; display:inline-block; margin-right:6px;}
        .dot-green { background-color:#22c55e; box-shadow: 0 0 6px #22c55e;}
        .dot-red { background-color:#ef4444; box-shadow: 0 0 6px #ef4444;}
        .dot-yellow { background-color:#f59e0b; box-shadow: 0 0 6px #f59e0b;}
        .dot-blue { background-color:#3b82f6; box-shadow: 0 0 6px #3b82f6;}

        /* ---------------- CARDS ---------------- */
        .app-card {
            background-color: #161b22;
            border: 1px solid #232a35;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 14px;
        }
        .metric-card {
            background-color: #161b22;
            border: 1px solid #232a35;
            border-radius: 12px;
            padding: 16px 18px;
        }
        .metric-value {
            font-size: 30px;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.1;
        }
        .metric-label {
            font-size: 13px;
            color: #9aa4b2;
            margin-top: 2px;
        }
        .metric-trend-up { color: #22c55e; font-size: 12px; font-weight: 600;}
        .metric-trend-down { color: #ef4444; font-size: 12px; font-weight: 600;}

        .section-title {
            font-size: 16px;
            font-weight: 700;
            color: #e6e9ef;
            margin-bottom: 8px;
        }

        /* ---------------- CAMERA CARD ---------------- */
        .camera-card {
            background-color: #161b22;
            border: 1px solid #232a35;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }
        .camera-name { font-weight: 700; font-size: 14px; color: #e6e9ef;}
        .camera-meta { font-size: 12px; color: #9aa4b2; }

        /* ---------------- ALERT BOX ---------------- */
        .alert-critical {
            background: rgba(239,68,68,0.12);
            border: 1px solid #ef4444;
            border-left: 5px solid #ef4444;
            border-radius: 10px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }
        .alert-title { color: #ef4444; font-weight: 700; font-size: 16px; }

        /* ---------------- TABLE STYLING (dataframe container) ---------------- */
        .stDataFrame { border: 1px solid #232a35; border-radius: 8px; }

        /* ---------------- BUTTONS ---------------- */
        .stButton>button {
            background-color: #1c222b;
            color: #e6e9ef;
            border: 1px solid #2a313d;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }
        .stButton>button:hover {
            border-color: #3b82f6;
            color: #3b82f6;
        }

        /* nav button active look handled via container styling in sidebar.py */
        div[data-testid="stVerticalBlock"] .nav-active button {
            border-color: #3b82f6 !important;
            color: #3b82f6 !important;
        }

        hr { border-color: #232a35; }
        </style>
        """,
        unsafe_allow_html=True,
    )
