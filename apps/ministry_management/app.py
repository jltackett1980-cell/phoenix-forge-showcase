#!/usr/bin/env python3
"""
Member Pro - Backend API
Domain: ministry | Entities: Member
Generator: Phoenix Forge v2 (Domain-Agnostic)
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'ministry-secret-v2'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ministry.db')

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
        db.execute('''CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_name TEXT,
            join_date TEXT,
            ministry_role TEXT,
            attendance_rate TEXT,
            tithe_status TEXT,
            small_group TEXT,
            volunteer_hours TEXT,
            prayer_requests TEXT,
            contact_info TEXT,
            baptism_date TEXT,
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
    return jsonify({"app": "Member Pro", "status": "running"})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "app": "Member Pro", "domain": "ministry", "timestamp": datetime.now().isoformat()})

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

# ── MEMBER CRUD ──
@app.route("/api/members", methods=["GET"])
@token_required
def get_members():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute("SELECT * FROM members WHERE name LIKE ? OR status LIKE ? ORDER BY created_at DESC", (f"%{search}%", f"%{search}%")).fetchall()
            else:
                rows = db.execute("SELECT * FROM members ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/members", methods=["POST"])
@token_required
def create_member():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO members (member_name, join_date, ministry_role, attendance_rate, tithe_status, small_group, volunteer_hours, prayer_requests, contact_info, baptism_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [data.get(f, "") for f in ['member_name', 'join_date', 'ministry_role', 'attendance_rate', 'tithe_status', 'small_group', 'volunteer_hours', 'prayer_requests', 'contact_info', 'baptism_date']])
            db.commit()
        log_activity(request.user.get("user"), "create_member")
        return jsonify({"message": "Member created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/members/<int:item_id>", methods=["GET"])
@token_required
def get_member(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM members WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Member not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/members/<int:item_id>", methods=["PUT"])
@token_required
def update_member(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(f"UPDATE members SET member_name=?, join_date=?, ministry_role=?, attendance_rate=?, tithe_status=?, small_group=?, volunteer_hours=?, prayer_requests=?, contact_info=?, baptism_date=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['member_name', 'join_date', 'ministry_role', 'attendance_rate', 'tithe_status', 'small_group', 'volunteer_hours', 'prayer_requests', 'contact_info', 'baptism_date']] + [datetime.now().isoformat(), item_id])
            db.commit()
        log_activity(request.user.get("user"), "update_member", item_id)
        return jsonify({"message": "Member updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/members/<int:item_id>", methods=["DELETE"])
@token_required
def delete_member(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM members WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Member deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/stats", methods=["GET"])
@token_required
def stats():
    try:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM members").fetchone()["count"]
        return jsonify({"total": total, "domain": "ministry"})
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
