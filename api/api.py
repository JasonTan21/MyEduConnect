import os
import time

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)


def db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "myedu"),
        password=os.getenv("DB_PASSWORD", "myedu123"),
        database=os.getenv("DB_NAME", "myeduconnect"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def query(sql):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def require_api_key():
    # Deliberately static shared key transmitted over cleartext HTTP.
    return request.headers.get("X-API-Key") == os.getenv("API_SHARED_KEY", "demo-api-key")


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
    # Deliberately vulnerable SQL concatenation on the separate REST API.
    rows = query(f"SELECT id,name,email,role,bio,guardian_phone FROM users WHERE id = {student_id}")
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
