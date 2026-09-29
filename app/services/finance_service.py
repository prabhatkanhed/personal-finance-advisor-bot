"""
Financial Data Aggregation and Analytics Service.
Handles financial summaries, trends, category distributions, and budget comparisons.
"""

from datetime import datetime, date
from calendar import monthrange
from sqlalchemy import func, extract
from app import db
from app.models import Income, Expense, ExpenseCategory, Budget, SavingGoal


def get_current_month_year():
    now = datetime.utcnow()
    return now.month, now.year


def get_user_financial_overview(user_id, month=None, year=None):
    """
    Computes a comprehensive overview of user finances for the given month and year.
    Defaults to current UTC month/year.
    """
    if month is None or year is None:
        month, year = get_current_month_year()

    # Total income for the selected month
    month_income = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
        Income.user_id == user_id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).scalar()

    # Total expenses for the selected month
    month_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).scalar()

    # All-time income & expense
    all_time_income = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
        Income.user_id == user_id
    ).scalar()

    all_time_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.user_id == user_id
    ).scalar()

    current_balance = all_time_income - all_time_expense

    # Total current savings across all goals
    total_savings = db.session.query(func.coalesce(func.sum(SavingGoal.current_amount), 0.0)).filter(
        SavingGoal.user_id == user_id
    ).scalar()

    # Budgets for selected month
    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()
    total_budget = sum(b.amount for b in budgets) if budgets else 0.0

    # Budget utilization
    budget_utilization = 0.0
    if total_budget > 0:
        budget_utilization = min(999.0, round((month_expense / total_budget) * 100, 1))

    # Top spending categories for current month
    top_categories_query = db.session.query(
        func.coalesce(ExpenseCategory.name, 'Uncategorized').label('category_name'),
        func.coalesce(ExpenseCategory.color, '#6366f1').label('color'),
        func.sum(Expense.amount).label('total_amount')
    ).outerjoin(ExpenseCategory, Expense.category_id == ExpenseCategory.id).filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).group_by(ExpenseCategory.name, ExpenseCategory.color).order_by(func.sum(Expense.amount).desc()).limit(5).all()

    top_categories = [
        {
            'name': item.category_name,
            'color': item.color,
            'amount': round(item.total_amount, 2),
            'percentage': round((item.total_amount / month_expense * 100), 1) if month_expense > 0 else 0
        }
        for item in top_categories_query
    ]

    # Recent transactions (mix of latest 5 incomes and 5 expenses, ordered by date)
    recent_incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc(), Income.id.desc()).limit(5).all()
    recent_expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc(), Expense.id.desc()).limit(5).all()

    combined_transactions = []
    for inc in recent_incomes:
        combined_transactions.append({
            'type': 'income',
            'id': inc.id,
            'title': inc.source,
            'amount': inc.amount,
            'date': inc.date,
            'description': inc.description,
            'badge': 'success'
        })
    for exp in recent_expenses:
        combined_transactions.append({
            'type': 'expense',
            'id': exp.id,
            'title': exp.category.name if exp.category else 'Uncategorized',
            'amount': exp.amount,
            'date': exp.date,
            'description': exp.description,
            'badge': 'danger'
        })

    combined_transactions.sort(key=lambda x: (x['date'], x['id']), reverse=True)
    recent_transactions = combined_transactions[:6]

    # Saving goals
    goals = SavingGoal.query.filter_by(user_id=user_id).order_by(SavingGoal.target_date.asc()).all()

    # Detailed status of each budget item
    budgets_status = get_budgets_status(user_id, month, year)

    return {
        'month': month,
        'year': year,
        'month_name': date(year, month, 1).strftime('%B'),
        'month_income': round(month_income, 2),
        'month_expense': round(month_expense, 2),
        'month_savings': round(max(0.0, month_income - month_expense), 2),
        'all_time_income': round(all_time_income, 2),
        'all_time_expense': round(all_time_expense, 2),
        'current_balance': round(current_balance, 2),
        'total_savings': round(total_savings, 2),
        'total_budget': round(total_budget, 2),
        'remaining_budget': round(max(0.0, total_budget - month_expense), 2),
        'budget_utilization': budget_utilization,
        'is_over_budget': month_expense > total_budget if total_budget > 0 else False,
        'top_categories': top_categories,
        'recent_transactions': recent_transactions,
        'goals': goals,
        'budgets_status': budgets_status
    }


def get_budgets_status(user_id, month=None, year=None):
    """
    Returns spending vs budget for all user budgets in specified month.
    """
    if month is None or year is None:
        month, year = get_current_month_year()

    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()
    status_list = []

    for b in budgets:
        if b.category.lower() == 'overall':
            # Overall spending across all categories
            spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
                Expense.user_id == user_id,
                extract('month', Expense.date) == month,
                extract('year', Expense.date) == year
            ).scalar()
        else:
            # Category-specific spending
            cat = ExpenseCategory.query.filter_by(user_id=user_id, name=b.category).first()
            if cat:
                spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
                    Expense.user_id == user_id,
                    Expense.category_id == cat.id,
                    extract('month', Expense.date) == month,
                    extract('year', Expense.date) == year
                ).scalar()
            else:
                spent = 0.0

        spent = float(spent or 0.0)
        limit = float(b.amount)
        utilization = round((spent / limit) * 100, 1) if limit > 0 else 0.0
        remaining = max(0.0, round(limit - spent, 2))
        is_over = spent > limit

        status_list.append({
            'id': b.id,
            'category': b.category,
            'budget_amount': round(limit, 2),
            'spent_amount': round(spent, 2),
            'remaining_amount': remaining,
            'utilization': utilization,
            'is_over_budget': is_over,
            'progress_bar_class': 'bg-danger' if is_over else ('bg-warning' if utilization > 80 else 'bg-success')
        })

    return status_list


def get_monthly_spending_trends(user_id, num_months=6):
    """
    Returns monthly labels, income series, and expense series for Chart.js.
    """
    now = datetime.utcnow()
    labels = []
    income_data = []
    expense_data = []

    # Iterate back num_months in chronological order
    month_tuples = []
    cur_y = now.year
    cur_m = now.month

    for _ in range(num_months):
        month_tuples.append((cur_y, cur_m))
        cur_m -= 1
        if cur_m == 0:
            cur_m = 12
            cur_y -= 1

    month_tuples.reverse()

    for y, m in month_tuples:
        m_label = date(y, m, 1).strftime('%b %Y')
        labels.append(m_label)

        inc = db.session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
            Income.user_id == user_id,
            extract('month', Income.date) == m,
            extract('year', Income.date) == y
        ).scalar()
        income_data.append(round(float(inc), 2))

        exp = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
            Expense.user_id == user_id,
            extract('month', Expense.date) == m,
            extract('year', Expense.date) == y
        ).scalar()
        expense_data.append(round(float(exp), 2))

    return {
        'labels': labels,
        'income': income_data,
        'expense': expense_data
    }


def get_category_spending_breakdown(user_id, month=None, year=None):
    """
    Returns category names, amounts, and colors for donut chart.
    """
    if month is None or year is None:
        month, year = get_current_month_year()

    results = db.session.query(
        func.coalesce(ExpenseCategory.name, 'Uncategorized').label('name'),
        func.coalesce(ExpenseCategory.color, '#94a3b8').label('color'),
        func.sum(Expense.amount).label('total')
    ).outerjoin(ExpenseCategory, Expense.category_id == ExpenseCategory.id).filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).group_by(ExpenseCategory.name, ExpenseCategory.color).all()

    labels = [r.name for r in results]
    data = [round(float(r.total), 2) for r in results]
    colors = [r.color for r in results]

    if not labels:
        labels = ['No Expenses Yet']
        data = [0]
        colors = ['#cbd5e1']

    return {
        'labels': labels,
        'data': data,
        'colors': colors
    }
