#!/usr/bin/env python3
"""
Build A Reentry Support - Backend API
Domain: custom_build_a_reentry | Entities: Booking, Customer, Provider
Generator: Phoenix Forge v2 (Domain-Agnostic)
"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, os

app = Flask(__name__)
CORS(app)
SECRET_KEY = 'custom_build_a_reentry-secret-v2'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_build_a_reentry.db')

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
            booking_id INTEGER,
            customer_name TEXT,
            customer_phone TEXT,
            provider_name TEXT,
            service TEXT,
            location TEXT,
            scheduled_date TEXT,
            scheduled_time TEXT,
            duration TEXT,
            rate TEXT,
            total REAL DEFAULT 0,
            status TEXT DEFAULT 'draft',
            rating TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER,
            name TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS providers (
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
    return jsonify({"app": "Build A Reentry Support", "status": "running"})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "app": "Build A Reentry Support", "domain": "custom_build_a_reentry", "timestamp": datetime.now().isoformat()})

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
            db.execute("INSERT INTO bookings (booking_id, customer_name, customer_phone, provider_name, service, location, scheduled_date, scheduled_time, duration, rate, total, status, rating, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [data.get(f, "") for f in ['booking_id', 'customer_name', 'customer_phone', 'provider_name', 'service', 'location', 'scheduled_date', 'scheduled_time', 'duration', 'rate', 'total', 'status', 'rating', 'notes']])
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
            db.execute(f"UPDATE bookings SET booking_id=?, customer_name=?, customer_phone=?, provider_name=?, service=?, location=?, scheduled_date=?, scheduled_time=?, duration=?, rate=?, total=?, status=?, rating=?, notes=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['booking_id', 'customer_name', 'customer_phone', 'provider_name', 'service', 'location', 'scheduled_date', 'scheduled_time', 'duration', 'rate', 'total', 'status', 'rating', 'notes']] + [datetime.now().isoformat(), item_id])
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
# ── CUSTOMER CRUD ──
@app.route("/api/customers", methods=["GET"])
@token_required
def get_customers():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute("SELECT * FROM customers WHERE name LIKE ? OR status LIKE ? ORDER BY created_at DESC", (f"%{search}%", f"%{search}%")).fetchall()
            else:
                rows = db.execute("SELECT * FROM customers ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/customers", methods=["POST"])
@token_required
def create_customer():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO customers (booking_id, name, phone) VALUES (?, ?, ?)", [data.get(f, "") for f in ['booking_id', 'name', 'phone']])
            db.commit()
        log_activity(request.user.get("user"), "create_customer")
        return jsonify({"message": "Customer created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/customers/<int:item_id>", methods=["GET"])
@token_required
def get_customer(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM customers WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/customers/<int:item_id>", methods=["PUT"])
@token_required
def update_customer(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(f"UPDATE customers SET booking_id=?, name=?, phone=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['booking_id', 'name', 'phone']] + [datetime.now().isoformat(), item_id])
            db.commit()
        log_activity(request.user.get("user"), "update_customer", item_id)
        return jsonify({"message": "Customer updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/customers/<int:item_id>", methods=["DELETE"])
@token_required
def delete_customer(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM customers WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Customer deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ── PROVIDER CRUD ──
@app.route("/api/providers", methods=["GET"])
@token_required
def get_providers():
    try:
        search = request.args.get("search", "")
        with get_db() as db:
            if search:
                rows = db.execute("SELECT * FROM providers WHERE name LIKE ? OR status LIKE ? ORDER BY created_at DESC", (f"%{search}%", f"%{search}%")).fetchall()
            else:
                rows = db.execute("SELECT * FROM providers ORDER BY created_at DESC").fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/providers", methods=["POST"])
@token_required
def create_provider():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO providers (booking_id, name) VALUES (?, ?)", [data.get(f, "") for f in ['booking_id', 'name']])
            db.commit()
        log_activity(request.user.get("user"), "create_provider")
        return jsonify({"message": "Provider created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/providers/<int:item_id>", methods=["GET"])
@token_required
def get_provider(item_id):
    try:
        with get_db() as db:
            row = db.execute("SELECT * FROM providers WHERE id=?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Provider not found"}), 404
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/providers/<int:item_id>", methods=["PUT"])
@token_required
def update_provider(item_id):
    try:
        data = request.get_json()
        with get_db() as db:
            db.execute(f"UPDATE providers SET booking_id=?, name=?, updated_at=? WHERE id=?", [data.get(f, "") for f in ['booking_id', 'name']] + [datetime.now().isoformat(), item_id])
            db.commit()
        log_activity(request.user.get("user"), "update_provider", item_id)
        return jsonify({"message": "Provider updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/providers/<int:item_id>", methods=["DELETE"])
@token_required
def delete_provider(item_id):
    try:
        with get_db() as db:
            db.execute("DELETE FROM providers WHERE id=?", (item_id,))
            db.commit()
        return jsonify({"message": "Provider deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bookings/<int:parent_id>/customers", methods=["GET"])
@token_required
def get_booking_customers(parent_id):
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM customers WHERE booking_id=? ORDER BY created_at DESC", (parent_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bookings/<int:parent_id>/customers", methods=["POST"])
@token_required
def create_booking_customer(parent_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO customers (booking_id, name, phone) VALUES (?, ?, ?)", [parent_id] + [data.get(f, "") for f in ['booking_id', 'name', 'phone'][1:]])
            db.commit()
        return jsonify({"message": "customer created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/bookings/<int:parent_id>/providers", methods=["GET"])
@token_required
def get_booking_providers(parent_id):
    try:
        with get_db() as db:
            rows = db.execute("SELECT * FROM providers WHERE booking_id=? ORDER BY created_at DESC", (parent_id,)).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bookings/<int:parent_id>/providers", methods=["POST"])
@token_required
def create_booking_provider(parent_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        with get_db() as db:
            db.execute("INSERT INTO providers (booking_id, name) VALUES (?, ?)", [parent_id] + [data.get(f, "") for f in ['booking_id', 'name'][1:]])
            db.commit()
        return jsonify({"message": "provider created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ── STATUS ──
@app.route("/api/bookings/<int:item_id>/status", methods=["PATCH"])
@token_required
def update_booking_status(item_id):
    try:
        data = request.get_json()
        new_status = data.get("status")
        valid = ["draft", "sent", "partial", "paid", "overdue", "cancelled"]
        if new_status not in valid:
            return jsonify({"error": f"Invalid status. Valid: {valid}"}), 400
        with get_db() as db:
            db.execute("UPDATE bookings SET status=?, updated_at=? WHERE id=?", (new_status, datetime.now().isoformat(), item_id))
            db.commit()
        log_activity(request.user.get("user"), "update_status", item_id, new_status)
        return jsonify({"message": "Status updated", "status": new_status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
@token_required
def stats():
    try:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) as count FROM bookings").fetchone()["count"]
        return jsonify({"total": total, "domain": "custom_build_a_reentry"})
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
