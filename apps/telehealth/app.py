#!/usr/bin/env python3
"""
TeleHealth - Backend API
Domain: telehealth | Entities: Consultation, Patient, Insurance
Generator: Phoenix Forge v2 (Domain-Agnostic)
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'telehealth-secret-v2'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telehealth.db')

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
        db.execute('''CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            provider TEXT,
            session_date TEXT,
            session_type TEXT,
            chief_complaint TEXT,
            diagnosis TEXT,
            prescription_issued TEXT,
            follow_up_date TEXT,
            insurance_id INTEGER,
            recording_consent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultation_id INTEGER,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS insurances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultation_id INTEGER,
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
    return jsonify({"app": "TeleHealth", "status": "running"})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "app": "TeleHealth", "domain": "telehealth", "timestamp": datetime.now().isoformat()})

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

# ── CONSULTATION CRUD ──
@app.route("/api/consultations", methods=["GET"])
@token_required
def get_consultations():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute("SELECT * FROM consultations WHERE name LIKE ? OR status LIKE ? ORDER BY created_at DESC", (f"%{search}%", f"%{search}%")).fetchall()
            else:
                rows = db.execute("SELECT * FROM consultations ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/consultations", methods=["POST"])
@token_required
def create_consultation():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO consultations (patient_name, provider, session_date, session_type, chief_complaint, diagnosis, prescription_issued, follow_up_date, insurance_id, recording_consent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [data.get(f, "") for f in ['patient_name', 'provider', 'session_date', 'session_type', 'chief_complaint', 'diagnosis', 'prescription_issued', 'follow_up_date', 'insurance_id', 'recording_consent']])
            db.commit()
        log_activity(request.user.get("user"), "create_consultation")
        return jsonify({"message": "Consultation created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/consultations/<int:item_id>", methods=["GET"])
@token_required
def get_consultation(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM consultations WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Consultation not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/consultations/<int:item_id>", methods=["PUT"])
@token_required
def update_consultation(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(f"UPDATE consultations SET patient_name=?, provider=?, session_date=?, session_type=?, chief_complaint=?, diagnosis=?, prescription_issued=?, follow_up_date=?, insurance_id=?, recording_consent=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['patient_name', 'provider', 'session_date', 'session_type', 'chief_complaint', 'diagnosis', 'prescription_issued', 'follow_up_date', 'insurance_id', 'recording_consent']] + [datetime.now().isoformat(), item_id])
            db.commit()
        log_activity(request.user.get("user"), "update_consultation", item_id)
        return jsonify({"message": "Consultation updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/consultations/<int:item_id>", methods=["DELETE"])
@token_required
def delete_consultation(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM consultations WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Consultation deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ── PATIENT CRUD ──
@app.route("/api/patients", methods=["GET"])
@token_required
def get_patients():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute("SELECT * FROM patients WHERE name LIKE ? OR status LIKE ? ORDER BY created_at DESC", (f"%{search}%", f"%{search}%")).fetchall()
            else:
                rows = db.execute("SELECT * FROM patients ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/patients", methods=["POST"])
@token_required
def create_patient():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO patients (consultation_id, name) VALUES (?, ?)", [data.get(f, "") for f in ['consultation_id', 'name']])
            db.commit()
        log_activity(request.user.get("user"), "create_patient")
        return jsonify({"message": "Patient created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/patients/<int:item_id>", methods=["GET"])
@token_required
def get_patient(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM patients WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Patient not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/patients/<int:item_id>", methods=["PUT"])
@token_required
def update_patient(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(f"UPDATE patients SET consultation_id=?, name=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['consultation_id', 'name']] + [datetime.now().isoformat(), item_id])
            db.commit()
        log_activity(request.user.get("user"), "update_patient", item_id)
        return jsonify({"message": "Patient updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/patients/<int:item_id>", methods=["DELETE"])
@token_required
def delete_patient(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM patients WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Patient deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ── INSURANCE CRUD ──
@app.route("/api/insurances", methods=["GET"])
@token_required
def get_insurances():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute("SELECT * FROM insurances WHERE name LIKE ? OR status LIKE ? ORDER BY created_at DESC", (f"%{search}%", f"%{search}%")).fetchall()
            else:
                rows = db.execute("SELECT * FROM insurances ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/insurances", methods=["POST"])
@token_required
def create_insurance():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO insurances (consultation_id, name) VALUES (?, ?)", [data.get(f, "") for f in ['consultation_id', 'name']])
            db.commit()
        log_activity(request.user.get("user"), "create_insurance")
        return jsonify({"message": "Insurance created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/insurances/<int:item_id>", methods=["GET"])
@token_required
def get_insurance(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM insurances WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Insurance not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/insurances/<int:item_id>", methods=["PUT"])
@token_required
def update_insurance(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(f"UPDATE insurances SET consultation_id=?, name=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['consultation_id', 'name']] + [datetime.now().isoformat(), item_id])
            db.commit()
        log_activity(request.user.get("user"), "update_insurance", item_id)
        return jsonify({"message": "Insurance updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/insurances/<int:item_id>", methods=["DELETE"])
@token_required
def delete_insurance(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM insurances WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Insurance deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/consultations/<int:parent_id>/patients", methods=["GET"])
@token_required
def get_consultation_patients(parent_id):
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM patients WHERE consultation_id=? ORDER BY created_at DESC", (parent_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/consultations/<int:parent_id>/patients", methods=["POST"])
@token_required
def create_consultation_patient(parent_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO patients (consultation_id, name) VALUES (?, ?)", [parent_id] + [data.get(f, "") for f in ['consultation_id', 'name'][1:]])
            db.commit()
        return jsonify({"message": "patient created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/consultations/<int:parent_id>/insurances", methods=["GET"])
@token_required
def get_consultation_insurances(parent_id):
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM insurances WHERE consultation_id=? ORDER BY created_at DESC", (parent_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/consultations/<int:parent_id>/insurances", methods=["POST"])
@token_required
def create_consultation_insurance(parent_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO insurances (consultation_id, name) VALUES (?, ?)", [parent_id] + [data.get(f, "") for f in ['consultation_id', 'name'][1:]])
            db.commit()
        return jsonify({"message": "insurance created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/stats", methods=["GET"])
@token_required
def stats():
    try:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM consultations").fetchone()["count"]
        return jsonify({"total": total, "domain": "telehealth"})
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
