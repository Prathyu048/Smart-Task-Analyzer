🌟 Smart Task Analyzer

Technical Assessment — Software Development Intern (Singularium Technologies Pvt Ltd)

Smart Task Analyzer is a full-stack mini-application that analyzes tasks and calculates a priority score based on urgency, importance, effort, and task dependencies.
The system provides multiple scoring strategies and a clean UI built with HTML/CSS/JavaScript, served through Django templates.

🚀 Features Implemented
✔ Backend (Django)

POST /api/tasks/analyze/
Returns all tasks sorted by priority with:

Score (0–1)

Priority level (High/Medium/Low)

Explanation

Breakdown (urgency, importance, effort, dependencies)

Circular dependency warnings

GET /api/tasks/suggest/
Returns top 3 recommended tasks with explanations.

✔ Prioritization Strategies
Strategy	Description
Smart Balance	Considers all factors fairly
Fastest Wins	Prioritizes low-effort tasks
High Impact	Focuses on high-importance tasks
Deadline Driven	Urgency-based ranking
✔ Frontend (HTML/CSS/JavaScript)

Add tasks through form

Or paste JSON list

Strategy dropdown

Displays:

Final score

Priority

Complete explanation

Breakdown

Uses fetch API to call Django backend

Clean responsive UI

✔ Additional Backend Features

Circular dependency detection

Validation for missing/bad fields

Normalized scoring for fairness

Safe error responses

✔ Unit Tests (tasks/tests.py)

Urgency calculation

Importance normalization

Effort scoring

Cycle detection

📁 Project Structure (Matches Your Screenshot)
SmartTaskAnalyzer/
│── manage.py
│── db.sqlite3
│── requirements.txt
│── README.md
│── smarttask/
│    ├── settings.py
│    ├── urls.py
│    └── ...
│
└── tasks/
     ├── views.py
     ├── scoring.py
     ├── utils.py
     ├── tests.py
     ├── urls.py
     └── templates/
          └── frontend.html


Note: Frontend lives inside Django templates at tasks/templates/frontend.html.

⚙️ Setup Instructions
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Run migrations
python manage.py migrate

3️⃣ Start Django server
python manage.py runserver

4️⃣ Open frontend

Navigate to:

http://127.0.0.1:8000/


This loads frontend.html.

🧠 Algorithm Explanation

Each task gets a score between 0 and 1, computed using:

score = weighted_sum(urgency, importance, effort, dependency_factor)

➤ Urgency

Due date closer → higher score

Past-due tasks → boosted urgency

➤ Importance (1–10)

Converted to 0–1 scale using normalization.

➤ Effort

Low effort = quick win = higher score.

➤ Dependency Factor

Tasks blocking others get higher priority.

➤ Strategy Weights

Example:

Factor	Smart	Fastest	Impact	Deadline
Urgency	0.35	0.20	0.20	0.70
Importance	0.30	0.10	0.70	0.20
Effort	0.20	0.60	0.05	0.05
Dependency	0.15	0.10	0.05	0.05

These weights change how scoring behaves.

🧪 Running the Tests
python manage.py test tasks

🧩 Design Decisions

Implemented flexible weights to allow expansion

Chose simple normalized formula for clarity

Browser-friendly JSON frontend

Safe error handling on backend

Separate files for logic (scoring.py), utils, tests, views

Single HTML file for simplicity (frontend.html)

🔮 Future Improvements

Dependency graph visualization

Drag-and-drop task UI

Save tasks to database

Personalized scoring using ML

Holiday-aware urgency system

Eisenhower Matrix view
