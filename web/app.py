import hashlib
import os
import time
from functools import wraps

import pymysql
import requests
from flask import Flask, make_response, redirect, render_template, request, send_from_directory, url_for

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


def db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "myedu"),
        password=os.getenv("DB_PASSWORD", "myedu123"),
        database=os.getenv("DB_NAME", "myeduconnect"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        local_infile=True,
    )


def query(sql):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql, args=None):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.lastrowid
    finally:
        conn.close()


def password_hash(password):
    return hashlib.md5(password.encode()).hexdigest()


def make_session(user_id):
    # Deliberately predictable: useful for the cryptography/session weakness requirement.
    return f"{user_id}-{int(time.time() // 60)}"


def current_user():
    token = request.cookies.get("session_id")
    if not token or "-" not in token:
        return None
    user_id = token.split("-", 1)[0]
    users = query(f"SELECT * FROM users WHERE id = {user_id}")
    return users[0] if users else None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or user["role"] != "admin":
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


def init_db():
    execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120),
            email VARCHAR(160) UNIQUE,
            password_hash VARCHAR(64),
            role VARCHAR(20) DEFAULT 'student',
            bio TEXT,
            guardian_phone VARCHAR(40)
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20),
            title VARCHAR(160),
            description TEXT,
            fee DECIMAL(10,2)
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS enrolments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            course_id INT,
            status VARCHAR(30),
            UNIQUE KEY unique_user_course (user_id, course_id)
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            course_id INT,
            amount DECIMAL(10,2),
            card_last4 VARCHAR(4),
            status VARCHAR(30)
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS announcements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            author_id INT,
            title VARCHAR(160),
            body TEXT
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS support_files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            filename VARCHAR(255),
            original_name VARCHAR(255)
        )
        """
    )
    if not query("SELECT id FROM users LIMIT 1"):
        execute(
            "INSERT INTO users (name,email,password_hash,role,bio,guardian_phone) VALUES (%s,%s,%s,%s,%s,%s)",
            ("Admin User", "admin@myeduconnect.local", password_hash("admin123"), "admin", "System administrator", "60123456789"),
        )
        execute(
            "INSERT INTO users (name,email,password_hash,role,bio,guardian_phone) VALUES (%s,%s,%s,%s,%s,%s)",
            ("Aina Rahman", "aina@student.local", password_hash("student123"), "student", "SPM student interested in STEM.", "60112223333"),
        )
        execute(
            "INSERT INTO users (name,email,password_hash,role,bio,guardian_phone) VALUES (%s,%s,%s,%s,%s,%s)",
            ("Teacher Lee", "teacher@school.local", password_hash("teacher123"), "teacher", "Mathematics teacher.", "60198887777"),
        )
        courses = [
            ("MATH101", "Modern Mathematics Booster", "Exam-focused modules, quizzes, and teacher feedback.", 49.90),
            ("SCI220", "Interactive Science Lab", "Simulated experiments and assessment packs.", 59.90),
            ("ENG130", "Academic English Writing", "Guided writing practice and rubric-based marking.", 39.90),
            ("CS150", "Introductory Python", "Beginner-friendly coding lessons for school learners.", 69.90),
            ("BM110", "Bahasa Melayu Karangan Mastery", "Step-by-step essay planning, grammar drills, and guided model answers.", 34.90),
            ("SEJ125", "Sejarah SPM Intensive", "Timeline-based revision, KBAT practice, and topic-by-topic exam notes.", 44.90),
            ("PHY210", "Physics Problem Solving", "Forces, waves, electricity, and exam-style calculation walkthroughs.", 64.90),
            ("CHEM215", "Chemistry Formula Clinic", "Structured lessons for mole concepts, salts, acids, and organic chemistry.", 64.90),
            ("BIO205", "Biology Visual Revision", "Diagram-led learning for cells, genetics, ecosystems, and human systems.", 54.90),
            ("ADD201", "Additional Mathematics Sprint", "Focused practice for functions, calculus, trigonometry, and probability.", 74.90),
            ("ACC180", "Principles of Accounting", "Journal entries, ledgers, trial balance, and financial statement preparation.", 49.90),
            ("ECO170", "Economics Fundamentals", "Micro and macro concepts explained with Malaysian market examples.", 39.90),
            ("GEO140", "Geography Fieldwork Prep", "Map skills, physical geography, human geography, and fieldwork reporting.", 34.90),
            ("ICT160", "Digital Literacy and Productivity", "Safe computing, office productivity, collaboration tools, and digital citizenship.", 29.90),
            ("CS220", "Web Development Basics", "HTML, CSS, JavaScript, and simple project-based website building.", 79.90),
            ("CS260", "Cybersecurity Awareness", "Password safety, phishing recognition, privacy, and secure online habits.", 59.90),
            ("DATA210", "Data Skills with Spreadsheets", "Data cleaning, formulas, charts, pivot tables, and simple dashboards.", 49.90),
            ("ART115", "Creative Design Foundations", "Color, layout, typography, and portfolio exercises for young designers.", 39.90),
            ("BUS190", "Young Entrepreneur Toolkit", "Business model basics, budgeting, marketing, and pitch preparation.", 54.90),
            ("LAW100", "Digital Rights and PDPA Basics", "Introductory privacy, consent, data protection, and responsible platform use.", 44.90),
            ("STUDY90", "Study Skills and Exam Strategy", "Time management, active recall, note-taking, and stress-aware revision planning.", 24.90),
            ("CAREER80", "University and Career Readiness", "Pathway planning, personal statements, interview practice, and scholarship prep.", 29.90),
        ]
        for course in courses:
            execute("INSERT INTO courses (code,title,description,fee) VALUES (%s,%s,%s,%s)", course)
        execute(
            "INSERT INTO announcements (author_id,title,body) VALUES (1,%s,%s)",
            ("Welcome to MyEduConnect", "Trial learning portal for the CCS6324 final assignment."),
        )


@app.route("/")
def index():
    user = current_user()
    courses = query("SELECT * FROM courses ORDER BY id LIMIT 3")
    return render_template("index.html", user=user, courses=courses)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        execute(
            "INSERT INTO users (name,email,password_hash,bio,guardian_phone) VALUES (%s,%s,%s,%s,%s)",
            (
                request.form["name"],
                request.form["email"],
                password_hash(request.form["password"]),
                request.form.get("bio", ""),
                request.form.get("guardian_phone", ""),
            ),
        )
        return redirect(url_for("login"))
    return render_template("register.html", user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        pwd = password_hash(request.form["password"])
        # Deliberately vulnerable SQL concatenation for SQL injection exercises.
        users = query(f"SELECT * FROM users WHERE email = '{email}' AND password_hash = '{pwd}'")
        if users:
            resp = make_response(redirect(url_for("dashboard")))
            resp.set_cookie("session_id", make_session(users[0]["id"]), httponly=False, secure=False, samesite=None)
            return resp
        error = "Invalid login"
    return render_template("login.html", user=current_user(), error=error)


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("session_id")
    return resp


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    enrolments = query(
        f"""
        SELECT e.id, e.course_id, e.status, c.code, c.title
        FROM enrolments e JOIN courses c ON c.id = e.course_id
        WHERE e.user_id = {user['id']}
        ORDER BY e.id DESC
        """
    )
    announcements = query("SELECT a.*, u.name AS author FROM announcements a JOIN users u ON u.id = a.author_id ORDER BY a.id DESC")
    return render_template("dashboard.html", user=user, enrolments=enrolments, announcements=announcements)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if request.method == "POST":
        execute(
            "UPDATE users SET name=%s, bio=%s, guardian_phone=%s WHERE id=%s",
            (request.form["name"], request.form.get("bio", ""), request.form.get("guardian_phone", ""), user["id"]),
        )
        return redirect(url_for("profile"))
    return render_template("profile.html", user=current_user())


@app.route("/courses")
def courses():
    term = request.args.get("q", "")
    if term:
        # Deliberately vulnerable SQL concatenation for SQL injection exercises.
        rows = query(f"SELECT * FROM courses WHERE title LIKE '%{term}%' OR code LIKE '%{term}%'")
    else:
        rows = query("SELECT * FROM courses ORDER BY code")
    return render_template("courses.html", user=current_user(), courses=rows, term=term)


@app.route("/enrol/<int:course_id>", methods=["POST"])
@login_required
def enrol(course_id):
    user = current_user()
    existing = query(f"SELECT id, status FROM enrolments WHERE user_id = {user['id']} AND course_id = {course_id} LIMIT 1")
    if existing:
        if existing[0]["status"] == "pending_payment":
            return redirect(url_for("payment", course_id=course_id))
        if existing[0]["status"] == "cancelled":
            execute("UPDATE enrolments SET status='pending_payment' WHERE id=%s", (existing[0]["id"],))
            return redirect(url_for("payment", course_id=course_id))
        return redirect(url_for("dashboard"))
    execute("INSERT INTO enrolments (user_id, course_id, status) VALUES (%s,%s,%s)", (user["id"], course_id, "pending_payment"))
    return redirect(url_for("payment", course_id=course_id))


@app.route("/cancel-enrolment/<int:enrolment_id>", methods=["POST"])
@login_required
def cancel_enrolment(enrolment_id):
    user = current_user()
    enrolments = query(f"SELECT * FROM enrolments WHERE id = {enrolment_id} AND user_id = {user['id']} LIMIT 1")
    if not enrolments:
        return redirect(url_for("dashboard"))
    enrolment = enrolments[0]
    execute("UPDATE enrolments SET status='cancelled' WHERE id=%s", (enrolment_id,))
    execute(
        "UPDATE payments SET status='cancelled' WHERE user_id=%s AND course_id=%s",
        (user["id"], enrolment["course_id"]),
    )
    return redirect(url_for("dashboard"))


@app.route("/payment/<int:course_id>", methods=["GET", "POST"])
@login_required
def payment(course_id):
    user = current_user()
    course = query(f"SELECT * FROM courses WHERE id = {course_id}")[0]
    enrolments = query(f"SELECT id, status FROM enrolments WHERE user_id = {user['id']} AND course_id = {course_id} LIMIT 1")
    if not enrolments:
        execute("INSERT INTO enrolments (user_id, course_id, status) VALUES (%s,%s,%s)", (user["id"], course_id, "pending_payment"))
    elif enrolments[0]["status"] == "cancelled":
        execute("UPDATE enrolments SET status='pending_payment' WHERE id=%s", (enrolments[0]["id"],))
    elif enrolments[0]["status"] == "active":
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        card = request.form.get("card_number", "")
        execute(
            "INSERT INTO payments (user_id, course_id, amount, card_last4, status) VALUES (%s,%s,%s,%s,%s)",
            (user["id"], course_id, course["fee"], card[-4:], "approved"),
        )
        execute("UPDATE enrolments SET status='active' WHERE user_id=%s AND course_id=%s", (user["id"], course_id))
        return redirect(url_for("dashboard"))
    return render_template("payment.html", user=user, course=course)


@app.route("/invoice/<int:payment_id>")
@login_required
def invoice(payment_id):
    # Deliberately missing ownership check for IDOR exercises.
    rows = query(
        f"""
        SELECT p.*, u.name, u.email, c.code, c.title
        FROM payments p
        JOIN users u ON u.id = p.user_id
        JOIN courses c ON c.id = p.course_id
        WHERE p.id = {payment_id}
        """
    )
    if not rows:
        return "Invoice not found", 404
    return render_template("invoice.html", user=current_user(), invoice=rows[0])


@app.route("/support", methods=["GET", "POST"])
@login_required
def support():
    user = current_user()
    if request.method == "POST":
        file = request.files.get("attachment")
        if file and file.filename:
            # Deliberately no extension/content validation.
            dest = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(dest)
            execute(
                "INSERT INTO support_files (user_id, filename, original_name) VALUES (%s,%s,%s)",
                (user["id"], file.filename, file.filename),
            )
        return redirect(url_for("support"))
    files = query(f"SELECT * FROM support_files WHERE user_id = {user['id']} ORDER BY id DESC")
    return render_template("support.html", user=user, files=files)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/api-summary")
@login_required
def api_summary():
    api_base = os.getenv("API_BASE", "http://api:5001")
    headers = {"X-API-Key": os.getenv("API_SHARED_KEY", "demo-api-key")}
    response = requests.get(f"{api_base}/internal/stats", headers=headers, timeout=5)
    return render_template("api_summary.html", user=current_user(), stats=response.json(), api_base=api_base)


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    user = current_user()
    if request.method == "POST":
        execute(
            "INSERT INTO announcements (author_id,title,body) VALUES (%s,%s,%s)",
            (user["id"], request.form["title"], request.form["body"]),
        )
        return redirect(url_for("admin"))
    users = query("SELECT id,name,email,role,guardian_phone,bio FROM users ORDER BY id")
    payments = query("SELECT * FROM payments ORDER BY id DESC")
    return render_template("admin.html", user=user, users=users, payments=payments)


@app.after_request
def weak_headers(response):
    response.headers["Server"] = "MyEduConnect-Legacy/1.0"
    response.headers["X-Powered-By"] = "Flask-Debug-Lab"
    return response


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    for _ in range(40):
        try:
            init_db()
            break
        except Exception as exc:
            print(f"Waiting for database: {exc}")
            time.sleep(2)
    app.run(host="0.0.0.0", port=8080, debug=True)
