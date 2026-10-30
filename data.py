"""Skill catalog and role requirements for the three courses.

ROLES[course][role] = {skill: (required_level 1-5, weight 1-3)}
Replace / extend these numbers with real industry data (job postings, surveys)
to strengthen the research claim of the project.
"""
from urllib.parse import quote_plus

COURSES = {"CSE": "B.Tech CSE", "BCOM": "B.Com", "BBA": "BBA"}


def S(name, cat, *kw):
    return {"name": name, "cat": cat, "kw": list(kw)}


SKILLS = {
    "CSE": [
        S("DSA", "Technical", "data structure", "algorithm", "leetcode", "linked list", "binary tree",
          "dynamic programming", "competitive programming", "codeforces", "hackerrank"),
        S("OOP", "Technical", "object oriented", "object-oriented", "oop", "oops", "java", "c++", "inheritance"),
        S("DBMS & SQL", "Technical", "sql", "mysql", "postgresql", "dbms", "database", "mongodb", "oracle"),
        S("Operating Systems", "Technical", "operating system", "linux", "unix", "process scheduling", "shell script"),
        S("Computer Networks", "Technical", "computer network", "networking", "tcp", "ccna", "routing", "http"),
        S("Web Development", "Technical", "html", "css", "javascript", "react", "node", "nodejs", "django", "flask",
          "angular", "web development", "rest api"),
        S("Python", "Tools", "python", "pandas", "numpy"),
        S("Machine Learning", "Technical", "machine learning", "deep learning", "tensorflow", "pytorch", "scikit",
          "neural network", "nlp", "data science"),
        S("Cloud Computing", "Tools", "aws", "azure", "gcp", "google cloud", "cloud computing", "lambda", "ec2"),
        S("Git & Version Control", "Tools", "git", "github", "gitlab", "version control"),
        S("Docker & DevOps", "Tools", "docker", "kubernetes", "jenkins", "ci/cd", "devops", "terraform"),
        S("Cybersecurity", "Domain", "cyber security", "cybersecurity", "penetration testing", "ethical hacking",
          "encryption", "owasp", "network security", "kali"),
        S("Communication", "Soft Skills", "communication", "presentation", "public speaking", "team lead",
          "teamwork", "collaborat"),
    ],
    "BCOM": [
        S("Financial Accounting", "Domain", "financial accounting", "bookkeeping", "book keeping", "journal entries",
          "ledger", "trial balance", "accounting"),
        S("Taxation (GST & IT)", "Domain", "gst", "income tax", "taxation", "tds", "itr", "tax filing", "tax return"),
        S("Auditing", "Domain", "audit", "auditing", "internal audit", "statutory audit", "vouching"),
        S("Financial Reporting", "Domain", "financial reporting", "financial statement", "balance sheet", "ifrs",
          "ind as", "p&l", "profit and loss", "cash flow"),
        S("Banking & Finance", "Domain", "banking", "loan", "credit", "kyc", "treasury", "mutual fund", "insurance"),
        S("Tally", "Tools", "tally", "tally prime", "tally erp"),
        S("Advanced Excel", "Tools", "excel", "vlookup", "xlookup", "pivot", "macros", "power query"),
        S("SAP / ERP", "Tools", "sap", "erp", "quickbooks", "zoho books", "oracle fusion"),
        S("Business Law", "Domain", "business law", "company law", "companies act", "contract act", "legal compliance"),
        S("Financial Analysis", "Domain", "financial analysis", "ratio analysis", "financial modelling",
          "financial modeling", "valuation", "budgeting", "forecasting"),
        S("Communication", "Soft Skills", "communication", "presentation", "client handling", "teamwork",
          "public speaking"),
        S("Attention to Detail", "Soft Skills", "attention to detail", "accuracy", "reconciliation", "detail oriented",
          "detail-oriented"),
    ],
    "BBA": [
        S("Marketing Management", "Domain", "marketing", "brand management", "market research", "stp", "4ps",
          "campaign"),
        S("Digital Marketing", "Tools", "digital marketing", "seo", "sem", "social media", "google ads",
          "facebook ads", "content marketing", "email marketing"),
        S("HR Management", "Domain", "human resource", "recruitment", "talent acquisition", "payroll", "onboarding",
          "performance appraisal", "hr "),
        S("Operations Management", "Domain", "operations management", "supply chain", "logistics", "inventory",
          "lean", "six sigma", "procurement"),
        S("Business Strategy", "Domain", "business strategy", "swot", "strategic planning", "business plan",
          "porter", "case study", "competitive analysis"),
        S("Financial Management", "Domain", "financial management", "capital budgeting", "working capital",
          "financial planning", "costing", "cost accounting"),
        S("Advanced Excel", "Tools", "excel", "vlookup", "xlookup", "pivot", "macros", "power query"),
        S("Data Analysis & Power BI", "Tools", "power bi", "tableau", "data analysis", "data analytics", "sql",
          "google analytics", "dashboard", "spss"),
        S("CRM Tools", "Tools", "crm", "salesforce", "hubspot", "zoho crm", "lead management"),
        S("Leadership", "Soft Skills", "leadership", "team lead", "led a team", "club president", "event head",
          "captain", "coordinator"),
        S("Negotiation & Sales", "Soft Skills", "negotiation", "sales", "business development", "cold calling",
          "client acquisition"),
        S("Presentation Skills", "Soft Skills", "presentation", "public speaking", "communication", "powerpoint",
          "pitch"),
    ],
}

ROLES = {
    "CSE": {
        "Full Stack Developer": {
            "Web Development": (5, 3), "DSA": (3, 2), "OOP": (4, 2), "DBMS & SQL": (4, 2),
            "Git & Version Control": (4, 2), "Cloud Computing": (2, 1), "Docker & DevOps": (2, 1),
            "Communication": (3, 1)},
        "Data Analyst": {
            "DBMS & SQL": (5, 3), "Python": (4, 3), "Machine Learning": (2, 1), "DSA": (2, 1),
            "Git & Version Control": (2, 1), "Communication": (4, 2)},
        "ML Engineer": {
            "Python": (5, 3), "Machine Learning": (5, 3), "DSA": (4, 2), "DBMS & SQL": (3, 1),
            "Cloud Computing": (3, 1), "Git & Version Control": (3, 1), "Docker & DevOps": (3, 1),
            "Communication": (3, 1)},
        "DevOps Engineer": {
            "Docker & DevOps": (5, 3), "Cloud Computing": (4, 3), "Operating Systems": (4, 2),
            "Computer Networks": (4, 2), "Git & Version Control": (4, 2), "Python": (3, 1),
            "Cybersecurity": (3, 1)},
        "Cybersecurity Analyst": {
            "Cybersecurity": (5, 3), "Computer Networks": (5, 3), "Operating Systems": (4, 2),
            "Python": (3, 1), "Cloud Computing": (3, 1), "DBMS & SQL": (2, 1), "Communication": (3, 1)},
    },
    "BCOM": {
        "Accountant": {
            "Financial Accounting": (5, 3), "Tally": (5, 3), "Advanced Excel": (4, 2),
            "Taxation (GST & IT)": (4, 2), "Financial Reporting": (3, 2), "Attention to Detail": (4, 1),
            "Communication": (3, 1)},
        "Financial Analyst": {
            "Financial Analysis": (5, 3), "Advanced Excel": (5, 3), "Financial Reporting": (4, 2),
            "Financial Accounting": (4, 2), "Banking & Finance": (3, 1), "SAP / ERP": (2, 1),
            "Communication": (4, 1)},
        "Tax Consultant": {
            "Taxation (GST & IT)": (5, 3), "Financial Accounting": (4, 2), "Business Law": (4, 2),
            "Tally": (3, 1), "Advanced Excel": (3, 1), "Communication": (4, 2), "Attention to Detail": (4, 1)},
        "Auditor": {
            "Auditing": (5, 3), "Financial Reporting": (4, 3), "Financial Accounting": (4, 2),
            "Business Law": (3, 1), "Taxation (GST & IT)": (3, 1), "Advanced Excel": (3, 1),
            "SAP / ERP": (3, 1), "Attention to Detail": (5, 2)},
        "Banking Associate": {
            "Banking & Finance": (5, 3), "Communication": (4, 2), "Financial Accounting": (3, 1),
            "Advanced Excel": (3, 1), "Business Law": (3, 1), "Financial Analysis": (3, 1),
            "Attention to Detail": (4, 1)},
    },
    "BBA": {
        "Marketing Executive": {
            "Marketing Management": (5, 3), "Digital Marketing": (5, 3), "Presentation Skills": (4, 2),
            "Data Analysis & Power BI": (3, 1), "Advanced Excel": (3, 1), "Negotiation & Sales": (3, 1),
            "CRM Tools": (3, 1)},
        "HR Executive": {
            "HR Management": (5, 3), "Leadership": (3, 2), "Presentation Skills": (3, 1),
            "Negotiation & Sales": (3, 1), "Advanced Excel": (3, 1), "Business Strategy": (2, 1)},
        "Business Analyst": {
            "Data Analysis & Power BI": (5, 3), "Advanced Excel": (5, 3), "Business Strategy": (4, 2),
            "Presentation Skills": (4, 2), "Financial Management": (3, 1), "Operations Management": (3, 1)},
        "Operations Manager": {
            "Operations Management": (5, 3), "Leadership": (4, 2), "Advanced Excel": (4, 2),
            "Business Strategy": (3, 1), "Data Analysis & Power BI": (3, 1), "Financial Management": (3, 1)},
        "Sales Manager": {
            "Negotiation & Sales": (5, 3), "CRM Tools": (4, 2), "Leadership": (4, 2),
            "Marketing Management": (4, 2), "Presentation Skills": (4, 1), "Digital Marketing": (3, 1)},
    },
}

# sanity check: every skill used in a role exists in the course catalog
for _c, _roles in ROLES.items():
    _names = {s["name"] for s in SKILLS[_c]}
    for _r, _reqs in _roles.items():
        for _sk in _reqs:
            assert _sk in _names, f"{_c}/{_r}: unknown skill {_sk}"


def resources_for(skill):
    """Search links (never go stale like hard-coded course URLs)."""
    q = quote_plus(skill)
    return [
        ("YouTube tutorials", f"https://www.youtube.com/results?search_query={q}+full+course"),
        ("Coursera courses", f"https://www.coursera.org/search?query={q}"),
        ("NPTEL / SWAYAM (free, Indian universities)", "https://nptel.ac.in/courses"),
    ]


# Average self-rating profile used ONLY by seed_demo.py to generate synthetic demo students
DEMO_PROFILE = {
    "CSE": {"DSA": 3.4, "OOP": 3.6, "DBMS & SQL": 3.2, "Operating Systems": 3.0, "Computer Networks": 2.8,
            "Web Development": 3.3, "Python": 3.5, "Machine Learning": 2.3, "Cloud Computing": 1.8,
            "Git & Version Control": 2.9, "Docker & DevOps": 1.6, "Cybersecurity": 1.7, "Communication": 3.0},
    "BCOM": {"Financial Accounting": 4.0, "Taxation (GST & IT)": 3.1, "Auditing": 3.0, "Financial Reporting": 3.2,
             "Banking & Finance": 3.3, "Tally": 3.4, "Advanced Excel": 2.4, "SAP / ERP": 1.5,
             "Business Law": 3.0, "Financial Analysis": 2.5, "Communication": 3.0, "Attention to Detail": 3.5},
    "BBA": {"Marketing Management": 3.8, "Digital Marketing": 2.8, "HR Management": 3.5, "Operations Management": 3.0,
            "Business Strategy": 3.1, "Financial Management": 2.9, "Advanced Excel": 2.3,
            "Data Analysis & Power BI": 1.6, "CRM Tools": 1.7, "Leadership": 3.3, "Negotiation & Sales": 3.0,
            "Presentation Skills": 3.4},
}
