"""Create SYNTHETIC demo students so the comparison and admin charts have something to show.

    python seed_demo.py            # add 12 demo students per course
    python seed_demo.py --clear    # remove all demo students

These are random numbers around typical profiles in data.DEMO_PROFILE. They are NOT real survey
data: do not present them as research findings. Replace them with real student responses.
"""
import random
import sqlite3
import sys

from werkzeug.security import generate_password_hash

import app as appmod
from data import COURSES, DEMO_PROFILE, ROLES

N_PER_COURSE = 12


def main():
    db = sqlite3.connect(appmod.DB_PATH)
    ids = [r[0] for r in db.execute("SELECT id FROM users WHERE is_demo=1")]
    for i in ids:
        for t in ("self_ratings", "quiz_results", "resumes", "snapshots", "progress"):
            db.execute(f"DELETE FROM {t} WHERE user_id=?", (i,))
    db.execute("DELETE FROM users WHERE is_demo=1")
    if "--clear" in sys.argv:
        db.commit()
        print(f"Removed {len(ids)} demo students.")
        return
    rng = random.Random(42)
    pw = generate_password_hash("demo-not-for-login")
    for course in COURSES:
        roles = list(ROLES[course])
        for n in range(N_PER_COURSE):
            cur = db.execute(
                "INSERT INTO users(name,email,pw_hash,course,college,grad_year,cgpa,target_role,is_demo,created_at) "
                "VALUES(?,?,?,?,?,?,?,?,1,?)",
                (f"Demo {course} {n + 1}", f"demo.{course.lower()}.{n + 1}@example.invalid", pw, course,
                 "Demo College", 2027, round(rng.uniform(6.0, 9.2), 2), roles[n % len(roles)], appmod.now()))
            uid = cur.lastrowid
            ability = rng.gauss(0, 0.5)          # some students are simply stronger overall
            for skill, mean in DEMO_PROFILE[course].items():
                v = max(0, min(5, round(rng.gauss(mean + ability, 0.8))))
                db.execute("INSERT INTO self_ratings VALUES(?,?,?)", (uid, skill, v))
    db.commit()
    print(f"Added {N_PER_COURSE * len(COURSES)} synthetic demo students. Remove with: python seed_demo.py --clear")


if __name__ == "__main__":
    main()
