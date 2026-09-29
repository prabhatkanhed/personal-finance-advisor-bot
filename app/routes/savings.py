from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import SavingGoal
from app.utils.forms import SavingGoalForm, AddFundsForm

savings_bp = Blueprint('savings', __name__)


@savings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = SavingGoalForm()
    deposit_form = AddFundsForm()

    if form.validate_on_submit():
        new_goal = SavingGoal(
            user_id=current_user.id,
            goal_name=form.goal_name.data.strip(),
            target_amount=float(form.target_amount.data),
            current_amount=float(form.current_amount.data or 0.0),
            target_date=form.target_date.data
        )
        db.session.add(new_goal)
        db.session.commit()
        flash(f'Goal "{new_goal.goal_name}" created successfully.', 'success')
        return redirect(url_for('savings.index'))

    goals = SavingGoal.query.filter_by(user_id=current_user.id).order_by(SavingGoal.target_date.asc()).all()
    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    overall_progress = round((total_saved / total_target * 100), 1) if total_target > 0 else 0.0

    return render_template(
        'savings.html',
        form=form,
        deposit_form=deposit_form,
        goals=goals,
        total_target=total_target,
        total_saved=total_saved,
        overall_progress=overall_progress
    )


@savings_bp.route('/<int:id>/deposit', methods=['POST'])
@login_required
def add_funds(id):
    goal = SavingGoal.query.get_or_404(id)
    if goal.user_id != current_user.id:
        abort(403)

    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Deposit amount must be positive.', 'danger')
        else:
            goal.current_amount = round(goal.current_amount + amount, 2)
            db.session.commit()
            if goal.is_completed:
                flash(f'Congratulations! You have reached your goal for "{goal.goal_name}"! 🎉', 'success')
            else:
                flash(f'Added ${amount:,.2f} to "{goal.goal_name}".', 'success')
    except (ValueError, TypeError):
        flash('Invalid deposit amount entered.', 'danger')

    return redirect(url_for('savings.index'))


@savings_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_goal(id):
    goal = SavingGoal.query.get_or_404(id)
    if goal.user_id != current_user.id:
        abort(403)

    form = SavingGoalForm(obj=goal)
    if form.validate_on_submit():
        goal.goal_name = form.goal_name.data.strip()
        goal.target_amount = float(form.target_amount.data)
        goal.current_amount = float(form.current_amount.data or 0.0)
        goal.target_date = form.target_date.data
        db.session.commit()
        flash('Savings goal updated successfully.', 'success')
        return redirect(url_for('savings.index'))

    return render_template('savings_edit.html', form=form, goal=goal)


@savings_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_goal(id):
    goal = SavingGoal.query.get_or_404(id)
    if goal.user_id != current_user.id:
        abort(403)

    db.session.delete(goal)
    db.session.commit()
    flash('Savings goal removed.', 'info')
    return redirect(url_for('savings.index'))
