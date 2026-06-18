import hmac
import os
import time

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

# Mode mirrors the web app (synced via POST /mode). Controls E2-API SQLi and E11 key handling.
STATE = {"secure": os.getenv("SECURE_MODE", "0").lower() in ("1", "true", "yes", "on")}
VULN_KEY = os.getenv("API_SHARED_KEY", "demo-api-key")
SECURE_KEY = os.getenv("API_SECURE_KEY", "s3cure-rotated-key-change-me-1f9b2d")


def db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "myedu"),
        password=os.getenv("DB_PASSWORD", "myedu123"),
        database=os.getenv("DB_NAME", "myeduconnect"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def query(sql, args=None):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args) if args is not None else cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def require_api_key():
    provided = request.headers.get("X-API-Key", "")
    if STATE["secure"]:
        # Secure: strong rotated key, constant-time comparison (fixes E11 replay/guess/timing).
        return hmac.compare_digest(provided, SECURE_KEY)
    # Vulnerable: static guessable key over cleartext HTTP (E11).
    return provided == VULN_KEY


@app.route("/mode", methods=["GET", "POST"])
def mode():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        STATE["secure"] = bool(data.get("secure"))
    return {"secure": STATE["secure"]}


@app.route("/health")
def health():
    return {"status": "ok", "service": "myeduconnect-api"}


@app.route("/internal/stats")
def stats():
    if not require_api_key():
        return {"error": "invalid api key"}, 403
    return jsonify(
        {
            "students": query("SELECT COUNT(*) AS count FROM users WHERE role='student'")[0]["count"],
            "courses": query("SELECT COUNT(*) AS count FROM courses")[0]["count"],
            "payments": query("SELECT COUNT(*) AS count FROM payments")[0]["count"],
            "generated_at": int(time.time()),
        }
    )


@app.route("/internal/student/<student_id>")
def student(student_id):
    if not require_api_key():
        return {"error": "invalid api key"}, 403
    if STATE["secure"]:
        # Secure: parameterized, integer-coerced (fixes E2 API SQLi).
        sid = int(student_id) if str(student_id).isdigit() else 0
        rows = query("SELECT id,name,email,role,bio,guardian_phone FROM users WHERE id = %s", (sid,))
    else:
        # Vulnerable: path value concatenated into SQL (E2).
        rows = query(f"SELECT id,name,email,role,bio,guardian_phone FROM users WHERE id = {student_id}")
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
