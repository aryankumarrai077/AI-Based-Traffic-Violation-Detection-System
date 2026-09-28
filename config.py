"""
config.py
---------
Central place for all project-wide settings.

Keeping configuration in one file makes it easy to later switch from
demo/sample data to a real MySQL database and a real YOLO/OpenCV/OCR
pipeline without touching the UI code.
"""

# ----------------------------------------------------------------------
# APP INFO
# ----------------------------------------------------------------------
APP_NAME = "AI-Powered Illegal Parking Detection System"
APP_SHORT_NAME = "ParkGuard AI"
APP_VERSION = "1.0.0-prototype"

# ----------------------------------------------------------------------
# DEMO LOGIN CREDENTIALS (for prototype / academic demo only)
# In production these must come from a hashed-password table in MySQL,
# never stored in plain text like this.
# ----------------------------------------------------------------------
DEMO_USERS = {
    "admin": {
        "password": "admin123",
        "full_name": "System Administrator",
        "role": "Administrator",
        "email": "admin@parkguard.ai",
    },
    "officer": {
        "password": "officer123",
        "full_name": "Traffic Officer",
        "role": "Monitoring Officer",
        "email": "officer@parkguard.ai",
    },
}

# ----------------------------------------------------------------------
# DATABASE CONFIG (placeholders only - connect a real MySQL DB later)
# ----------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "parkguard_user",
    "password": "",            # never hard-code real passwords
    "database": "parking_detection_db",
}

# ----------------------------------------------------------------------
# AI / MODEL CONFIG (placeholders for future YOLO / OpenCV / OCR wiring)
# ----------------------------------------------------------------------
AI_CONFIG = {
    "yolo_model_path": "models/yolov8_vehicle.pt",
    "ocr_engine": "EasyOCR",
    "default_confidence_threshold": 0.50,
    "opencv_backend": "cv2.CAP_FFMPEG",
}

# ----------------------------------------------------------------------
# NAVIGATION
# ----------------------------------------------------------------------
NAV_ITEMS = [
    ("Dashboard", "📊"),
    ("Live Monitoring", "🎥"),
    ("Violations", "🚫"),
    ("Cameras", "📷"),
    ("Reports & Analytics", "📈"),
    ("Settings", "⚙️"),
]

# ----------------------------------------------------------------------
# COLOR SYSTEM (meaning must stay consistent across the whole app)
# ----------------------------------------------------------------------
COLORS = {
    "bg_primary": "#0e1117",
    "bg_secondary": "#161b22",
    "bg_card": "#1c222b",
    "border": "#2a313d",
    "text_primary": "#e6e9ef",
    "text_secondary": "#9aa4b2",
    "accent_blue": "#3b82f6",
    "safe_green": "#22c55e",
    "critical_red": "#ef4444",
    "warning_yellow": "#f59e0b",
    "info_blue": "#3b82f6",
}
