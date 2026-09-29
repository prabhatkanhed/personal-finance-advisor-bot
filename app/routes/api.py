from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.finance_service import (
    get_user_financial_overview,
    get_monthly_spending_trends,
    get_category_spending_breakdown
)
from app.models import SavingGoal

api_bp = Blueprint('api', __name__)


@api_bp.route('/charts/income-vs-expense')
@login_required
def chart_income_vs_expense():
    now = datetime.utcnow()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)

    overview = get_user_financial_overview(current_user.id, month=month, year=year)

    return jsonify({
        'labels': ['Total Income', 'Total Expenses', 'Net Savings'],
        'data': [overview['month_income'], overview['month_expense'], overview['month_savings']],
        'backgroundColor': ['#10b981', '#ef4444', '#3b82f6']
    })


@api_bp.route('/charts/monthly-trends')
@login_required
def chart_monthly_trends():
    trends = get_monthly_spending_trends(current_user.id, num_months=6)
    return jsonify(trends)


@api_bp.route('/charts/category-distribution')
@login_required
def chart_category_distribution():
    now = datetime.utcnow()
    month = request.args.get('month', now.month, type=int)
    year = request.args.get('year', now.year, type=int)

    breakdown = get_category_spending_breakdown(current_user.id, month=month, year=year)
    return jsonify(breakdown)


@api_bp.route('/charts/savings-progress')
@login_required
def chart_savings_progress():
    goals = SavingGoal.query.filter_by(user_id=current_user.id).all()
    labels = [g.goal_name for g in goals] or ['No Goals Yet']
    current_vals = [g.current_amount for g in goals] or [0]
    target_vals = [g.target_amount for g in goals] or [0]

    return jsonify({
        'labels': labels,
        'current': current_vals,
        'target': target_vals
    })


@api_bp.route('/summary')
@login_required
def api_summary():
    overview = get_user_financial_overview(current_user.id)
    return jsonify(overview)
