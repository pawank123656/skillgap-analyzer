"""Mock-interview question generator (HR bank + technical prompts built from the role's top skills)."""
HR = [
    ("Tell me about yourself.", "Present, past, future: what you study now, one strength or project, why this role."),
    ("Why do you want this role?", "Link a real interest or project to what the role does day to day."),
    ("Describe a time you worked in a team and faced a conflict.", "Use STAR: Situation, Task, Action, Result. End with what you learned."),
    ("What is your biggest weakness?", "Name a real one, then show the concrete steps you are taking to improve it."),
    ("Tell me about a time you failed.", "Own it, explain what changed afterwards. Avoid blaming others."),
    ("Where do you see yourself in 3 years?", "Show learning and growth tied to the role, not just a job title."),
]
TECH = [
    "Explain {s} in simple words, as if to a friend outside your field.",
    "Describe a project, assignment or case where you used {s}. What was your role and the result?",
    "What is the most common mistake beginners make in {s}, and how do you avoid it?",
]


def questions(kind, role_reqs):
    if kind == "hr":
        return [{"q": q, "tip": t} for q, t in HR]
    top = sorted(role_reqs, key=lambda s: -role_reqs[s][0] * role_reqs[s][1])[:6]
    return [{"q": TECH[i % len(TECH)].format(s=s), "tip": "Define it, give a concrete example, mention one trade-off or pitfall."}
            for i, s in enumerate(top)]
