# AI-Powered Illegal Parking Detection System — Dashboard Prototype

A Streamlit-only admin dashboard prototype for an academic (SIH-style) project.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Login with a demo account:
- `admin` / `admin123`
- `officer` / `officer123`

## Project structure

```
app.py                  # entry point: login gate + page routing
config.py               # app constants, demo credentials, DB/AI config placeholders
styles.py                # all custom CSS (dark CCTV theme), loaded once
components.py            # reusable UI helpers: cards, badges, page headers
database.py              # data access layer -> swap for real MySQL queries later
ai_engine.py              # AI access layer -> swap for real YOLO/OpenCV/OCR later
sample_data.py            # realistic demo data generator (used by database.py)
modules/
    login.py              # login screen
    sidebar.py             # persistent sidebar navigation + system status
    dashboard.py           # Dashboard page
    live_monitoring.py     # Live Monitoring page
    violations.py           # Violations page
    cameras.py               # Cameras page
    reports.py                # Reports & Analytics page
    settings.py                # Settings page
```

## Connecting real systems later

- **MySQL**: only `database.py` needs to change. Every function there
  currently calls `sample_data.py`; replace each function body with a
  real `mysql-connector-python` / SQLAlchemy query that returns the same
  list-of-dict shape. No UI code needs to change.
- **YOLO / OpenCV / OCR**: only `ai_engine.py` needs to change.
  `detect_vehicles()`, `read_number_plate()`, and `check_zone_violation()`
  are already isolated from the UI in `modules/live_monitoring.py`.
- **Camera streams**: `modules/live_monitoring.py` has a clearly marked
  webcam/RTSP integration point using `cv2.VideoCapture(...)`.

## Notes

- Color meaning is consistent everywhere: green = safe/active,
  red = violation/offline, yellow = warning/pending, blue = info.
- All data shown is realistic sample data generated in `sample_data.py`
  (seeded, so it stays consistent between reruns).
