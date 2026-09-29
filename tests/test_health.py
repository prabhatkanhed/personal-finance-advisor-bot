from app.services.health_service import calculate_financial_health


def test_financial_health_calculation_excellent():
    # User with strong income, low expenses, disciplined budget
    health = calculate_financial_health(
        income_total=6000.0,
        expense_total=2500.0,
        budgets_status=[
            {'budget_amount': 2800.0, 'spent_amount': 2500.0, 'is_over_budget': False}
        ],
        saving_goals=[]
    )
    assert health['score'] >= 75
    assert health['tier'] in ('Good', 'Excellent')
    assert len(health['strengths']) > 0
    assert len(health['breakdown']) == 5


def test_financial_health_calculation_deficit():
    # User operating at a severe deficit with overspending
    health = calculate_financial_health(
        income_total=3000.0,
        expense_total=4500.0,
        budgets_status=[
            {'budget_amount': 2500.0, 'spent_amount': 4500.0, 'is_over_budget': True}
        ],
        saving_goals=[]
    )
    assert health['score'] < 50
    assert health['tier'] == 'Needs Attention'
    assert len(health['improvements']) > 0


def test_health_route(client, sample_user, auth):
    auth.login()
    res = client.get('/health/')
    assert res.status_code == 200
    assert b'Health' in res.data
    assert b'Transparent Scoring Methodology' in res.data
