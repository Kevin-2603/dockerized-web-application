
import os
import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "dockerapp"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"),
        cursor_factory=RealDictCursor
    )

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "application": "Dockerized Web Application",
        "status": "running",
        "message": "Flask API is running successfully"
    })

@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            "application": "healthy",
            "database": "connected"
        }), 200
    except Exception:
        return jsonify({
            "application": "healthy",
            "database": "disconnected"
        }), 503

@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users ORDER BY id")
        users = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(users), 200
    except Exception:
        return jsonify({"error": "Unable to retrieve users"}), 500

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({
            "error": "Name and email are required"
        }), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) "
            "RETURNING id, name, email",
            (name, email)
        )

        user = cur.fetchone()
        conn.commit()

        cur.close()
        conn.close()

        return jsonify(user), 201

    except psycopg2.IntegrityError:
        conn.rollback()
        conn.close()
        return jsonify({"error": "Email already exists"}), 409

    except Exception:
        return jsonify({"error": "Unable to create user"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
