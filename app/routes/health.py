from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.finance_service import get_user_financial_overview
from app.services.health_service import calculate_financial_health

health_bp = Blueprint('health', __name__)


@health_bp.route('/', methods=['GET'])
@login_required
def index():
    overview = get_user_financial_overview(current_user.id)
    health = calculate_financial_health(
        income_total=overview['month_income'],
        expense_total=overview['month_expense'],
        budgets_status=overview['budgets_status'],
        saving_goals=overview['goals']
    )

    return render_template(
        'health.html',
        overview=overview,
        health=health
    )
