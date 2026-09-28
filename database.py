import os
import random
import sqlite3
from datetime import datetime, timedelta

# 1. CONNECTION HELPER

# The .db file will be created in the same folder as this script.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parking.db")


def get_connection():
    """
    Opens a connection to the SQLite database file.
    `row_factory = sqlite3.Row` lets us access columns by name
    (like a dictionary) instead of by position - much easier to work with.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _rows_to_dicts(rows):
    """Converts a list of sqlite3.Row objects into a list of dictionaries."""
    return [dict(row) for row in rows]


def _create_tables(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cameras (
            id            TEXT PRIMARY KEY,
            name          TEXT NOT NULL,
            location      TEXT NOT NULL,
            status        TEXT NOT NULL DEFAULT 'Online',
            fps           INTEGER DEFAULT 0,
            resolution    TEXT DEFAULT 'Unknown',
            last_activity TEXT DEFAULT 'just now',
            source        TEXT,
            camera_type   TEXT DEFAULT 'IP Camera'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS violations (
            id                TEXT PRIMARY KEY,
            vehicle_number    TEXT NOT NULL,
            violation_type    TEXT NOT NULL,
            location          TEXT NOT NULL,
            camera            TEXT NOT NULL,
            datetime          TEXT NOT NULL,   -- stored as ISO text, e.g. 2026-09-17T21:45:00
            confidence        REAL DEFAULT 0,
            plate_confidence  REAL DEFAULT 0,
            status            TEXT DEFAULT 'Pending'
        )
        """
    )
    conn.commit()


def _seed_demo_data_if_empty(conn):
    """
    Only runs the very first time the app is started (when the tables
    are empty). Fills the database with realistic-looking demo data so
    the app doesn't look blank on first launch. After this, every run
    uses whatever real data is actually in the database.
    """
    camera_count = conn.execute("SELECT COUNT(*) FROM cameras").fetchone()[0]
    if camera_count == 0:
        demo_cameras = [
            # ("CAM-01", "Camera 01", "Main Road", "Online", 30, "1920x1080", "2 sec ago", "rtsp://192.168.1.10:554/stream1", "IP Camera"),
            # ("CAM-02", "Camera 02", "Parking Area", "Online", 28, "1920x1080", "1 sec ago", "rtsp://192.168.1.11:554/stream1", "IP Camera"),
            # ("CAM-03", "Camera 03", "College Gate", "Online", 30, "1280x720", "3 sec ago", "rtsp://192.168.1.12:554/stream1", "IP Camera"),
            # ("CAM-04", "Camera 04", "Market Road", "Offline", 0, "Unknown", "42 min ago", "rtsp://192.168.1.13:554/stream1", "IP Camera"),
        ]
        conn.executemany(
            "INSERT INTO cameras (id, name, location, status, fps, resolution, last_activity, source, camera_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            demo_cameras,
        )

    violation_count = conn.execute("SELECT COUNT(*) FROM violations").fetchone()[0]
    if violation_count == 0:
        random.seed(42)  # keeps the demo data the same every fresh install
        violation_types = ["Illegal Parking", "No Parking Zone", "Restricted Zone", "Long Duration Parking"]
        locations = ["Main Road", "Parking Area", "College Gate", "Market Road"]
        camera_names = ["Camera 01", "Camera 02", "Camera 03", "Camera 04"]
        state_codes = ["UP70", "DL8C", "MH12", "UP32", "RJ14", "GJ05"]

        demo_violations = []
        now = datetime.now()
        for i in range(60):
            dt = now - timedelta(hours=random.randint(0, 24 * 10), minutes=random.randint(0, 59))
            letters = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
            plate = f"{random.choice(state_codes)} {letters} {random.randint(1000, 9999)}"
            demo_violations.append(
                (
                    f"VLN-{1000 + i}",
                    plate,
                    random.choice(violation_types),
                    random.choice(locations),
                    random.choice(camera_names),
                    dt.isoformat(timespec="seconds"),
                    round(random.uniform(0.78, 0.99), 2),
                    round(random.uniform(0.70, 0.98), 2),
                    random.choices(["Pending", "Confirmed", "Dismissed"], weights=[0.3, 0.5, 0.2])[0],
                )
            )
        conn.executemany(
            "INSERT INTO violations (id, vehicle_number, violation_type, location, camera, datetime, "
            "confidence, plate_confidence, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            demo_violations,
        )

    conn.commit()


def init_db():
    """Creates the tables (if they don't exist yet) and seeds demo data (if empty)."""
    conn = get_connection()
    try:
        _create_tables(conn)
        _seed_demo_data_if_empty(conn)
    finally:
        conn.close()


# Runs once, automatically, the moment this file is imported anywhere in the app.
init_db()

# 3. READ FUNCTIONS  (same names/shapes the rest of the app already expects)

def get_connection_status():
    """Real health-check: can we actually open the database file?"""
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"connected": True, "engine": f"SQLite ({os.path.basename(DB_PATH)})", "last_sync": "just now"}
    except Exception as e:
        return {"connected": False, "engine": "SQLite", "last_sync": f"error: {e}"}


def get_cameras():
    """Returns list of camera dicts. Real query: SELECT * FROM cameras."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cameras ORDER BY id").fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_violations(n=60):
    """Returns the n most recent violations, newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM violations ORDER BY datetime DESC LIMIT ?", (n,)
    ).fetchall()
    conn.close()

    violations = _rows_to_dicts(rows)
    # The UI code expects a few extra convenience fields derived from `datetime`.
    for v in violations:
        dt = datetime.fromisoformat(v["datetime"])
        v["date"] = dt.strftime("%Y-%m-%d")
        v["time"] = dt.strftime("%H:%M:%S")
        v["datetime"] = dt  # replace the string with a real datetime object
    return violations


def get_dashboard_metrics(violations=None):
    """Aggregates a few headline numbers for the Dashboard page."""
    violations = violations if violations is not None else get_violations()
    today_str = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    total_cameras = conn.execute("SELECT COUNT(*) FROM cameras").fetchone()[0]
    active_cameras = conn.execute("SELECT COUNT(*) FROM cameras WHERE status = 'Online'").fetchone()[0]
    total_violation_rows = conn.execute("SELECT COUNT(*) FROM violations").fetchone()[0]
    conn.close()

    todays_violations = sum(1 for v in violations if v["date"] == today_str)
    pending_reviews = sum(1 for v in violations if v["status"] == "Pending")

    return {
        # Simple placeholder formula until real vehicle-count logging is wired up.
        "total_vehicles_detected": 4820 + total_violation_rows * 3,
        "todays_violations": todays_violations,
        "active_cameras": active_cameras,
        "total_cameras": total_cameras,
        "pending_reviews": pending_reviews,
    }


def get_weekly_violation_trend():
    """Returns violation counts per violation type, per day, for the last 7 days."""
    violation_types = ["Illegal Parking", "No Parking Zone", "Restricted Zone", "Long Duration Parking"]
    days = [(datetime.now() - timedelta(days=i)) for i in range(6, -1, -1)]
    day_labels = [d.strftime("%a %d") for d in days]

    conn = get_connection()
    data = {"day": day_labels}
    for vt in violation_types:
        counts = []
        for d in days:
            day_start = d.strftime("%Y-%m-%d") + "T00:00:00"
            day_end = d.strftime("%Y-%m-%d") + "T23:59:59"
            count = conn.execute(
                "SELECT COUNT(*) FROM violations WHERE violation_type = ? AND datetime BETWEEN ? AND ?",
                (vt, day_start, day_end),
            ).fetchone()[0]
            counts.append(count)
        data[vt] = counts
    conn.close()
    return data

def get_reports_table(days=7):
    """Returns a per-day summary table used in Reports & Analytics."""
    conn = get_connection()
    rows = []
    for i in range(days - 1, -1, -1):
        d = datetime.now() - timedelta(days=i)
        day_str = d.strftime("%Y-%m-%d")
        day_start = day_str + "T00:00:00"
        day_end = day_str + "T23:59:59"

        total_violations = conn.execute(
            "SELECT COUNT(*) FROM violations WHERE datetime BETWEEN ? AND ?", (day_start, day_end)
        ).fetchone()[0]
        confirmed = conn.execute(
            "SELECT COUNT(*) FROM violations WHERE status = 'Confirmed' AND datetime BETWEEN ? AND ?",
            (day_start, day_end),
        ).fetchone()[0]
        dismissed = conn.execute(
            "SELECT COUNT(*) FROM violations WHERE status = 'Dismissed' AND datetime BETWEEN ? AND ?",
            (day_start, day_end),
        ).fetchone()[0]

        rows.append(
            {
                "Date": day_str,
                # Real per-camera vehicle-count logging isn't wired up yet, so this
                # stays estimated until you log every detected vehicle, not just violations.
                "Total Vehicles": 400 + total_violations * 12,
                "Violations": total_violations,
                "Confirmed": confirmed,
                "Dismissed": dismissed,
            }
        )
    conn.close()
    return rows

# 4. WRITE FUNCTIONS  (for the next step: Add Camera form + live violation logging)

def add_camera(name, location, source, resolution="1920x1080", camera_type="IP Camera"):
    """
    Inserts a new camera into the database.
    Call this from modules/cameras.py when the 'Add Camera' form is submitted.
    """
    conn = get_connection()
    next_num = conn.execute("SELECT COUNT(*) FROM cameras").fetchone()[0] + 1
    new_id = f"CAM-{next_num:02d}"
    conn.execute(
        "INSERT INTO cameras (id, name, location, status, fps, resolution, last_activity, source, camera_type) "
        "VALUES (?, ?, ?, 'Online', 0, ?, 'just now', ?, ?)",
        (new_id, name, location, resolution, source, camera_type),
    )
    conn.commit()
    conn.close()
    return new_id


def log_violation(vehicle_number, violation_type, location, camera, confidence=0.0, plate_confidence=0.0, status="Pending"):
    """
    Inserts a new violation record into the database.
    Call this from modules/live_monitoring.py right after a real
    violation + number-plate read happens, instead of just showing
    an on-screen alert.
    """
    conn = get_connection()
    next_num = conn.execute("SELECT COUNT(*) FROM violations").fetchone()[0] + 1001
    new_id = f"VLN-{next_num}"
    conn.execute(
        "INSERT INTO violations (id, vehicle_number, violation_type, location, camera, datetime, "
        "confidence, plate_confidence, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            new_id,
            vehicle_number,
            violation_type,
            location,
            camera,
            datetime.now().isoformat(timespec="seconds"),
            confidence,
            plate_confidence,
            status,
        ),
    )
    conn.commit()
    conn.close()
    return new_id