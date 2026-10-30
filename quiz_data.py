"""MCQ bank: QUIZ[course][skill] = [(question, [options], correct_index), ...]
Two questions per skill. Extend this to 5+ per skill for a more reliable assessment."""

_EXCEL = [
    ("Which function looks up a value in the first column and returns a value from another column?",
     ["SUMIF", "VLOOKUP", "COUNT", "CONCAT"], 1),
    ("Which feature summarises large data quickly by dragging fields into rows and columns?",
     ["Pivot Table", "Data validation", "Freeze panes", "Spell check"], 0),
]
_COMM_CSE = [
    ("When giving a status update to a non-technical manager you should:",
     ["Use as much jargon as possible", "Explain impact in plain language", "Skip blockers", "Send only code"], 1),
    ("Active listening includes:",
     ["Interrupting to save time", "Paraphrasing to confirm understanding", "Multitasking", "Planning your rebuttal"], 1),
]

QUIZ = {
    "CSE": {
        "DSA": [
            ("Time complexity of binary search on a sorted array?", ["O(n)", "O(log n)", "O(n log n)", "O(1)"], 1),
            ("Which data structure follows LIFO order?", ["Queue", "Stack", "Heap", "Graph"], 1),
        ],
        "OOP": [
            ("Which concept lets a subclass provide its own version of a parent method?",
             ["Encapsulation", "Overriding", "Abstraction", "Compilation"], 1),
            ("Exposing only essential features while hiding internal details is called:",
             ["Inheritance", "Polymorphism", "Abstraction", "Serialization"], 2),
        ],
        "DBMS & SQL": [
            ("Which SQL clause filters groups after GROUP BY?", ["WHERE", "HAVING", "ORDER BY", "LIMIT"], 1),
            ("A column (or set) that uniquely identifies each row is a:",
             ["Foreign key", "Primary key", "Index scan", "View"], 1),
        ],
        "Operating Systems": [
            ("Which scheduling algorithm can starve long processes?",
             ["Round Robin", "FCFS", "Shortest Job First", "None of them"], 2),
            ("Processes waiting on each other forever is called:", ["Deadlock", "Paging", "Spooling", "Booting"], 0),
        ],
        "Computer Networks": [
            ("At which OSI layer does IP operate?", ["Data link", "Network", "Transport", "Session"], 1),
            ("Which protocol translates domain names to IP addresses?", ["DHCP", "DNS", "ARP", "FTP"], 1),
        ],
        "Web Development": [
            ("Which HTTP method is normally used to create a new resource?", ["GET", "POST", "HEAD", "TRACE"], 1),
            ("Which CSS property controls space outside an element's border?",
             ["padding", "margin", "outline", "overflow"], 1),
        ],
        "Python": [
            ("Which of these Python types is immutable?", ["list", "dict", "tuple", "set"], 2),
            ("What does len([1, 2, 3]) return?", ["2", "3", "4", "Error"], 1),
        ],
        "Machine Learning": [
            ("A model that does very well on training data but poorly on new data is:",
             ["Underfitting", "Overfitting", "Well generalised", "Unbiased"], 1),
            ("Which of these is a supervised learning task?",
             ["Clustering", "Classification", "Association mining", "Noise injection"], 1),
        ],
        "Cloud Computing": [
            ("Which service model gives you virtual machines and storage to manage yourself?",
             ["SaaS", "PaaS", "IaaS", "DaaS"], 2),
            ("Auto scaling mainly helps with:",
             ["Matching capacity to demand", "Encrypting data", "Compiling code", "Designing UI"], 0),
        ],
        "Git & Version Control": [
            ("Which command copies a remote repository to your machine?",
             ["git init", "git clone", "git commit", "git merge"], 1),
            ("Which command records staged changes into history?",
             ["git add", "git commit", "git push", "git fetch"], 1),
        ],
        "Docker & DevOps": [
            ("A Docker image is best described as:",
             ["A running container", "A read-only template used to create containers", "A VM disk", "A network driver"], 1),
            ("CI in CI/CD stands for:",
             ["Continuous Integration", "Code Inspection", "Cloud Infrastructure", "Container Isolation"], 0),
        ],
        "Cybersecurity": [
            ("An attack that injects malicious SQL through input fields is:",
             ["XSS", "SQL injection", "CSRF", "DDoS"], 1),
            ("What protects data confidentiality in transit?",
             ["Hashing only", "TLS / HTTPS encryption", "Compression", "Caching"], 1),
        ],
        "Communication": _COMM_CSE,
    },
    "BCOM": {
        "Financial Accounting": [
            ("The accounting equation is:",
             ["Assets = Liabilities + Equity", "Assets = Revenue - Expenses", "Equity = Assets + Liabilities",
              "Liabilities = Assets + Equity"], 0),
            ("Which of these increases with a debit entry?", ["Revenue", "Capital", "Assets", "Liabilities"], 2),
        ],
        "Taxation (GST & IT)": [
            ("GST in India is best described as:",
             ["A direct tax on income", "An indirect tax on supply of goods and services", "A wealth tax",
              "A customs duty"], 1),
            ("Input Tax Credit lets a registered business:",
             ["Claim credit for GST paid on business purchases", "Skip GST filing", "Avoid income tax",
              "Get all taxes refunded"], 0),
        ],
        "Auditing": [
            ("Which audit evidence is generally the most reliable?",
             ["Verbal explanation by management", "Confirmation from an external third party",
              "An unsigned internal note", "Management's estimate"], 1),
            ("The main objective of a statutory audit is to:",
             ["Detect every fraud", "Express an opinion on whether the statements give a true and fair view",
              "Prepare the accounts", "Reduce taxes"], 1),
        ],
        "Financial Reporting": [
            ("Which statement shows financial position at a specific date?",
             ["Income statement", "Balance sheet", "Cash flow statement", "Budget"], 1),
            ("Under accrual accounting, revenue is recorded when:",
             ["Cash is received", "It is earned", "Tax is filed", "The audit ends"], 1),
        ],
        "Banking & Finance": [
            ("India's central bank is:", ["SBI", "RBI", "NABARD", "SEBI"], 1),
            ("The repo rate is the rate at which:",
             ["RBI lends short-term funds to banks", "Banks lend to retail customers", "RBI borrows from the public",
              "Government borrows from banks"], 0),
        ],
        "Tally": [
            ("In Tally, which voucher type records a sale?", ["Payment", "Sales", "Contra", "Journal"], 1),
            ("Cash deposited into a bank account is recorded with a:",
             ["Contra voucher", "Sales voucher", "Purchase voucher", "Memorandum only"], 0),
        ],
        "Advanced Excel": _EXCEL,
        "SAP / ERP": [
            ("ERP stands for:",
             ["Enterprise Resource Planning", "Electronic Record Processing", "External Resource Payment",
              "Enterprise Revenue Planning"], 0),
            ("In SAP, the FI module deals with:",
             ["Financial accounting", "Field inspection", "Fleet information", "Factory inventory"], 0),
        ],
        "Business Law": [
            ("A valid contract requires:",
             ["Offer, acceptance and lawful consideration", "Only a written document", "Government approval always",
              "Two witnesses always"], 0),
            ("The Indian Contract Act was enacted in:", ["1872", "1947", "1956", "2013"], 0),
        ],
        "Financial Analysis": [
            ("Current ratio is:",
             ["Current assets / current liabilities", "Net profit / sales", "Debt / equity", "Sales / assets"], 0),
            ("Which ratio measures profitability on sales?",
             ["Net profit margin", "Quick ratio", "Debt-equity ratio", "Current ratio"], 0),
        ],
        "Communication": [
            ("Best way to present financial results to non-finance managers:",
             ["Dense tables only", "Key insights with simple visuals", "Technical jargon", "Raw ledgers"], 1),
            ("In a formal business email you should:",
             ["Use a clear subject and concise purpose", "Use slang", "Omit the greeting", "Write in capitals"], 0),
        ],
        "Attention to Detail": [
            ("Best way to catch data-entry errors:",
             ["Reconcile and cross-check totals", "Trust the first entry", "Skip review", "Round every number"], 0),
            ("A trial balance does not tally. First step?",
             ["Re-check totals and look for transposed digits", "Delete entries", "Ignore it", "Adjust capital"], 0),
        ],
    },
    "BBA": {
        "Marketing Management": [
            ("The classic 4Ps of marketing are:",
             ["Product, Price, Place, Promotion", "Planning, People, Profit, Policy",
              "Product, Process, Profit, Position", "Price, Packaging, People, Performance"], 0),
            ("STP in marketing stands for:",
             ["Segmentation, Targeting, Positioning", "Selling, Training, Promotion", "Strategy, Tactics, Planning",
              "Sampling, Testing, Pricing"], 0),
        ],
        "Digital Marketing": [
            ("SEO aims to:",
             ["Improve organic search visibility", "Buy ad slots", "Send bulk emails", "Design logos"], 0),
            ("Click-through rate (CTR) is:",
             ["Clicks / impressions", "Cost / revenue", "Conversions / clicks", "Views / followers"], 0),
        ],
        "HR Management": [
            ("Attracting and choosing candidates is called:",
             ["Recruitment and selection", "Appraisal", "Payroll", "Offboarding"], 0),
            ("Which is a performance appraisal method?",
             ["360-degree feedback", "Break-even analysis", "Pareto chart", "Gantt chart"], 0),
        ],
        "Operations Management": [
            ("Economic Order Quantity (EOQ) helps decide:",
             ["Order size that minimises total inventory cost", "Employee quotas", "Exchange rates",
              "Dividend payout"], 0),
            ("Just-in-time (JIT) aims to:",
             ["Minimise inventory by receiving goods when needed", "Maximise stock", "Increase lead time",
              "Avoid suppliers"], 0),
        ],
        "Business Strategy": [
            ("SWOT stands for:",
             ["Strengths, Weaknesses, Opportunities, Threats", "Sales, Work, Orders, Targets",
              "Strategy, Workflow, Output, Tactics", "Scope, Wealth, Operations, Time"], 0),
            ("Porter's Five Forces analyses:",
             ["Industry competitiveness", "Employee morale", "Tax liability", "Stock volatility"], 0),
        ],
        "Financial Management": [
            ("A positive NPV generally means the project:",
             ["Adds value and can be accepted", "Should be rejected", "Only breaks even", "Makes a loss"], 0),
            ("Working capital equals:",
             ["Current assets - current liabilities", "Fixed assets - liabilities", "Equity - debt",
              "Revenue - expenses"], 0),
        ],
        "Advanced Excel": _EXCEL,
        "Data Analysis & Power BI": [
            ("Which language is used to write measures in Power BI?", ["DAX", "CSS", "Bash", "Swift"], 0),
            ("Which chart best shows a trend over time?",
             ["Line chart", "Pie chart", "Donut chart", "Word cloud"], 0),
        ],
        "CRM Tools": [
            ("CRM stands for:",
             ["Customer Relationship Management", "Corporate Revenue Model", "Client Risk Matrix",
              "Customer Retail Margin"], 0),
            ("A sales pipeline in a CRM tracks:",
             ["Leads moving through stages to closing", "Employee leave", "Inventory counts", "Tax filings"], 0),
        ],
        "Leadership": [
            ("A leader who involves the team in decisions uses a ___ style:",
             ["Participative", "Autocratic", "Absent", "Coercive"], 0),
            ("Best first response when two team members clash:",
             ["Listen to both and mediate", "Ignore it", "Take sides", "Replace one of them"], 0),
        ],
        "Negotiation & Sales": [
            ("BATNA stands for:",
             ["Best Alternative To a Negotiated Agreement", "Basic Agreement To Negotiate Actions",
              "Budget And Targets Not Agreed", "Better Arguments Take No Account"], 0),
            ("In consultative selling you first:",
             ["Understand the customer's needs", "Quote the lowest price", "Close immediately",
              "Avoid asking questions"], 0),
        ],
        "Presentation Skills": [
            ("A good slide usually has:",
             ["One main idea with minimal text", "Full paragraphs", "Tiny fonts", "Many unrelated charts"], 0),
            ("If you cannot answer an audience question you should:",
             ["Admit it and promise a follow-up", "Make something up", "Ignore it", "Blame the audience"], 0),
        ],
    },
}

from data import SKILLS  # noqa: E402

for _c in SKILLS:
    for _s in SKILLS[_c]:
        assert _s["name"] in QUIZ[_c], f"missing quiz for {_c}/{_s['name']}"
