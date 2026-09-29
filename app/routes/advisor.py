import json
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from app.services.finance_service import get_user_financial_overview
from app.services.gemini_service import analyze_user_finances, generate_ai_budget, DISCLAIMER_TEXT
from app.utils.forms import AIBudgetGenerationForm

advisor_bp = Blueprint('advisor', __name__)


@advisor_bp.route('/', methods=['GET'])
@login_required
def index():
    """AI Financial Advisor dashboard view."""
    overview = get_user_financial_overview(current_user.id)
    budget_form = AIBudgetGenerationForm()

    # Pre-fill budget generation defaults if user has existing income/expenses
    if overview['month_income'] > 0:
        budget_form.monthly_income.data = overview['month_income']

    return render_template(
        'advisor.html',
        overview=overview,
        budget_form=budget_form,
        disclaimer=DISCLAIMER_TEXT
    )


@advisor_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Trigger AI spending analysis on current user data."""
    overview = get_user_financial_overview(current_user.id)
    analysis = analyze_user_finances(overview)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'status': 'success', 'data': analysis})

    budget_form = AIBudgetGenerationForm()
    return render_template(
        'advisor.html',
        overview=overview,
        budget_form=budget_form,
        analysis=analysis,
        disclaimer=DISCLAIMER_TEXT
    )


@advisor_bp.route('/generate-budget', methods=['POST'])
@login_required
def generate_budget():
    """Trigger AI budget generation according to user parameters."""
    form = AIBudgetGenerationForm()
    overview = get_user_financial_overview(current_user.id)

    if form.validate_on_submit():
        result = generate_ai_budget(
            monthly_income=float(form.monthly_income.data),
            fixed_expenses=float(form.fixed_expenses.data or 0.0),
            variable_expenses=float(form.variable_expenses.data or 0.0),
            savings_goal=float(form.savings_goal.data or 0.0),
            financial_goals_text=form.financial_goals.data or ""
        )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({'status': 'success', 'data': result})

        return render_template(
            'advisor.html',
            overview=overview,
            budget_form=form,
            budget_plan=result,
            budget_plan_json=json.dumps(result),
            disclaimer=DISCLAIMER_TEXT
        )
    else:
        flash('Please provide valid numbers for your budget parameters.', 'danger')
        return render_template(
            'advisor.html',
            overview=overview,
            budget_form=form,
            disclaimer=DISCLAIMER_TEXT
        )
