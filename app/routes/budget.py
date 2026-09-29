from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Budget, ExpenseCategory
from app.utils.forms import BudgetForm
from app.services.finance_service import get_budgets_status

budget_bp = Blueprint('budget', __name__)


@budget_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    now = datetime.utcnow()
    try:
        month = int(request.args.get('month', now.month))
        year = int(request.args.get('year', now.year))
    except (ValueError, TypeError):
        month, year = now.month, now.year

    form = BudgetForm()

    # Populate categories dropdown including "Overall"
    categories = ExpenseCategory.query.filter_by(user_id=current_user.id).order_by(ExpenseCategory.name).all()
    form.category.choices = [('Overall', 'Overall Monthly Budget')] + [(c.name, c.name) for c in categories]
    form.month.choices = [(m, datetime(2000, m, 1).strftime('%B')) for m in range(1, 13)]

    if request.method == 'GET':
        form.month.data = month
        form.year.data = year

    if form.validate_on_submit():
        cat_name = form.category.data
        b_month = form.month.data
        b_year = form.year.data
        amount = float(form.amount.data)

        # Check if a budget already exists for this category/month/year
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            category=cat_name,
            month=b_month,
            year=b_year
        ).first()

        if existing:
            existing.amount = amount
            flash(f'Updated budget for {cat_name} ({datetime(2000, b_month, 1).strftime("%B")} {b_year}) to ${amount:,.2f}.', 'success')
        else:
            new_budget = Budget(
                user_id=current_user.id,
                category=cat_name,
                amount=amount,
                month=b_month,
                year=b_year
            )
            db.session.add(new_budget)
            flash(f'Set budget for {cat_name} to ${amount:,.2f}.', 'success')

        db.session.commit()
        return redirect(url_for('budget.index', month=b_month, year=b_year))

    # Retrieve statuses
    status_list = get_budgets_status(current_user.id, month, year)
    total_budgeted = sum(b['budget_amount'] for b in status_list)
    total_spent = sum(b['spent_amount'] for b in status_list)
    remaining = max(0.0, total_budgeted - total_spent)
    overall_utilization = round((total_spent / total_budgeted * 100), 1) if total_budgeted > 0 else 0.0

    return render_template(
        'budgets.html',
        form=form,
        budgets=status_list,
        total_budgeted=total_budgeted,
        total_spent=total_spent,
        remaining=remaining,
        overall_utilization=overall_utilization,
        selected_month=month,
        selected_year=year
    )


@budget_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    if budget.user_id != current_user.id:
        abort(403)

    month = budget.month
    year = budget.year
    db.session.delete(budget)
    db.session.commit()
    flash('Budget target deleted.', 'info')
    return redirect(url_for('budget.index', month=month, year=year))


@budget_bp.route('/apply-ai-budget', methods=['POST'])
@login_required
def apply_ai_budget():
    """
    Applies the structured categories from AI budget generation into actual Budget rows.
    """
    import json
    data_json = request.form.get('budget_json')
    if not data_json:
        flash('No AI budget data found to apply.', 'danger')
        return redirect(url_for('budget.index'))

    try:
        plan = json.loads(data_json)
        now = datetime.utcnow()
        month = now.month
        year = now.year

        categories_added = 0
        # Parse needs categories
        needs_cats = plan.get('needs', {}).get('categories', [])
        wants_cats = plan.get('wants', {}).get('categories', [])

        all_cats = needs_cats + wants_cats

        for item in all_cats:
            cat_name = item.get('name')
            amt = float(item.get('amount', 0))
            if cat_name and amt > 0:
                # Ensure category exists in ExpenseCategory
                cat_obj = ExpenseCategory.query.filter_by(user_id=current_user.id, name=cat_name).first()
                if not cat_obj:
                    cat_obj = ExpenseCategory(user_id=current_user.id, name=cat_name, color='#4f46e5')
                    db.session.add(cat_obj)
                    db.session.flush()

                # Upsert budget
                b = Budget.query.filter_by(user_id=current_user.id, category=cat_name, month=month, year=year).first()
                if b:
                    b.amount = amt
                else:
                    b = Budget(user_id=current_user.id, category=cat_name, amount=amt, month=month, year=year)
                    db.session.add(b)
                categories_added += 1

        db.session.commit()
        flash(f'Successfully applied {categories_added} AI-recommended budget allocations for this month!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Could not apply budget: {str(e)}', 'danger')

    return redirect(url_for('budget.index'))
