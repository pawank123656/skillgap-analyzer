"""End-to-end tests. Run:  python -m pytest -q   (or: python test_app.py)"""
import io
import os
import re
import tempfile

os.environ["SKILLGAP_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

import app as appmod  # noqa: E402
import engine  # noqa: E402
from data import ROLES, SKILLS  # noqa: E402
from quiz_data import QUIZ  # noqa: E402

client = appmod.app.test_client()


def token(html):
    return re.search(r'name="_csrf" value="([^"]+)"', html).group(1)


def post(url, data=None, **kw):
    page = client.get(url if "?" not in url else url.split("?")[0]).get_data(as_text=True)
    d = dict(data or {})
    d["_csrf"] = token(page)
    return client.post(url, data=d, follow_redirects=True, **kw)


# ---------------------------------------------------------------- pure-logic tests
def test_gap_formula():
    reqs = {"A": (4, 2), "B": (2, 1)}
    lv = {"A": {"level": 2.0}, "B": {"level": 3.0}}
    r = engine.compute_gap(reqs, lv)
    # num = 2*(4-2)=4 ; den = 2*4 + 1*2 = 10 ; gap = 0.4 ; readiness = 60
    assert r["gap_score"] == 0.4 and r["readiness"] == 60.0
    assert [x["status"] for x in r["rows"]] == ["Critical", "Strong"]


def test_perfect_and_zero():
    reqs = ROLES["CSE"]["Data Analyst"]
    full = {s: {"level": 5.0} for s in reqs}
    none = {s: {"level": 0.0} for s in reqs}
    assert engine.compute_gap(reqs, full)["readiness"] == 100.0
    assert engine.compute_gap(reqs, none)["readiness"] == 0.0


def test_quiz_and_resume_evidence():
    lv = engine.effective_levels("CSE", {"Python": 5}, {"Python": (0, 2)}, {})
    assert lv["Python"]["level"] == 3.0            # (5 + 1) / 2 : wrong answers pull the rating down
    lv = engine.effective_levels("CSE", {"Python": 0}, {}, {"Python": ["python"]})
    assert lv["Python"]["level"] == 2.0            # resume evidence floor


def test_quiz_bank_complete():
    for course, skills in SKILLS.items():
        for s in skills:
            qs = QUIZ[course][s["name"]]
            assert len(qs) == 2
            for q, opts, ans in qs:
                assert 0 <= ans < len(opts) == 4


def test_roadmap_fits_weeks():
    reqs = ROLES["BBA"]["Business Analyst"]
    res = engine.compute_gap(reqs, {s: {"level": 1.0} for s in reqs})
    for w in (4, 8, 12):
        plan = engine.build_roadmap(res["rows"], w)
        assert sum(p["weeks"] for p in plan) == w
        assert plan[0]["start"] == 1 and plan[-1]["end"] == w


def test_curriculum_gap():
    r = engine.curriculum_gap("CSE", "Data Structures, Java OOP, DBMS with SQL, Operating Systems")
    names = {u["skill"] for u in r["uncovered"]}
    assert "Docker & DevOps" in names and "DSA" not in names


# ---------------------------------------------------------------- full user journey
def test_journey():
    # protected pages redirect to login
    assert client.get("/dashboard").status_code == 302
    # CSRF is enforced
    assert client.post("/login", data={"email": "x", "password": "y"}).status_code == 400

    r = post("/signup", {"name": "Test Student", "email": "t@example.com", "password": "password1",
                         "confirm": "password1", "course": "BCOM", "college": "XYZ", "grad_year": "2027"})
    assert "Choose your target role" in r.get_data(as_text=True) or "Course" in r.get_data(as_text=True)
    # duplicate email rejected
    client.post("/logout", data={"_csrf": token(client.get("/select").get_data(as_text=True))})
    r = post("/signup", {"name": "Dup", "email": "t@example.com", "password": "password1",
                         "confirm": "password1", "course": "BCOM"})
    assert "already registered" in r.get_data(as_text=True)

    r = post("/login", {"email": "t@example.com", "password": "wrong"})
    assert "Wrong email or password" in r.get_data(as_text=True)
    r = post("/login", {"email": "t@example.com", "password": "password1"})
    assert r.status_code == 200

    # pages that need a role redirect to /select first
    assert "Choose your target role" in client.get("/gap", follow_redirects=True).get_data(as_text=True)
    r = post("/select", {"course": "BCOM", "target_role": "Accountant"})
    assert "Self-assessment" in r.get_data(as_text=True)

    ratings = {f"s_{s['name']}": 3 for s in SKILLS["BCOM"]}
    ratings["s_Tally"] = 1
    ratings["s_Advanced Excel"] = 2
    r = post("/assess", ratings)
    assert "Skill quiz" in r.get_data(as_text=True)

    quiz = {}
    for sk in ROLES["BCOM"]["Accountant"]:
        for i, (_, _, ans) in enumerate(QUIZ["BCOM"][sk]):
            quiz[f"q_{sk}_{i}"] = ans
    r = post("/quiz", quiz)
    assert "Gap analysis" in r.get_data(as_text=True)

    # resume (docx)
    import docx
    d = docx.Document()
    for line in ["Test Student  t@example.com  +91 98765 43210", "Summary", "Commerce graduate seeking an accounting role.",
                 "Education", "B.Com, XYZ College, CGPA 8.1", "Skills", "Tally Prime, Excel, GST, financial accounting",
                 "Projects", "Managed 120+ invoices in Tally and reduced month-end closing time by 30%.",
                 "Prepared balance sheet and reconciled bank statements for a local firm. Presented findings to 15 members.",
                 "Certifications", "Tally Prime certification"]:
        d.add_paragraph(line)
    buf = io.BytesIO()
    d.save(buf)
    buf.seek(0)
    page = client.get("/resume").get_data(as_text=True)
    r = client.post("/resume", data={"_csrf": token(page), "resume": (buf, "resume.docx")},
                    content_type="multipart/form-data", follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "Resume score" in html and "Tally" in html
    # bad file type
    r = client.post("/resume", data={"_csrf": token(page), "resume": (io.BytesIO(b"x"), "a.exe")},
                    content_type="multipart/form-data", follow_redirects=True)
    assert "Unsupported file type" in r.get_data(as_text=True)

    html = client.get("/gap").get_data(as_text=True)
    assert "Gap analysis: Accountant" in html and "Job readiness" in html
    for path in ("/dashboard", "/roadmap?weeks=4", "/roadmap?weeks=12", "/report", "/jd", "/compare"):
        assert client.get(path).status_code == 200, path
    r = post("/roadmap?weeks=8", {"skill": "Tally", "done": "1"})
    assert r.status_code == 200
    r = post("/jd", {"jd": "We need an accountant with Tally, GST filing, advanced Excel and strong auditing "
                           "knowledge. Experience with SAP is a plus for this role in our finance team."})
    assert "match with this job" in r.get_data(as_text=True)

    # students cannot open admin pages
    assert client.get("/admin").status_code == 302 or client.get("/admin").status_code == 403
    client.post("/logout", data={"_csrf": token(client.get("/dashboard").get_data(as_text=True))})


def test_admin():
    r = post("/login", {"email": "admin@skillgap.local", "password": "admin123"})
    assert "Placement-cell analytics" in r.get_data(as_text=True)
    r = post("/admin/curriculum", {"course": "BBA", "syllabus": "Marketing management, HR, operations management, SWOT"})
    html = r.get_data(as_text=True)
    assert "Not covered by the syllabus" in html and "Data Analysis" in html
    assert client.get("/compare").status_code == 200


def test_profile():
    c = appmod.app.test_client()

    def tok(url):
        return re.search(r'name="_csrf" value="([^"]+)"', c.get(url).get_data(as_text=True)).group(1)

    c.post("/signup", data={"_csrf": tok("/signup"), "name": "Asha Rao", "email": "asha@example.com", "password": "password123",
                            "confirm": "password123", "course": "CSE"})
    assert c.get("/profile").status_code == 200
    r = c.post("/profile", data={"_csrf": tok("/profile"), "action": "details", "name": "Asha K Rao", "headline": "Backend aspirant",
                                 "college": "XYZ", "grad_year": "2027", "cgpa": "8.4", "github": "github.com/asha",
                                 "bio": "Hello"}, follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "Profile saved" in html and "Asha K Rao" in html and "https://github.com/asha" in html
    r = c.post("/profile", data={"_csrf": tok("/profile"), "action": "details", "name": "Asha", "cgpa": "15"}, follow_redirects=True)
    assert "Check graduation year" in r.get_data(as_text=True)
    r = c.post("/profile", data={"_csrf": tok("/profile"), "action": "password", "current": "wrong", "new": "newpass123",
                                 "confirm": "newpass123"}, follow_redirects=True)
    assert "Current password is wrong" in r.get_data(as_text=True)
    r = c.post("/profile", data={"_csrf": tok("/profile"), "action": "password", "current": "password123", "new": "newpass123",
                                 "confirm": "newpass123"}, follow_redirects=True)
    assert "Password updated" in r.get_data(as_text=True)


def test_v2_features():
    os.environ.pop("ANTHROPIC_API_KEY", None)
    c = appmod.app.test_client()

    def tok(url):
        return re.search(r'name="_csrf" value="([^"]+)"', c.get(url).get_data(as_text=True)).group(1)

    c.post("/signup", data={"_csrf": tok("/signup"), "name": "Ravi K", "email": "ravi@example.com", "password": "password123",
                            "confirm": "password123", "course": "CSE"})
    c.post("/select", data={"_csrf": tok("/select"), "course": "CSE", "target_role": list(ROLES["CSE"])[0]})
    r = c.post("/tracker", data={"_csrf": tok("/tracker"), "action": "add", "company": "Acme", "title": "Dev",
                                 "jd": "We need python sql git docker and html css javascript skills from every candidate here"}, follow_redirects=True)
    assert "Acme" in r.get_data(as_text=True) and "% match" in r.get_data(as_text=True)
    aid = appmod.sqlite3.connect(appmod.DB_PATH).execute("SELECT id FROM applications WHERE company='Acme'").fetchone()[0]
    r = c.post("/tracker", data={"_csrf": tok("/tracker"), "action": "move", "id": aid, "status": "Interview"}, follow_redirects=True)
    assert r.status_code == 200
    assert c.get("/interview?kind=technical").status_code == 200
    r = c.post("/interview", data={"_csrf": tok("/interview"), "kind": "hr", "scores": "4,5,4"}, follow_redirects=True)
    assert "Interview complete" in r.get_data(as_text=True)
    assert "Interview ready" in c.get("/dashboard").get_data(as_text=True) and "Study streak" in c.get("/dashboard").get_data(as_text=True)
    assert c.get("/coach").status_code == 200
    r = c.post("/coach/ask", json={"messages": [{"role": "user", "content": "hi"}]}, headers={"X-CSRF": tok("/coach")})
    assert "not switched on" in r.get_json()["reply"]
    assert c.post("/coach/ask", json={"messages": []}).status_code == 400


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
