from datetime import date
from app import db
from app.models import Income, Expense, Budget, SavingGoal


def test_user_data_isolation(client, sample_user, sample_user_2, auth):
    # Setup data owned by User 2 (Bob)
    bob_income = Income(
        user_id=sample_user_2.id,
        source='Bob Secret Consulting',
        amount=9999.00,
        date=date.today()
    )
    bob_expense = Expense(
        user_id=sample_user_2.id,
        amount=450.00,
        date=date.today(),
        description='Bob Secret Expense'
    )
    bob_budget = Budget(
        user_id=sample_user_2.id,
        category='Secret Cat',
        amount=800.00,
        month=date.today().month,
        year=date.today().year
    )
    bob_goal = SavingGoal(
        user_id=sample_user_2.id,
        goal_name='Bob Secret Yacht',
        target_amount=50000.00,
        current_amount=10000.00,
        target_date=date.today()
    )
    db.session.add_all([bob_income, bob_expense, bob_budget, bob_goal])
    db.session.commit()

    bob_inc_id = bob_income.id
    bob_exp_id = bob_expense.id
    bob_b_id = bob_budget.id
    bob_goal_id = bob_goal.id

    # Now login as User 1 (Alice)
    auth.login(email='alice@example.com', password='Password123!')

    # 1. Alice should not see Bob's items on Alice's dashboard
    dash_res = client.get('/dashboard')
    assert b'Bob Secret Consulting' not in dash_res.data
    assert b'9,999.00' not in dash_res.data
    assert b'Bob Secret Expense' not in dash_res.data

    # 2. Alice attempts to edit Bob's income -> 403
    res = client.get(f'/finance/income/{bob_inc_id}/edit')
    assert res.status_code == 403

    # 3. Alice attempts to delete Bob's income -> 403
    res = client.post(f'/finance/income/{bob_inc_id}/delete')
    assert res.status_code == 403

    # 4. Alice attempts to edit Bob's expense -> 403
    res = client.get(f'/finance/expenses/{bob_exp_id}/edit')
    assert res.status_code == 403

    # 5. Alice attempts to delete Bob's expense -> 403
    res = client.post(f'/finance/expenses/{bob_exp_id}/delete')
    assert res.status_code == 403

    # 6. Alice attempts to delete Bob's budget -> 403
    res = client.post(f'/budgets/{bob_b_id}/delete')
    assert res.status_code == 403

    # 7. Alice attempts to deposit or edit Bob's saving goal -> 403
    res = client.post(f'/savings/{bob_goal_id}/deposit', data={'amount': '50.00'})
    assert res.status_code == 403

    res = client.post(f'/savings/{bob_goal_id}/delete')
    assert res.status_code == 403

    # Verify Bob's records are completely intact in database
    assert Income.query.get(bob_inc_id) is not None
    assert Expense.query.get(bob_exp_id) is not None
    assert Budget.query.get(bob_b_id) is not None
    assert SavingGoal.query.get(bob_goal_id) is not None
