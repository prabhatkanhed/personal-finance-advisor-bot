from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.utils.forms import LoginForm
from app.services.finance_service import get_user_financial_overview
from app.services.health_service import calculate_financial_health

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    return render_template('auth/login.html', form=form)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Allow filtering by month and year via query params, defaulting to current
    now = datetime.utcnow()
    try:
        month = int(request.args.get('month', now.month))
        year = int(request.args.get('year', now.year))
    except (ValueError, TypeError):
        month, year = now.month, now.year

    # Retrieve comprehensive financial data for this user
    overview = get_user_financial_overview(current_user.id, month=month, year=year)

    # Compute financial health score
    health = calculate_financial_health(
        income_total=overview['month_income'],
        expense_total=overview['month_expense'],
        budgets_status=overview['budgets_status'],
        saving_goals=overview['goals']
    )

    return render_template(
        'dashboard.html',
        overview=overview,
        health=health,
        selected_month=month,
        selected_year=year
    )

