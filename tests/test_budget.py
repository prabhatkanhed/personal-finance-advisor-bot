import json
from datetime import date
from app import db
from app.models import Budget, Expense, ExpenseCategory
from app.services.finance_service import get_budgets_status


def test_budget_crud_and_calculations(client, sample_user, auth):
    auth.login()

    # Create category
    cat = ExpenseCategory(user_id=sample_user.id, name='Groceries', color='#10b981')
    db.session.add(cat)
    db.session.commit()

    # 1. Set Budget
    res = client.post('/budgets/', data={
        'category': 'Groceries',
        'amount': '500.00',
        'month': 9,
        'year': 2026
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'500.00' in res.data

    b = Budget.query.filter_by(user_id=sample_user.id, category='Groceries').first()
    assert b is not None
    assert b.amount == 500.00

    # 2. Add Expense under budget
    exp = Expense(
        user_id=sample_user.id,
        category_id=cat.id,
        amount=350.00,
        date=date(2026, 9, 10),
        description='Supermarket run'
    )
    db.session.add(exp)
    db.session.commit()

    status = get_budgets_status(sample_user.id, month=9, year=2026)
    assert len(status) == 1
    assert status[0]['spent_amount'] == 350.00
    assert status[0]['utilization'] == 70.0
    assert status[0]['is_over_budget'] is False
    assert status[0]['remaining_amount'] == 150.00

    # 3. Add Expense to trigger overspending
    exp_over = Expense(
        user_id=sample_user.id,
        category_id=cat.id,
        amount=200.00,
        date=date(2026, 9, 20),
        description='Additional groceries'
    )
    db.session.add(exp_over)
    db.session.commit()

    status_over = get_budgets_status(sample_user.id, month=9, year=2026)
    assert status_over[0]['spent_amount'] == 550.00
    assert status_over[0]['is_over_budget'] is True
    assert status_over[0]['utilization'] == 110.0

    # 4. Delete Budget
    res = client.post(f'/budgets/{b.id}/delete', follow_redirects=True)
    assert res.status_code == 200
    assert Budget.query.get(b.id) is None


def test_apply_ai_budget(client, sample_user, auth):
    auth.login()

    ai_plan = {
        "needs": {
            "total": 2000.0,
            "categories": [
                {"name": "Housing Rent", "amount": 1400.0},
                {"name": "Groceries Food", "amount": 600.0}
            ]
        },
        "wants": {
            "total": 800.0,
            "categories": [
                {"name": "Dining Takeout", "amount": 500.0},
                {"name": "Entertainment Fun", "amount": 300.0}
            ]
        }
    }

    res = client.post('/budgets/apply-ai-budget', data={
        'budget_json': json.dumps(ai_plan)
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'applied' in res.data.lower()

    # Verify budgets created
    budgets = Budget.query.filter_by(user_id=sample_user.id).all()
    categories_set = {b.category for b in budgets}
    assert 'Housing Rent' in categories_set
    assert 'Groceries Food' in categories_set
    assert 'Dining Takeout' in categories_set
    assert 'Entertainment Fun' in categories_set
