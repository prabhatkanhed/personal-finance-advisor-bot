# Personal Finance Advisor Bot 💰🤖

A full-stack, production-quality financial planning and advisory web application powered by **Flask**, **SQLAlchemy**, **Chart.js**, and **Google Gemini AI**.

The application helps individuals track cash flow, categorize expenditures, establish dynamic category budgets, monitor savings milestones, evaluate deterministic financial health scores, and receive tailored AI-driven recommendations.

---

## 🌟 Key Features

### 1. 🔐 Secure Authentication & Multi-Tenant Data Isolation
- User registration, login, logout, and profile management with password changes.
- Password hashing with salted PBKDF2/SHA-256 via Werkzeug.
- HTTP-only session cookies and CSRF protection on all forms.
- **Strict data isolation**: Users can only read and mutate their own income, expenses, budgets, categories, and savings goals.

### 2. 📊 Interactive Dashboard & Visualizations
- Real-time KPI statistics: Total Income, Total Expenses, Net Liquidity Balance, Total Savings.
- Visual Monthly Budget Utilization bar with real-time overspending alerts.
- **4 Interactive Chart.js Visualizations**:
  1. *Income vs. Expense* comparative bar chart.
  2. *6-Month Cash Flow Trends* line chart.
  3. *Category Expense Breakdown* doughnut chart.
  4. *Savings Goals Progress* horizontal bar milestone chart.
- Month-by-month and year-by-year historical inspection filters.
- Recent transaction logs with quick action links.

### 3. 💵 Financial Tracking (Full CRUD)
- **Income Tracker**: Track salary, freelance payments, dividends, and bonuses with dates and descriptions.
- **Expense Tracker**: Record spending by custom category, date, and vendor with instant validation.
- **Category Manager**: Create custom categories with custom hex accent colors and Bootstrap icons.

### 4. 🎯 Budget Management
- Define overall monthly caps and category-level budgets.
- Automated tracking of spent vs. remaining funds and utilization percentages.
- Visual alerts when categories exceed planned spending limits.
- **One-Click AI Budget Application**: Directly convert AI-generated plans into live database budgets.

### 5. 🐖 Savings Goal Tracking
- Set target goal amounts and target deadlines.
- Real-time progress percentage and remaining amounts needed.
- Quick **"Deposit to Goal"** action to record incremental savings.
- Celebration badge and completion indicators upon reaching targets.

### 6. 🧠 AI Financial Advisor (Google Gemini API)
- Connects to Google Gemini (`gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro`).
- Generates:
  - Spending habit evaluation
  - Overspending and cash leak detection
  - Budget optimization recommendations
  - Savings acceleration tactics
  - Practical cost-cutting opportunities
  - Emergency buffer guidance (3–6 months)
  - Motivating personalized executive summary
- **"Generate My Budget with AI"**: Enter monthly income, fixed costs, variable spending, and personal lifestyle priorities to receive a custom 50/30/20 budget with needs, wants, and emergency fund allocations.
- **Zero-Failure Fallback Engine**: If a Gemini API key is not configured or network quotas are exceeded, the app switches to an intelligent local heuristic analysis engine without error crashes.
- Clear informational disclaimer on all AI recommendations.

### 7. 🩺 Deterministic Financial Health Score (0 - 100)
- Transparent, rule-based scoring (not solely an AI black box):
  - **Savings Rate** (up to 25 pts)
  - **Expense-to-Income Ratio** (up to 25 pts)
  - **Budget Adherence** (up to 25 pts)
  - **Emergency Fund & Goal Progress** (up to 15 pts)
  - **Cash Flow / Overspending Check** (up to 10 pts)
- Displays overall score, score tier (*Excellent, Good, Fair, Needs Attention*), key strengths, and areas for improvement with detailed criteria explanations.

### 8. 🪄 One-Click Demo Data
- Option to load realistic sample financial records (Income, Expenses, Budgets, Saving Goals, Categories) with a single click from the navigation bar or profile screen.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, Flask 3.1, SQLAlchemy 2.1, Flask-Login, Flask-WTF, WTForms
- **Database**: SQLite (Local development default), PostgreSQL compatible
- **AI Integration**: Google Gemini API (`google-genai` SDK & REST endpoints)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6+), Bootstrap 5.3, Bootstrap Icons
- **Data Visualizations**: Chart.js 4.4
- **WSGI Production**: Waitress (Windows) / Gunicorn (Linux/macOS)
- **Testing**: Pytest 9.1 with automated fixtures and 100% route coverage

---

## 📁 Folder Structure

```
Personal-Finance-Advisor-Bot/
├── app/
│   ├── __init__.py             # Flask application factory, extensions, and blueprints
│   ├── models.py               # SQLAlchemy models (User, Income, Expense, Budget, SavingGoal, etc.)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py             # Auth routes (register, login, logout, profile, demo data)
│   │   ├── main.py             # Dashboard and home views
│   │   ├── finance.py          # CRUD for Income, Expenses, Categories
│   │   ├── budget.py           # Budget planning and AI budget application
│   │   ├── savings.py          # Saving goals tracking and deposit actions
│   │   ├── advisor.py          # Gemini AI analysis and budget generator
│   │   ├── health.py           # Deterministic health scoring view
│   │   └── api.py              # JSON endpoints for Chart.js
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py   # Gemini API client, prompts, JSON parsers & fallback engine
│   │   ├── health_service.py   # Rule-based financial health scoring calculator
│   │   ├── finance_service.py  # Data aggregation, trends, and budget calculations
│   │   └── demo_service.py     # Sample data seeder
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Premium SaaS styles, stat cards, overlays
│   │   └── js/
│   │       ├── main.js         # Toasts, sidebar toggle, AI overlays
│   │       └── dashboard_charts.js # Chart.js configuration
│   ├── templates/
│   │   ├── base.html           # Layout with sidebar, navbar, toasts, modals
│   │   ├── dashboard.html      # Central dashboard with KPIs and charts
│   │   ├── income.html         # Income list & form
│   │   ├── income_edit.html    # Edit income record
│   │   ├── expenses.html       # Expense list, category filter & form
│   │   ├── expense_edit.html   # Edit expense record
│   │   ├── categories.html     # Category management
│   │   ├── budgets.html        # Budget planning & progress bars
│   │   ├── savings.html        # Saving goals & quick deposit
│   │   ├── savings_edit.html   # Edit saving goal
│   │   ├── advisor.html        # AI Advisor audit & AI Budget Generator
│   │   ├── health.html         # Detailed health score breakdown
│   │   ├── profile.html        # Profile & password management
│   │   ├── auth/
│   │   │   ├── login.html      # Sign in page
│   │   │   └── register.html   # Registration page
│   │   └── errors/
│   │       ├── 404.html
│   │       ├── 403.html
│   │       └── 500.html
│   └── utils/
│       ├── __init__.py
│       └── forms.py            # Flask-WTF form classes with CSRF and validation
├── instance/                   # Local SQLite storage directory
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures, test database, auth helpers
│   ├── test_auth.py            # Register, login, logout, protected routes
│   ├── test_finance.py         # Income, Expense, Category CRUD tests
│   ├── test_budget.py          # Budget utilization and AI budget application
│   ├── test_savings.py         # Saving goal tracking and deposits
│   ├── test_health.py          # Financial health calculation tests
│   └── test_isolation.py       # Cross-user authorization and data isolation tests
├── config.py                   # Dev, Test, Prod configuration classes
├── run.py                      # Local development runner
├── wsgi.py                     # Production WSGI server runner
├── requirements.txt            # Dependency manifest
├── .env.example                # Example environment configuration
└── README.md
```

---

## 🚀 Quickstart & Installation

### 1. Clone the repository and navigate into the folder
```bash
git clone <repository_url>
cd Personal-Finance-Advisor-Bot
```

### 2. Create and activate a Python virtual environment
```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install required dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` to configure your settings:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=generate-a-secure-random-secret-key
DATABASE_URL=sqlite:///instance/personal_finance.db
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
DEBUG=True
```

> **Note**: To obtain a free Google Gemini API key, visit [Google AI Studio](https://aistudio.google.com/). If left unset, the application automatically runs in smart heuristic mode so all features remain functional.

---

## 🏃 Running the Application

### Development Server:
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Production Server:
- **Windows (Waitress)**:
  ```bash
  python wsgi.py
  ```
- **Linux / macOS (Gunicorn)**:
  ```bash
  gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
  ```

---

## 🧪 Running Automated Tests

Run the complete test suite with verbose output:
```bash
pytest -v
```

All 16 test cases verify:
- User registration and duplicate prevention
- Login, session persistence, and logout
- Protection of all private routes
- Income, Expense, and Category CRUD workflows
- Budget utilization and overspending detection
- Applying AI-generated budgets to database
- Savings goal tracking and deposits
- Deterministic financial health scoring rules
- Multi-tenant user data isolation and 403 authorization barriers

---

## 🛡️ Security Features

1. **Password Hashing**: Werkzeug's `generate_password_hash` with secure PBKDF2/SHA-256 salt.
2. **Session Protection**: Flask-Login session management with `HttpOnly` and `SameSite=Lax` cookies.
3. **CSRF Defense**: All POST requests validate CSRF tokens via Flask-WTF.
4. **SQL Injection Defense**: All database operations use SQLAlchemy ORM parameterized queries.
5. **Multi-Tenant Isolation**: Queries strictly filter by `user_id == current_user.id`. Cross-user access triggers HTTP 403 Forbidden.
6. **API Key Security**: Secrets are loaded strictly from environment variables on the backend and are **never exposed** to client-side scripts.
