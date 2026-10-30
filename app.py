import json
import os
import secrets
import sqlite3
import urllib.request
from datetime import date, datetime, timedelta
from functools import wraps

from flask import (Flask, abort, flash, g, redirect, jsonify, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import engine
from data import COURSES, ROLES, SKILLS, resources_for
from interview_data import questions as interview_questions
from quiz_data import QUIZ

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("SKILLGAP_DB", os.path.join(BASE, "skillgap.db"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB resume uploads


def _secret():
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    path = os.path.join(BASE, ".secret_key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    return open(path).read().strip()


app.secret_key = _secret()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
  pw_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'student', course TEXT, college TEXT,
  grad_year INTEGER, cgpa REAL, target_role TEXT, is_demo INTEGER DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS self_ratings(user_id INTEGER, skill TEXT, level INTEGER, PRIMARY KEY(user_id, skill));
CREATE TABLE IF NOT EXISTS quiz_results(user_id INTEGER, skill TEXT, correct INTEGER, total INTEGER, taken_at TEXT,
  PRIMARY KEY(user_id, skill));
CREATE TABLE IF NOT EXISTS resumes(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, filename TEXT, text TEXT,
  score INTEGER, details TEXT, target_role TEXT, uploaded_at TEXT);
CREATE TABLE IF NOT EXISTS snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, target_role TEXT,
  readiness REAL, created_at TEXT);
CREATE TABLE IF NOT EXISTS progress(user_id INTEGER, skill TEXT, done INTEGER DEFAULT 0, PRIMARY KEY(user_id, skill));
CREATE TABLE IF NOT EXISTS curriculum(course TEXT PRIMARY KEY, text TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, company TEXT, title TEXT,
  status TEXT DEFAULT 'Saved', match INTEGER, notes TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS interviews(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, kind TEXT, score REAL, n INTEGER, taken_at TEXT);
CREATE TABLE IF NOT EXISTS activity(user_id INTEGER, day TEXT, n INTEGER DEFAULT 0, PRIMARY KEY(user_id, day));
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    have = {r[1] for r in db.execute("PRAGMA table_info(users)")}
    for col in ("headline", "bio", "phone", "github", "linkedin"):
        if col not in have:
            db.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@skillgap.local")
    admin_pw = os.environ.get("ADMIN_PASSWORD", "admin123")
    if not db.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
        db.execute("INSERT INTO users(name,email,pw_hash,role,created_at) VALUES(?,?,?,?,?)",
                   ("Administrator", admin_email, generate_password_hash(admin_pw), "admin", now()))
    db.commit()
    db.close()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------------------------------------------ auth helpers + CSRF
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token
app.jinja_env.globals["COURSES"] = COURSES


@app.before_request
def check_csrf():
    if request.method == "POST":
        if not secrets.compare_digest(request.form.get("_csrf") or request.headers.get("X-CSRF", ""), session.get("_csrf", "x")):
            abort(400, "Invalid CSRF token")


@app.before_request
def load_user():
    g.user = None
    if session.get("uid"):
        g.user = get_db().execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not g.user:
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapper


def student_required(f):
    @wraps(f)
    @login_required
    def wrapper(*a, **kw):
        if g.user["role"] == "admin":
            return redirect(url_for("admin"))
        return f(*a, **kw)
    return wrapper


def role_required(f):
    """Student must have chosen a target role first."""
    @wraps(f)
    @student_required
    def wrapper(*a, **kw):
        if not g.user["target_role"] or g.user["target_role"] not in ROLES[g.user["course"]]:
            flash("Choose your target role first.", "warn")
            return redirect(url_for("select"))
        return f(*a, **kw)
    return wrapper


def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*a, **kw):
        if g.user["role"] != "admin":
            abort(403)
        return f(*a, **kw)
    return wrapper


# ------------------------------------------------------------------ data helpers
def user_state(db, user):
    """Return (levels, latest_resume_row_or_None, resume_skills) for a user row."""
    uid, course = user["id"], user["course"]
    self_r = {r["skill"]: r["level"] for r in db.execute("SELECT skill,level FROM self_ratings WHERE user_id=?", (uid,))}
    quiz = {r["skill"]: (r["correct"], r["total"]) for r in db.execute(
        "SELECT skill,correct,total FROM quiz_results WHERE user_id=?", (uid,))}
    resume = db.execute("SELECT * FROM resumes WHERE user_id=? ORDER BY id DESC LIMIT 1", (uid,)).fetchone()
    rskills = json.loads(resume["details"])["skills_found"] if resume else {}
    return engine.effective_levels(course, self_r, quiz, rskills), resume, rskills


def save_snapshot(db, user, readiness):
    last = db.execute("SELECT readiness,target_role FROM snapshots WHERE user_id=? ORDER BY id DESC LIMIT 1",
                      (user["id"],)).fetchone()
    if not last or last["readiness"] != readiness or last["target_role"] != user["target_role"]:
        db.execute("INSERT INTO snapshots(user_id,target_role,readiness,created_at) VALUES(?,?,?,?)",
                   (user["id"], user["target_role"], readiness, now()))
        db.commit()


PROFILE_FIELDS = ["name", "headline", "phone", "college", "grad_year", "cgpa", "bio", "github", "linkedin", "target_role"]


def initials(name):
    p = (name or "?").split()
    return (p[0][0] + (p[-1][0] if len(p) > 1 else "")).upper()


app.jinja_env.globals["initials"] = initials


def completion(u):
    return round(100 * sum(1 for k in PROFILE_FIELDS if u[k] not in (None, "")) / len(PROFILE_FIELDS))


def achievements(db, u):
    """Badges computed from the student's existing data (nothing extra is stored)."""
    if u["role"] != "student" or u["course"] not in COURSES:
        return []
    uid, course = u["id"], u["course"]
    levels, resume, _ = user_state(db, u)
    count = lambda t, extra="": db.execute(f"SELECT COUNT(*) FROM {t} WHERE user_id=?{extra}", (uid,)).fetchone()[0]
    rated, quizzed, done = count("self_ratings"), count("quiz_results"), count("progress", " AND done=1")
    has_role = u["target_role"] in ROLES[course]
    readiness = engine.compute_gap(ROLES[course][u["target_role"]], levels)["readiness"] if has_role else 0
    best = db.execute("SELECT MAX(score) FROM interviews WHERE user_id=?", (uid,)).fetchone()[0] or 0
    return [
        {"icon": "🎯", "name": "Goal setter", "desc": "Chose a target role", "got": has_role},
        {"icon": "📝", "name": "Self-aware", "desc": "Rated every skill", "got": rated >= len(SKILLS[course])},
        {"icon": "🧠", "name": "Verified", "desc": "Quizzed 5+ skills", "got": quizzed >= 5},
        {"icon": "📄", "name": "Resume ready", "desc": "Resume score 70+", "got": bool(resume and resume["score"] >= 70)},
        {"icon": "✅", "name": "Finisher", "desc": "Completed 3 roadmap skills", "got": done >= 3},
        {"icon": "🚀", "name": "Job ready", "desc": "Readiness 70%+", "got": readiness >= 70},
        {"icon": "🎤", "name": "Interview ready", "desc": "Mock interview avg 4+", "got": best >= 4},
    ]


# ------------------------------------------------------------------ public pages
@app.route("/")
def index():
    if g.user:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        f = request.form
        name, email, pw = f.get("name", "").strip(), f.get("email", "").strip().lower(), f.get("password", "")
        course = f.get("course")
        err = None
        if not name or not email or "@" not in email:
            err = "Enter your name and a valid email."
        elif len(pw) < 8:
            err = "Password must be at least 8 characters."
        elif pw != f.get("confirm"):
            err = "Passwords do not match."
        elif course not in COURSES:
            err = "Select your course."
        if not err:
            db = get_db()
            try:
                year = int(f.get("grad_year") or 0) or None
                cgpa = float(f.get("cgpa") or 0) or None
            except ValueError:
                year = cgpa = None
            try:
                cur = db.execute(
                    "INSERT INTO users(name,email,pw_hash,course,college,grad_year,cgpa,created_at) VALUES(?,?,?,?,?,?,?,?)",
                    (name, email, generate_password_hash(pw), course, f.get("college", "").strip(), year, cgpa, now()))
                db.commit()
            except sqlite3.IntegrityError:
                err = "That email is already registered."
            else:
                session.clear()
                session["uid"] = cur.lastrowid
                flash("Account created. Now choose your target role.", "ok")
                return redirect(url_for("select"))
        flash(err, "err")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        u = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if u and check_password_hash(u["pw_hash"], request.form.get("password", "")):
            session.clear()
            session["uid"] = u["id"]
            return redirect(url_for("admin" if u["role"] == "admin" else "dashboard"))
        flash("Wrong email or password.", "err")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))


# ------------------------------------------------------------------ student flow
@app.route("/select", methods=["GET", "POST"])
@student_required
def select():
    if request.method == "POST":
        course, role = request.form.get("course"), request.form.get("target_role")
        if course not in COURSES or role not in ROLES[course]:
            flash("Pick a valid course and role.", "err")
        else:
            db = get_db()
            db.execute("UPDATE users SET course=?, target_role=? WHERE id=?", (course, role, g.user["id"]))
            db.commit()
            flash(f"Target role set to {role}.", "ok")
            return redirect(url_for("assess"))
    return render_template("select.html", roles={c: list(r) for c, r in ROLES.items()})


@app.route("/dashboard")
@role_required
def dashboard():
    db, uid, course = get_db(), g.user["id"], g.user["course"]
    levels, resume, _ = user_state(db, g.user)
    gap = engine.compute_gap(ROLES[course][g.user["target_role"]], levels)
    save_snapshot(db, g.user, gap["readiness"])
    snaps = db.execute("SELECT readiness,created_at FROM snapshots WHERE user_id=? AND target_role=? ORDER BY id",
                       (uid, g.user["target_role"])).fetchall()
    rated = db.execute("SELECT COUNT(*) FROM self_ratings WHERE user_id=?", (uid,)).fetchone()[0]
    quizzed = db.execute("SELECT COUNT(*) FROM quiz_results WHERE user_id=?", (uid,)).fetchone()[0]
    critical = sorted([r for r in gap["rows"] if r["status"] == "Critical"], key=lambda r: -r["priority"])
    plan = engine.build_roadmap(gap["rows"], 8)
    done = {r["skill"] for r in db.execute("SELECT skill FROM progress WHERE user_id=? AND done=1", (uid,))}
    total = len(SKILLS[course])
    if rated < total:
        nxt = ("Complete your self-assessment", url_for("assess"), f"{rated} of {total} skills rated")
    elif not quizzed:
        nxt = ("Verify your skills with the quiz", url_for("quiz"), "Quiz results make your score credible")
    elif not resume:
        nxt = ("Upload your resume", url_for("resume"), "Get a score out of 100 with specific fixes")
    elif critical:
        nxt = (f"Work on {critical[0]['skill']}", url_for("roadmap"), "Your biggest gap right now")
    else:
        nxt = ("Check a real job posting", url_for("jd"), "See how well you match")
    streak, cells = streak_info(db, uid)
    delta = round(snaps[-1]["readiness"] - snaps[0]["readiness"], 1) if len(snaps) > 1 else None
    return render_template("dashboard.html", gap=gap, resume=resume, rated=rated, quizzed=quizzed, total_skills=total,
                           snaps=snaps, critical=critical, nxt=nxt, delta=delta,
                           plan_done=sum(p["skill"] in done for p in plan), plan_total=len(plan),
                           alt=engine.readiness_for_all_roles(course, levels)[:3],
                           badges=achievements(db, g.user), completion=completion(g.user), streak=streak, cells=cells,
                           history=json.dumps([{"t": s["created_at"][5:16], "v": s["readiness"]} for s in snaps]))


@app.route("/assess", methods=["GET", "POST"])
@role_required
def assess():
    db, course = get_db(), g.user["course"]
    reqs = ROLES[course][g.user["target_role"]]
    if request.method == "POST":
        for s in SKILLS[course]:
            try:
                v = int(request.form.get(f"s_{s['name']}", 0))
            except ValueError:
                v = 0
            v = max(0, min(5, v))
            db.execute("INSERT INTO self_ratings(user_id,skill,level) VALUES(?,?,?) "
                       "ON CONFLICT(user_id,skill) DO UPDATE SET level=excluded.level", (g.user["id"], s["name"], v))
        db.commit()
        flash("Self-assessment saved. Take the quiz to verify your ratings.", "ok")
        return redirect(url_for("quiz"))
    current = {r["skill"]: r["level"] for r in db.execute("SELECT skill,level FROM self_ratings WHERE user_id=?",
                                                          (g.user["id"],))}
    groups = {}
    for s in SKILLS[course]:
        groups.setdefault(s["cat"], []).append(s["name"])
    return render_template("assess.html", groups=groups, current=current, reqs=reqs)


@app.route("/quiz", methods=["GET", "POST"])
@role_required
def quiz():
    db, course = get_db(), g.user["course"]
    reqs = ROLES[course][g.user["target_role"]]
    skills = sorted(reqs, key=lambda s: -reqs[s][1])
    if request.method == "POST":
        for sk in skills:
            qs = QUIZ[course][sk]
            correct, answered = 0, 0
            for i, (_, _, ans) in enumerate(qs):
                val = request.form.get(f"q_{sk}_{i}")
                if val is not None and val != "":
                    answered += 1
                    correct += int(val == str(ans))
            if answered:
                db.execute("INSERT INTO quiz_results(user_id,skill,correct,total,taken_at) VALUES(?,?,?,?,?) "
                           "ON CONFLICT(user_id,skill) DO UPDATE SET correct=excluded.correct,total=excluded.total,"
                           "taken_at=excluded.taken_at", (g.user["id"], sk, correct, len(qs), now()))
        db.commit()
        flash("Quiz graded. Your verified skill levels are updated.", "ok")
        return redirect(url_for("gap"))
    return render_template("quiz.html", skills=skills, bank=QUIZ[course])


@app.route("/resume", methods=["GET", "POST"])
@role_required
def resume():
    db, course, role = get_db(), g.user["course"], g.user["target_role"]
    if request.method == "POST":
        f = request.files.get("resume")
        if not f or not f.filename:
            flash("Choose a file first.", "err")
        else:
            try:
                text = engine.extract_text(f.filename, f.read())
            except ValueError as e:
                flash(str(e), "err")
            except Exception:
                flash("Could not read that file. Try exporting it again as PDF or DOCX.", "err")
            else:
                if len(text.split()) < 30:
                    flash("Almost no text found. If your resume is a scanned image, use a text-based PDF or DOCX.", "err")
                else:
                    res = engine.analyze_resume(text, course, role)
                    db.execute("INSERT INTO resumes(user_id,filename,text,score,details,target_role,uploaded_at) "
                               "VALUES(?,?,?,?,?,?,?)",
                               (g.user["id"], os.path.basename(f.filename), text, res["score"], json.dumps(res), role, now()))
                    db.commit()
                    flash("Resume analysed.", "ok")
                    return redirect(url_for("resume"))
    row = db.execute("SELECT * FROM resumes WHERE user_id=? ORDER BY id DESC LIMIT 1", (g.user["id"],)).fetchone()
    history = db.execute("SELECT filename,score,target_role,uploaded_at FROM resumes WHERE user_id=? ORDER BY id DESC",
                         (g.user["id"],)).fetchall()
    details = json.loads(row["details"]) if row else None
    # re-score against the current role if the role changed since upload
    if row and row["target_role"] != role:
        details = engine.analyze_resume(row["text"], course, role)
    return render_template("resume.html", row=row, d=details, history=history)


@app.route("/gap")
@role_required
def gap():
    db, course, role = get_db(), g.user["course"], g.user["target_role"]
    levels, _, _ = user_state(db, g.user)
    result = engine.compute_gap(ROLES[course][role], levels)
    save_snapshot(db, g.user, result["readiness"])
    alt = engine.readiness_for_all_roles(course, levels)
    sim = [{"skill": r["skill"], "req": r["required"], "w": r["weight"], "lvl": r["level"]} for r in result["rows"]]
    return render_template("gap.html", gp=result, alt=alt, levels=levels, sim=json.dumps(sim),
                           rows=sorted(result["rows"], key=lambda r: -r["priority"]))


@app.route("/roadmap", methods=["GET", "POST"])
@role_required
def roadmap():
    db, course, role = get_db(), g.user["course"], g.user["target_role"]
    if request.method == "POST":
        sk = request.form.get("skill")
        if sk in {s["name"] for s in SKILLS[course]}:
            done = 1 if request.form.get("done") == "1" else 0
            db.execute("INSERT INTO progress(user_id,skill,done) VALUES(?,?,?) "
                       "ON CONFLICT(user_id,skill) DO UPDATE SET done=excluded.done", (g.user["id"], sk, done))
            db.commit()
        return redirect(url_for("roadmap", weeks=request.args.get("weeks", 8)))
    weeks = request.args.get("weeks", "8")
    weeks = int(weeks) if weeks in ("4", "8", "12") else 8
    levels, _, _ = user_state(db, g.user)
    result = engine.compute_gap(ROLES[course][role], levels)
    plan = engine.build_roadmap(result["rows"], weeks)
    done = {r["skill"] for r in db.execute("SELECT skill FROM progress WHERE user_id=? AND done=1", (g.user["id"],))}
    for p in plan:
        p["done"] = p["skill"] in done
        p["links"] = resources_for(p["skill"])
    pct = round(100 * sum(p["done"] for p in plan) / len(plan)) if plan else 100
    return render_template("roadmap.html", plan=plan, weeks=weeks, pct=pct, readiness=result["readiness"])


@app.route("/jd", methods=["GET", "POST"])
@role_required
def jd():
    db, course = get_db(), g.user["course"]
    res = text = None
    if request.method == "POST":
        text = request.form.get("jd", "")
        if len(text.split()) < 15:
            flash("Paste the full job description (at least a few lines).", "err")
        else:
            levels, resume_row, rskills = user_state(db, g.user)
            res = engine.analyze_jd(text, course, levels)
            res["resume_missing"] = [s for s in res["missing"] if s not in rskills] if resume_row else []
            res["has_resume"] = bool(resume_row)
    return render_template("jd.html", res=res, text=text)


@app.route("/report")
@role_required
def report():
    db, course, role = get_db(), g.user["course"], g.user["target_role"]
    levels, resume_row, _ = user_state(db, g.user)
    result = engine.compute_gap(ROLES[course][role], levels)
    plan = engine.build_roadmap(result["rows"], 8)
    details = json.loads(resume_row["details"]) if resume_row else None
    return render_template("report.html", gp=result, plan=plan, d=details, today=now()[:10],
                           rows=sorted(result["rows"], key=lambda r: -r["priority"]),
                           alt=engine.readiness_for_all_roles(course, levels))


def clean_url(v):
    v = (v or "").strip()[:200]
    return v if not v or v.startswith(("http://", "https://")) else "https://" + v


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db, f = get_db(), request.form
    if request.method == "POST":
        if f.get("action") == "password":
            if not check_password_hash(g.user["pw_hash"], f.get("current", "")):
                flash("Current password is wrong.", "err")
            elif len(f.get("new", "")) < 8:
                flash("New password must be at least 8 characters.", "err")
            elif f.get("new") != f.get("confirm"):
                flash("New passwords do not match.", "err")
            else:
                db.execute("UPDATE users SET pw_hash=? WHERE id=?", (generate_password_hash(f["new"]), g.user["id"]))
                db.commit()
                flash("Password updated.", "ok")
        else:
            name = f.get("name", "").strip()[:80]
            try:
                year = int(f.get("grad_year") or 0) or None
                cgpa = float(f.get("cgpa") or 0) or None
            except ValueError:
                year = cgpa = -1
            if not name:
                flash("Name cannot be empty.", "err")
            elif year == -1 or (year and not 2020 <= year <= 2035) or (cgpa and not 0 <= cgpa <= 10):
                flash("Check graduation year (2020-2035) and CGPA (0-10).", "err")
            else:
                db.execute("UPDATE users SET name=?, headline=?, phone=?, college=?, grad_year=?, cgpa=?, bio=?, "
                           "github=?, linkedin=? WHERE id=?",
                           (name, f.get("headline", "").strip()[:80], f.get("phone", "").strip()[:20],
                            f.get("college", "").strip()[:120], year, cgpa, f.get("bio", "").strip()[:400],
                            clean_url(f.get("github")), clean_url(f.get("linkedin")), g.user["id"]))
                db.commit()
                flash("Profile saved.", "ok")
        return redirect(url_for("profile"))
    return render_template("profile.html", badges=achievements(db, g.user), completion=completion(g.user))


# ------------------------------------------------------------------ v2: streaks, tracker, interview, coach
TRACKED = {"assess", "quiz", "resume", "roadmap", "interview", "tracker", "coach_ask"}
STATUSES = ["Saved", "Applied", "Interview", "Offer", "Rejected"]


@app.before_request
def track_activity():
    if request.method == "POST" and session.get("uid") and request.endpoint in TRACKED:
        db = get_db()
        db.execute("INSERT INTO activity(user_id,day,n) VALUES(?,?,1) ON CONFLICT(user_id,day) DO UPDATE SET n=n+1",
                   (session["uid"], date.today().isoformat()))
        db.commit()


def streak_info(db, uid):
    days = {r["day"]: r["n"] for r in db.execute("SELECT day,n FROM activity WHERE user_id=?", (uid,))}
    today = date.today()
    d = today if today.isoformat() in days else today - timedelta(days=1)
    streak = 0
    while d.isoformat() in days:
        streak += 1
        d -= timedelta(days=1)
    cells = []
    for i in range(83, -1, -1):
        k = (today - timedelta(days=i)).isoformat()
        cells.append({"d": k, "n": days.get(k, 0)})
    return streak, cells


@app.route("/tracker", methods=["GET", "POST"])
@role_required
def tracker():
    db, f = get_db(), request.form
    if request.method == "POST":
        act = f.get("action")
        if act == "add":
            title, company = f.get("title", "").strip()[:100], f.get("company", "").strip()[:100]
            if not title or not company:
                flash("Enter a company and a job title.", "err")
            else:
                match, jd_text = None, f.get("jd", "")
                if len(jd_text.split()) >= 15:
                    levels, _, _ = user_state(db, g.user)
                    match = engine.analyze_jd(jd_text, g.user["course"], levels)["match"]
                db.execute("INSERT INTO applications(user_id,company,title,status,match,notes,created_at) VALUES(?,?,?,?,?,?,?)",
                           (g.user["id"], company, title, "Saved", match, f.get("notes", "").strip()[:300], now()))
                db.commit()
                flash("Added to your board.", "ok")
        elif act == "move" and f.get("status") in STATUSES:
            db.execute("UPDATE applications SET status=? WHERE id=? AND user_id=?", (f["status"], f.get("id"), g.user["id"]))
            db.commit()
        elif act == "delete":
            db.execute("DELETE FROM applications WHERE id=? AND user_id=?", (f.get("id"), g.user["id"]))
            db.commit()
        return redirect(url_for("tracker"))
    rows = db.execute("SELECT * FROM applications WHERE user_id=? ORDER BY id DESC", (g.user["id"],)).fetchall()
    return render_template("tracker.html", statuses=STATUSES, cols={s: [r for r in rows if r["status"] == s] for s in STATUSES})


@app.route("/interview", methods=["GET", "POST"])
@role_required
def interview():
    db, course, role = get_db(), g.user["course"], g.user["target_role"]
    if request.method == "POST":
        sc = [int(x) for x in request.form.get("scores", "").split(",") if x.strip().isdigit() and 1 <= int(x) <= 5]
        kind = request.form.get("kind") if request.form.get("kind") in ("hr", "technical") else "hr"
        if sc:
            avg = round(sum(sc) / len(sc), 2)
            db.execute("INSERT INTO interviews(user_id,kind,score,n,taken_at) VALUES(?,?,?,?,?)",
                       (g.user["id"], kind, avg, len(sc), now()))
            db.commit()
            flash(f"Interview complete. You scored yourself {avg}/5.", "ok")
        return redirect(url_for("interview"))
    kind = request.args.get("kind")
    qs = interview_questions(kind, ROLES[course][role]) if kind in ("hr", "technical") else None
    hist = db.execute("SELECT kind,score,n,taken_at FROM interviews WHERE user_id=? ORDER BY id DESC LIMIT 8",
                      (g.user["id"],)).fetchall()
    return render_template("interview.html", kind=kind if qs else None, qs=qs, hist=hist)


@app.route("/coach")
@role_required
def coach():
    return render_template("coach.html", has_key=bool(os.environ.get("ANTHROPIC_API_KEY")),
                           sugg=["What should I learn this week?", "Rewrite my resume summary for my target role",
                                 f"Mock-interview me for {g.user['target_role']}", "Why is my readiness not higher?"])


@app.route("/coach/ask", methods=["POST"])
@role_required
def coach_ask():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return jsonify(reply="The coach is not switched on yet. Set the ANTHROPIC_API_KEY environment variable and restart the app.")
    msgs = [{"role": m["role"], "content": m["content"][:2000]} for m in (request.get_json(silent=True) or {}).get("messages", [])[-12:]
            if isinstance(m, dict) and m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str)]
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    if not msgs:
        return jsonify(reply="Ask me something about your career plan.")
    db, course, role = get_db(), g.user["course"], g.user["target_role"]
    levels, resume, _ = user_state(db, g.user)
    gap = engine.compute_gap(ROLES[course][role], levels)
    gaps = "; ".join(f"{r['skill']} (level {r['level']}, needs {r['required']})"
                     for r in sorted(gap["rows"], key=lambda r: -r["priority"]) if r["gap"] > 0)[:600]
    tips = "; ".join(json.loads(resume["details"])["tips"][:3]) if resume else "no resume uploaded"
    system = (f"You are a concise, honest career coach for graduating students in India. Student: {g.user['name']}, "
              f"{COURSES[course]}, target role {role}. Job readiness {gap['readiness']}%. Biggest gaps: {gaps or 'none'}. "
              f"Resume score: {resume['score'] if resume else 'n/a'}; resume tips: {tips}. "
              "Give concrete, prioritised steps for this week. Keep answers under 180 words. Never invent experience, "
              "projects or credentials when rewriting resume text; ask the student for real facts instead.")
    body = json.dumps({"model": os.environ.get("COACH_MODEL", "claude-sonnet-5-5"), "max_tokens": 700,
                       "system": system, "messages": msgs}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST",
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            text = "".join(b.get("text", "") for b in json.load(r)["content"] if b.get("type") == "text")
    except Exception:
        text = "Sorry, I could not reach the coach. Check your API key and internet connection."
    return jsonify(reply=text or "I have no answer for that. Try rephrasing.")


# ------------------------------------------------------------------ cross-course comparison
def cohort_stats(db):
    """Aggregate readiness + most common critical gaps per course (students with a target role)."""
    out = {}
    for course in COURSES:
        users = db.execute("SELECT * FROM users WHERE role='student' AND course=? AND target_role IS NOT NULL",
                           (course,)).fetchall()
        ready, gaps, demo = [], {}, 0
        for u in users:
            if u["target_role"] not in ROLES[course]:
                continue
            levels, _, _ = user_state(db, u)
            res = engine.compute_gap(ROLES[course][u["target_role"]], levels)
            ready.append(res["readiness"])
            demo += u["is_demo"] or 0
            for r in res["rows"]:
                d = gaps.setdefault(r["skill"], {"critical": 0, "gap_sum": 0.0, "n": 0})
                d["n"] += 1
                d["gap_sum"] += r["gap"]
                d["critical"] += r["status"] == "Critical"
        top = sorted(({"skill": s, "pct": round(100 * d["critical"] / d["n"]), "avg_gap": round(d["gap_sum"] / d["n"], 2)}
                      for s, d in gaps.items()), key=lambda x: (-x["pct"], -x["avg_gap"]))[:6]
        out[course] = {"n": len(ready), "demo": demo, "avg": round(sum(ready) / len(ready), 1) if ready else 0,
                       "top_gaps": top}
    return out


@app.route("/compare")
@login_required
def compare():
    stats = cohort_stats(get_db())
    return render_template("compare.html", stats=stats, labels=json.dumps([COURSES[c] for c in stats]),
                           avgs=json.dumps([stats[c]["avg"] for c in stats]))


# ------------------------------------------------------------------ admin / placement cell
@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    stats = cohort_stats(db)
    students = db.execute(
        "SELECT course, COUNT(*) n FROM users WHERE role='student' GROUP BY course").fetchall()
    return render_template("admin.html", stats=stats, counts={r["course"]: r["n"] for r in students})


@app.route("/admin/curriculum", methods=["GET", "POST"])
@admin_required
def admin_curriculum():
    db = get_db()
    course = request.values.get("course", "CSE")
    if course not in COURSES:
        course = "CSE"
    if request.method == "POST" and request.form.get("syllabus") is not None:
        db.execute("INSERT INTO curriculum(course,text,updated_at) VALUES(?,?,?) "
                   "ON CONFLICT(course) DO UPDATE SET text=excluded.text,updated_at=excluded.updated_at",
                   (course, request.form["syllabus"], now()))
        db.commit()
        flash("Syllabus saved.", "ok")
        return redirect(url_for("admin_curriculum", course=course))
    row = db.execute("SELECT * FROM curriculum WHERE course=?", (course,)).fetchone()
    res = engine.curriculum_gap(course, row["text"]) if row and row["text"].strip() else None
    return render_template("curriculum.html", course=course, row=row, res=res)


@app.cli.command("init-db")
def init_db_cmd():
    init_db()
    print("Database ready:", DB_PATH)


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=int(os.environ.get("PORT", 5000)))
