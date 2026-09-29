from datetime import date, timedelta
from app.models import SavingGoal


def test_savings_goals(client, sample_user, auth):
    auth.login()

    # 1. Create Goal
    due_date = date.today() + timedelta(days=90)
    res = client.post('/savings/', data={
        'goal_name': 'Emergency Buffer',
        'target_amount': '3000.00',
        'current_amount': '1000.00',
        'target_date': due_date.strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Emergency Buffer' in res.data

    goal = SavingGoal.query.filter_by(goal_name='Emergency Buffer').first()
    assert goal is not None
    assert goal.progress_percentage == 33.3
    assert goal.remaining_amount == 2000.00
    assert goal.is_completed is False

    # 2. Deposit Funds
    res = client.post(f'/savings/{goal.id}/deposit', data={'amount': '500.00'}, follow_redirects=True)
    assert res.status_code == 200
    goal = SavingGoal.query.get(goal.id)
    assert goal.current_amount == 1500.00
    assert goal.progress_percentage == 50.0

    # 3. Complete Goal by Depositing remainder
    res = client.post(f'/savings/{goal.id}/deposit', data={'amount': '1500.00'}, follow_redirects=True)
    assert res.status_code == 200
    goal = SavingGoal.query.get(goal.id)
    assert goal.current_amount == 3000.00
    assert goal.is_completed is True
    assert goal.progress_percentage == 100.0

    # 4. Edit Goal
    res = client.post(f'/savings/{goal.id}/edit', data={
        'goal_name': 'Emergency Fund Extended',
        'target_amount': '5000.00',
        'current_amount': '3000.00',
        'target_date': due_date.strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert res.status_code == 200
    goal = SavingGoal.query.get(goal.id)
    assert goal.goal_name == 'Emergency Fund Extended'
    assert goal.target_amount == 5000.00
    assert goal.is_completed is False

    # 5. Delete Goal
    res = client.post(f'/savings/{goal.id}/delete', follow_redirects=True)
    assert res.status_code == 200
    assert SavingGoal.query.get(goal.id) is None
