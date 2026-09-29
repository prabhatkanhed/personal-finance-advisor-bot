from datetime import date
from app import db
from app.models import Income, Expense, ExpenseCategory


def test_income_crud(client, sample_user, auth):
    auth.login()

    # 1. Create Income
    res = client.post('/finance/income', data={
        'source': 'Salary Tech Corp',
        'amount': '4200.00',
        'date': '2026-09-01',
        'description': 'Monthly paycheck'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Salary Tech Corp' in res.data
    assert b'4,200.00' in res.data

    inc = Income.query.filter_by(source='Salary Tech Corp').first()
    assert inc is not None
    assert inc.amount == 4200.00

    # 2. Edit Income
    res = client.post(f'/finance/income/{inc.id}/edit', data={
        'source': 'Salary Tech Corp Bonus',
        'amount': '4500.00',
        'date': '2026-09-01',
        'description': 'Updated paycheck with bonus'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Salary Tech Corp Bonus' in res.data

    updated_inc = Income.query.get(inc.id)
    assert updated_inc.amount == 4500.00

    # 3. Delete Income
    res = client.post(f'/finance/income/{inc.id}/delete', follow_redirects=True)
    assert res.status_code == 200
    assert Income.query.get(inc.id) is None


def test_category_crud(client, sample_user, auth):
    auth.login()

    # 1. Create Category
    res = client.post('/finance/categories', data={
        'name': 'Streaming & Media',
        'color': '#8b5cf6',
        'icon': 'bi-play-circle'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Streaming' in res.data

    cat = ExpenseCategory.query.filter_by(name='Streaming & Media').first()
    assert cat is not None

    # 2. Edit Category
    res = client.post(f'/finance/categories/{cat.id}/edit', data={
        'name': 'Streaming Apps',
        'color': '#7c3aed',
        'icon': 'bi-tv'
    }, follow_redirects=True)
    assert res.status_code == 200
    updated_cat = ExpenseCategory.query.get(cat.id)
    assert updated_cat.name == 'Streaming Apps'

    # 3. Delete Category
    res = client.post(f'/finance/categories/{cat.id}/delete', follow_redirects=True)
    assert res.status_code == 200
    assert ExpenseCategory.query.get(cat.id) is None


def test_expense_crud(client, sample_user, auth):
    auth.login()

    # Create category first
    cat = ExpenseCategory(user_id=sample_user.id, name='Dining', color='#ec4899', icon='bi-cup-hot')
    db.session.add(cat)
    db.session.commit()

    # 1. Create Expense
    res = client.post('/finance/expenses', data={
        'category_id': str(cat.id),
        'amount': '85.50',
        'date': '2026-09-15',
        'description': 'Family dinner'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'85.50' in res.data
    assert b'Family dinner' in res.data

    exp = Expense.query.filter_by(description='Family dinner').first()
    assert exp is not None
    assert exp.amount == 85.50

    # 2. Edit Expense
    res = client.post(f'/finance/expenses/{exp.id}/edit', data={
        'category_id': str(cat.id),
        'amount': '95.00',
        'date': '2026-09-15',
        'description': 'Family dinner with dessert'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'95.00' in res.data

    updated_exp = Expense.query.get(exp.id)
    assert updated_exp.amount == 95.00

    # 3. Delete Expense
    res = client.post(f'/finance/expenses/{exp.id}/delete', follow_redirects=True)
    assert res.status_code == 200
    assert Expense.query.get(exp.id) is None
