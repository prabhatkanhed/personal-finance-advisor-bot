"""
Demo Data Seeding Service.
Populates an account with realistic sample financial data on user request.
"""

from datetime import date, timedelta
from app import db
from app.models import ExpenseCategory, Income, Expense, Budget, SavingGoal


def seed_demo_data(user_id):
    """Seeds realistic financial history for the specified user."""
    today = date.today()
    cur_month = today.month
    cur_year = today.year

    # 1. Categories
    default_categories = [
        {"name": "Housing", "color": "#3b82f6", "icon": "bi-house-door"},
        {"name": "Groceries", "color": "#10b981", "icon": "bi-cart"},
        {"name": "Dining & Cafes", "color": "#ec4899", "icon": "bi-cup-hot"},
        {"name": "Utilities", "color": "#f59e0b", "icon": "bi-lightning-charge"},
        {"name": "Transportation", "color": "#06b6d4", "icon": "bi-car-front"},
        {"name": "Entertainment", "color": "#8b5cf6", "icon": "bi-controller"},
        {"name": "Healthcare", "color": "#ef4444", "icon": "bi-heart-pulse"},
        {"name": "Shopping", "color": "#6366f1", "icon": "bi-bag"}
    ]

    cat_map = {}
    for cat_data in default_categories:
        existing = ExpenseCategory.query.filter_by(user_id=user_id, name=cat_data["name"]).first()
        if not existing:
            new_cat = ExpenseCategory(
                user_id=user_id,
                name=cat_data["name"],
                color=cat_data["color"],
                icon=cat_data["icon"]
            )
            db.session.add(new_cat)
            db.session.flush()
            cat_map[cat_data["name"]] = new_cat
        else:
            cat_map[cat_data["name"]] = existing

    # 2. Incomes
    sample_incomes = [
        {"source": "Primary Salary", "amount": 4850.00, "day": 1, "desc": "Monthly corporate tech payroll"},
        {"source": "Freelance Consulting", "amount": 850.00, "day": 12, "desc": "UI design client project"},
        {"source": "Investment Dividends", "amount": 165.00, "day": 18, "desc": "Index fund quarterly distribution"}
    ]

    for inc in sample_incomes:
        inc_date = date(cur_year, cur_month, min(inc["day"], 28))
        new_inc = Income(
            user_id=user_id,
            source=inc["source"],
            amount=inc["amount"],
            date=inc_date,
            description=inc["desc"]
        )
        db.session.add(new_inc)

    # Also add previous month income for trend charts
    prev_month = 12 if cur_month == 1 else cur_month - 1
    prev_year = cur_year - 1 if cur_month == 1 else cur_year
    db.session.add(Income(
        user_id=user_id,
        source="Primary Salary",
        amount=4850.00,
        date=date(prev_year, prev_month, 1),
        description="Previous month salary"
    ))

    # 3. Expenses
    sample_expenses = [
        {"cat": "Housing", "amount": 1450.00, "day": 2, "desc": "Monthly apartment rent"},
        {"cat": "Utilities", "amount": 145.50, "day": 5, "desc": "Electric & high-speed fiber internet"},
        {"cat": "Groceries", "amount": 185.20, "day": 6, "desc": "Whole Foods weekly grocery haul"},
        {"cat": "Transportation", "amount": 65.00, "day": 8, "desc": "Gas tank refill"},
        {"cat": "Dining & Cafes", "amount": 54.00, "day": 10, "desc": "Dinner with colleagues"},
        {"cat": "Entertainment", "amount": 45.00, "day": 11, "desc": "Movie tickets & cinema snacks"},
        {"cat": "Groceries", "amount": 142.30, "day": 14, "desc": "Trader Joe's groceries"},
        {"cat": "Shopping", "amount": 119.99, "day": 16, "desc": "Ergonomic desk accessories"},
        {"cat": "Healthcare", "amount": 40.00, "day": 19, "desc": "Pharmacy prescriptions & vitamins"},
        {"cat": "Dining & Cafes", "amount": 88.50, "day": 21, "desc": "Weekend brunch with friends"}
    ]

    for exp in sample_expenses:
        exp_date = date(cur_year, cur_month, min(exp["day"], 28))
        cat_obj = cat_map.get(exp["cat"])
        new_exp = Expense(
            user_id=user_id,
            category_id=cat_obj.id if cat_obj else None,
            amount=exp["amount"],
            date=exp_date,
            description=exp["desc"]
        )
        db.session.add(new_exp)

    # Previous month expenses for trend
    db.session.add(Expense(
        user_id=user_id,
        category_id=cat_map.get("Housing").id if "Housing" in cat_map else None,
        amount=1450.00,
        date=date(prev_year, prev_month, 2),
        description="Previous month rent"
    ))
    db.session.add(Expense(
        user_id=user_id,
        category_id=cat_map.get("Groceries").id if "Groceries" in cat_map else None,
        amount=420.00,
        date=date(prev_year, prev_month, 10),
        description="Previous month groceries"
    ))

    # 4. Budgets
    sample_budgets = [
        {"cat": "Housing", "amount": 1500.00},
        {"cat": "Groceries", "amount": 450.00},
        {"cat": "Dining & Cafes", "amount": 200.00},
        {"cat": "Utilities", "amount": 180.00},
        {"cat": "Transportation", "amount": 150.00},
        {"cat": "Entertainment", "amount": 120.00},
        {"cat": "Shopping", "amount": 200.00}
    ]

    for b in sample_budgets:
        existing_b = Budget.query.filter_by(
            user_id=user_id,
            category=b["cat"],
            month=cur_month,
            year=cur_year
        ).first()
        if not existing_b:
            db.session.add(Budget(
                user_id=user_id,
                category=b["cat"],
                amount=b["amount"],
                month=cur_month,
                year=cur_year
            ))

    # 5. Saving Goals
    sample_goals = [
        {
            "name": "6-Month Emergency Fund",
            "target": 12000.00,
            "current": 8450.00,
            "date": today + timedelta(days=120)
        },
        {
            "name": "Vacation in Tokyo, Japan",
            "target": 4500.00,
            "current": 2900.00,
            "date": today + timedelta(days=210)
        },
        {
            "name": "Upgraded Developer Laptop",
            "target": 2200.00,
            "current": 1850.00,
            "date": today + timedelta(days=45)
        }
    ]

    for g in sample_goals:
        existing_g = SavingGoal.query.filter_by(user_id=user_id, goal_name=g["name"]).first()
        if not existing_g:
            db.session.add(SavingGoal(
                user_id=user_id,
                goal_name=g["name"],
                target_amount=g["target"],
                current_amount=g["current"],
                target_date=g["date"]
            ))

    db.session.commit()
    return True
