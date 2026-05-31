#!/usr/bin/env python3
"""
MindSpace - Backend API
Domain: mental_wellness | Entities: Booking, Client
Generator: Phoenix Forge v2 (Domain-Agnostic)
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'mental_wellness-secret-v2'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mental_wellness.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT "user",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            therapist TEXT,
            session_date TEXT,
            session_type TEXT,
            mood_rating TEXT,
            goals_progress TEXT,
            crisis_plan TEXT,
            homework_assigned TEXT,
            next_appointment TEXT,
            insurance TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            entity_id INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "No token"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def log_activity(user_id, action, entity_id=None, details=None):
    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO activity_log (user_id, action, entity_id, details) VALUES (?, ?, ?, ?)",
                (user_id, action, entity_id, details)
            )
            db.commit()
    except:
        pass

@app.route("/", methods=["GET"])
def index():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/index.html")
    if os.path.exists(p):
        return send_file(p)
    return jsonify({"app": "MindSpace", "status": "running"})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "app": "MindSpace", "domain": "mental_wellness", "timestamp": datetime.now().isoformat()})

@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400
        hashed = generate_password_hash(data["password"])
        with get_db() as db:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data["username"], hashed))
            db.commit()
        return jsonify({"message": "User created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (data["username"],)).fetchone()
        if user and check_password_hash(user["password"], data["password"]):
            token = jwt.encode({"user": data["username"], "role": user["role"]}, SECRET_KEY, algorithm="HS256")
            return jsonify({"token": token, "username": data["username"]})
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── BOOKING CRUD ──
@app.route("/api/bookings", methods=["GET"])
@token_required
def get_bookings():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute("SELECT * FROM bookings WHERE name LIKE ? OR status LIKE ? ORDER BY created_at DESC", (f"%{search}%", f"%{search}%")).fetchall()
            else:
                rows = db.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bookings", methods=["POST"])
@token_required
def create_booking():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO bookings (client_name, therapist, session_date, session_type, mood_rating, goals_progress, crisis_plan, homework_assigned, next_appointment, insurance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [data.get(f, "") for f in ['client_name', 'therapist', 'session_date', 'session_type', 'mood_rating', 'goals_progress', 'crisis_plan', 'homework_assigned', 'next_appointment', 'insurance']])
            db.commit()
        log_activity(request.user.get("user"), "create_booking")
        return jsonify({"message": "Booking created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/bookings/<int:item_id>", methods=["GET"])
@token_required
def get_booking(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM bookings WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Booking not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bookings/<int:item_id>", methods=["PUT"])
@token_required
def update_booking(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(f"UPDATE bookings SET client_name=?, therapist=?, session_date=?, session_type=?, mood_rating=?, goals_progress=?, crisis_plan=?, homework_assigned=?, next_appointment=?, insurance=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['client_name', 'therapist', 'session_date', 'session_type', 'mood_rating', 'goals_progress', 'crisis_plan', 'homework_assigned', 'next_appointment', 'insurance']] + [datetime.now().isoformat(), item_id])
            db.commit()
        log_activity(request.user.get("user"), "update_booking", item_id)
        return jsonify({"message": "Booking updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/bookings/<int:item_id>", methods=["DELETE"])
@token_required
def delete_booking(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM bookings WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Booking deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ── CLIENT CRUD ──
@app.route("/api/clients", methods=["GET"])
@token_required
def get_clients():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute("SELECT * FROM clients WHERE name LIKE ? OR status LIKE ? ORDER BY created_at DESC", (f"%{search}%", f"%{search}%")).fetchall()
            else:
                rows = db.execute("SELECT * FROM clients ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clients", methods=["POST"])
@token_required
def create_client():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO clients (booking_id, name) VALUES (?, ?)", [data.get(f, "") for f in ['booking_id', 'name']])
            db.commit()
        log_activity(request.user.get("user"), "create_client")
        return jsonify({"message": "Client created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/clients/<int:item_id>", methods=["GET"])
@token_required
def get_client(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM clients WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Client not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clients/<int:item_id>", methods=["PUT"])
@token_required
def update_client(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(f"UPDATE clients SET booking_id=?, name=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['booking_id', 'name']] + [datetime.now().isoformat(), item_id])
            db.commit()
        log_activity(request.user.get("user"), "update_client", item_id)
        return jsonify({"message": "Client updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/clients/<int:item_id>", methods=["DELETE"])
@token_required
def delete_client(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM clients WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Client deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bookings/<int:parent_id>/clients", methods=["GET"])
@token_required
def get_booking_clients(parent_id):
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM clients WHERE booking_id=? ORDER BY created_at DESC", (parent_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bookings/<int:parent_id>/clients", methods=["POST"])
@token_required
def create_booking_client(parent_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO clients (booking_id, name) VALUES (?, ?)", [parent_id] + [data.get(f, "") for f in ['booking_id', 'name'][1:]])
            db.commit()
        return jsonify({"message": "client created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/stats", methods=["GET"])
@token_required
def stats():
    try:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM bookings").fetchone()["count"]
        return jsonify({"total": total, "domain": "mental_wellness"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "code": 404}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request", "code": 400}), 400

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error", "code": 500}), 500

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
