from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Income, Expense, ExpenseCategory
from app.utils.forms import IncomeForm, ExpenseForm, CategoryForm

finance_bp = Blueprint('finance', __name__)


# -------------------------------------------------------------
# INCOME CRUD
# -------------------------------------------------------------
@finance_bp.route('/income', methods=['GET', 'POST'])
@login_required
def income_list():
    form = IncomeForm()
    if form.validate_on_submit():
        new_income = Income(
            user_id=current_user.id,
            source=form.source.data.strip(),
            amount=float(form.amount.data),
            date=form.date.data,
            description=form.description.data.strip() if form.description.data else None
        )
        db.session.add(new_income)
        db.session.commit()
        flash('Income entry added successfully.', 'success')
        return redirect(url_for('finance.income_list'))

    # Query all income entries for current user
    page = request.args.get('page', 1, type=int)
    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc(), Income.id.desc()).paginate(page=page, per_page=15)
    total_income = sum(i.amount for i in Income.query.filter_by(user_id=current_user.id).all())

    return render_template('income.html', form=form, incomes=incomes, total_income=total_income)


@finance_bp.route('/income/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_income(id):
    income = db.get_or_404(Income, id)
    if income.user_id != current_user.id:
        abort(403)

    form = IncomeForm(obj=income)
    if form.validate_on_submit():
        income.source = form.source.data.strip()
        income.amount = float(form.amount.data)
        income.date = form.date.data
        income.description = form.description.data.strip() if form.description.data else None
        db.session.commit()
        flash('Income entry updated successfully.', 'success')
        return redirect(url_for('finance.income_list'))

    return render_template('income_edit.html', form=form, income=income)


@finance_bp.route('/income/<int:id>/delete', methods=['POST'])
@login_required
def delete_income(id):
    income = db.get_or_404(Income, id)
    if income.user_id != current_user.id:
        abort(403)

    db.session.delete(income)
    db.session.commit()
    flash('Income entry deleted.', 'info')
    return redirect(url_for('finance.income_list'))


# -------------------------------------------------------------
# EXPENSE CRUD
# -------------------------------------------------------------
@finance_bp.route('/expenses', methods=['GET', 'POST'])
@login_required
def expense_list():
    form = ExpenseForm()
    # Populate user categories in the dropdown
    user_categories = ExpenseCategory.query.filter_by(user_id=current_user.id).order_by(ExpenseCategory.name).all()
    form.category_id.choices = [(0, 'Select Category (Optional)')] + [(c.id, c.name) for c in user_categories]

    if form.validate_on_submit():
        cat_id = form.category_id.data if form.category_id.data and form.category_id.data > 0 else None
        new_expense = Expense(
            user_id=current_user.id,
            category_id=cat_id,
            amount=float(form.amount.data),
            date=form.date.data,
            description=form.description.data.strip() if form.description.data else None
        )
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense recorded successfully.', 'success')
        return redirect(url_for('finance.expense_list'))

    # Filtering by category
    selected_cat_id = request.args.get('category', type=int)
    query = Expense.query.filter_by(user_id=current_user.id)
    if selected_cat_id:
        query = query.filter_by(category_id=selected_cat_id)

    page = request.args.get('page', 1, type=int)
    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).paginate(page=page, per_page=15)
    total_expenses = sum(e.amount for e in Expense.query.filter_by(user_id=current_user.id).all())

    cat_form = CategoryForm()
    return render_template(
        'expenses.html',
        form=form,
        cat_form=cat_form,
        expenses=expenses,
        categories=user_categories,
        total_expenses=total_expenses,
        selected_cat_id=selected_cat_id
    )


@finance_bp.route('/expenses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    expense = db.get_or_404(Expense, id)
    if expense.user_id != current_user.id:
        abort(403)

    form = ExpenseForm(obj=expense)
    user_categories = ExpenseCategory.query.filter_by(user_id=current_user.id).order_by(ExpenseCategory.name).all()
    form.category_id.choices = [(0, 'None / Uncategorized')] + [(c.id, c.name) for c in user_categories]

    if request.method == 'GET':
        form.category_id.data = expense.category_id or 0

    if form.validate_on_submit():
        expense.category_id = form.category_id.data if form.category_id.data and form.category_id.data > 0 else None
        expense.amount = float(form.amount.data)
        expense.date = form.date.data
        expense.description = form.description.data.strip() if form.description.data else None
        db.session.commit()
        flash('Expense record updated.', 'success')
        return redirect(url_for('finance.expense_list'))

    return render_template('expense_edit.html', form=form, expense=expense)


@finance_bp.route('/expenses/<int:id>/delete', methods=['POST'])
@login_required
def delete_expense(id):
    expense = db.get_or_404(Expense, id)
    if expense.user_id != current_user.id:
        abort(403)

    db.session.delete(expense)
    db.session.commit()
    flash('Expense entry removed.', 'info')
    return redirect(url_for('finance.expense_list'))


# -------------------------------------------------------------
# CATEGORY CRUD
# -------------------------------------------------------------
@finance_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        existing = ExpenseCategory.query.filter_by(user_id=current_user.id, name=name).first()
        if existing:
            flash(f'Category "{name}" already exists.', 'warning')
        else:
            category = ExpenseCategory(
                user_id=current_user.id,
                name=name,
                color=form.color.data.strip(),
                icon=form.icon.data.strip() or 'bi-tag'
            )
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{name}" created.', 'success')
        return redirect(url_for('finance.categories'))

    user_categories = ExpenseCategory.query.filter_by(user_id=current_user.id).order_by(ExpenseCategory.name).all()
    return render_template('categories.html', form=form, categories=user_categories)


@finance_bp.route('/categories/<int:id>/edit', methods=['POST'])
@login_required
def edit_category(id):
    category = ExpenseCategory.query.get_or_404(id)
    if category.user_id != current_user.id:
        abort(403)

    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#6366f1').strip()
    icon = request.form.get('icon', 'bi-tag').strip()

    if name:
        category.name = name
        category.color = color
        category.icon = icon
        db.session.commit()
        flash('Category updated.', 'success')
    else:
        flash('Category name cannot be empty.', 'danger')

    return redirect(url_for('finance.categories'))


@finance_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = db.get_or_404(ExpenseCategory, id)
    if category.user_id != current_user.id:
        abort(403)

    # Detach linked expenses to avoid orphaning issues
    Expense.query.filter_by(category_id=category.id).update({'category_id': None})
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted. Associated expenses are now marked as Uncategorized.', 'info')
    return redirect(url_for('finance.categories'))
