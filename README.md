# Skill Gap Analyzer for Graduating Students

A Flask + SQLite web app that measures the gap between a graduating student's skills and the skills a target job role demands, for **B.Tech CSE, B.Com and BBA**.

## Run it

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py                  # open http://127.0.0.1:5000
```

Optional:

```bash
python seed_demo.py            # add 36 SYNTHETIC demo students so the comparison charts are not empty
python seed_demo.py --clear    # remove them again
python test_app.py             # run the tests (also usable as your test-case evidence)
```

**Admin login** (created automatically on first run): `admin@skillgap.local` / `admin123`.
Change it before showing anyone else: set `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables before the first run, or delete `skillgap.db` and restart.

## Features

| Feature | Where |
|---|---|
| Signup / login with course selection, hashed passwords, CSRF protection | `/signup`, `/login` |
| Course and target-role selection (5 roles per course) | `/select` |
| Skill self-assessment (0-5) | `/assess` |
| Verification quiz (2 MCQs per skill, 74 questions) | `/quiz` |
| Resume upload (PDF / DOCX / TXT) and score out of 100 with suggestions | `/resume` |
| Gap analysis: radar chart, bar chart, Strong / Moderate / Critical, readiness % | `/gap` |
| What-if simulator ("if I learn SQL, readiness goes to...") | `/gap` |
| Best-fit role suggestions | `/gap` |
| 4 / 8 / 12-week roadmap with study links and progress tracking | `/roadmap` |
| Job-description match | `/jd` |
| Dashboard: readiness ring, trend, KPIs, next-best-action, best-fit roles, achievements | `/dashboard` |
| Profile: edit details, links, password change, profile strength, badges | `/profile` |
| Responsive sidebar layout, light/dark theme toggle | all pages |
| Printable report (Print > Save as PDF) | `/report` |
| Application tracker (kanban), mock interviews (HR + technical), study streak heatmap | `/tracker`, `/interview`, `/dashboard` |
| AI career coach (set `ANTHROPIC_API_KEY`; optional `COACH_MODEL`) | `/coach` |
| Card-style quiz, onboarding stepper, Ctrl+K command palette, toasts, confetti | all pages |
| Cross-course gap comparison (CSE vs B.Com vs BBA) | `/compare` |
| Placement-cell cohort analytics | `/admin` |
| Curriculum vs. industry gap (paste a syllabus) | `/admin/curriculum` |

## The method (explain this to your examiners)

**Skill level** (0-5) for each skill combines three sources:
- self-rating only: used as given
- quiz taken: `level = (self + quiz) / 2`, where `quiz = 1 + 4 x (correct / total)`
- found on the resume: level is at least 2 (it is evidence of use)

**Gap analysis** for a role whose skills have required level `r` and importance weight `w` (1-3):

```
Gap Score = sum( w x max(0, r - level) ) / sum( w x r )
Job Readiness % = 100 x (1 - Gap Score)
```

A skill is Strong (no gap), Moderate (short by less than 2 levels) or Critical (short by 2 or more).

**Resume score (100)**: role-skill match 40, section completeness 25, quantified results 15, action verbs 10, ATS basics (email, phone, length) 10.

**Curriculum gap**: each catalog skill has keywords; a skill counts as covered if any keyword appears in the pasted syllabus. Uncovered skills are ranked by industry demand (total weight across the course's roles).

## Important: what you must improve before submitting

1. **Role requirements are my estimates**, in `data.py`. For a research-quality project, derive them from real data: collect 20-30 job postings per role (Naukri, LinkedIn, Indeed), count how often each skill appears, and set levels and weights from that. Cite this as your methodology.
2. **The demo students are random numbers.** Never present the comparison charts built from them as findings. Collect real responses (a Google Form with the same skill list works) and enter them as users.
3. **Resume parsing is keyword-based**, not ML. It can miss unusual wording and cannot read scanned-image PDFs. State this as a limitation. A natural future-work item is spaCy NER or an LLM for deeper parsing.
4. **The quiz has 2 questions per skill**, enough for a demo but a coarse measure. Add more questions to `quiz_data.py` (the code handles any number).
5. Study links are search links (YouTube, Coursera, NPTEL) so they never go stale.

## Project layout

```
app.py          routes, database, auth
engine.py       resume analysis, gap formula, roadmap, JD match, curriculum gap
data.py         courses, skills, roles, required levels (edit this)
quiz_data.py    MCQ bank (edit this)
seed_demo.py    synthetic demo students
test_app.py     tests
templates/      HTML pages        static/style.css
```

## Ideas to extend

- Google login (Authlib), email verification, password reset by email
- AI career coach chatbot using the Claude API
- Mock interview questions per role
- Badges and streaks
- Admin screens to edit roles, skills and quiz questions in the browser
- Deploy on Render or PythonAnywhere (set `SECRET_KEY`, use gunicorn)
