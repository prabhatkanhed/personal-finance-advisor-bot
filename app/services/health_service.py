"""
Financial Health Calculation Service.
Provides transparent, deterministic scoring based on clear financial rules.
"""

def calculate_financial_health(income_total, expense_total, budgets_status=None, saving_goals=None):
    """
    Calculate financial health score (0 - 100) using transparent, rule-based criteria.

    Components:
    1. Savings Rate (Max 25 pts)
    2. Expense-to-Income Ratio (Max 25 pts)
    3. Budget Adherence (Max 25 pts)
    4. Emergency / Savings Goals Progress (Max 15 pts)
    5. Overspending Check (Max 10 pts)
    """
    income = float(income_total or 0)
    expense = float(expense_total or 0)
    budgets_status = budgets_status or []
    saving_goals = saving_goals or []

    breakdown = []
    strengths = []
    improvements = []

    # ----------------------------------------------------
    # 1. Savings Rate (25 points max)
    # ----------------------------------------------------
    savings = max(0.0, income - expense)
    savings_rate = (savings / income * 100) if income > 0 else 0.0

    if savings_rate >= 25.0:
        savings_pts = 25
        strengths.append(f"Outstanding savings rate of {savings_rate:.1f}% (target: >20%).")
    elif savings_rate >= 20.0:
        savings_pts = 22
        strengths.append(f"Strong savings rate of {savings_rate:.1f}%, beating standard benchmarks.")
    elif savings_rate >= 15.0:
        savings_pts = 18
        strengths.append(f"Solid savings rate of {savings_rate:.1f}%.")
    elif savings_rate >= 10.0:
        savings_pts = 12
        improvements.append(f"Current savings rate is {savings_rate:.1f}%. Aim to increase it towards 15-20%.")
    elif savings_rate > 0.0:
        savings_pts = 6
        improvements.append(f"Low savings rate ({savings_rate:.1f}%). Trim discretionary spending to build a buffer.")
    else:
        savings_pts = 0
        improvements.append("Zero or negative savings this month. Expenses currently meet or exceed income.")

    breakdown.append({
        'name': 'Savings Rate',
        'score': savings_pts,
        'max_score': 25,
        'percentage': round((savings_pts / 25) * 100),
        'metric': f"{savings_rate:.1f}%",
        'description': 'Measures the proportion of income saved after all monthly expenses.'
    })

    # ----------------------------------------------------
    # 2. Expense-to-Income Ratio (25 points max)
    # ----------------------------------------------------
    expense_ratio = (expense / income * 100) if income > 0 else (100.0 if expense > 0 else 0.0)

    if expense_ratio <= 50.0 and income > 0:
        expense_pts = 25
        strengths.append(f"Frugal spending: expenses account for only {expense_ratio:.1f}% of income.")
    elif expense_ratio <= 70.0:
        expense_pts = 20
        strengths.append(f"Healthy spending ratio: {expense_ratio:.1f}% of income utilized.")
    elif expense_ratio <= 85.0:
        expense_pts = 14
        improvements.append(f"Expenses represent {expense_ratio:.1f}% of income. Keep an eye on lifestyle inflation.")
    elif expense_ratio <= 100.0:
        expense_pts = 7
        improvements.append(f"High expense ratio ({expense_ratio:.1f}%). Little financial cushion remains.")
    else:
        expense_pts = 0
        improvements.append(f"Critical spending level: expenses are {expense_ratio:.1f}% of income (over budget).")

    breakdown.append({
        'name': 'Expense-to-Income Ratio',
        'score': expense_pts,
        'max_score': 25,
        'percentage': round((expense_pts / 25) * 100),
        'metric': f"{expense_ratio:.1f}%",
        'description': 'Measures cash flow pressure. Lower ratios indicate greater financial resilience.'
    })

    # ----------------------------------------------------
    # 3. Budget Adherence (25 points max)
    # ----------------------------------------------------
    if budgets_status:
        total_budget_limit = sum(b['budget_amount'] for b in budgets_status)
        total_budget_spent = sum(b['spent_amount'] for b in budgets_status)
        over_budget_count = sum(1 for b in budgets_status if b['is_over_budget'])

        if total_budget_limit > 0:
            utilization = (total_budget_spent / total_budget_limit) * 100
        else:
            utilization = 100

        if over_budget_count == 0 and utilization <= 95.0:
            budget_pts = 25
            strengths.append(f"Perfect budget discipline: all {len(budgets_status)} categories within limit.")
        elif over_budget_count == 0:
            budget_pts = 21
            strengths.append("Stayed within all budget caps this period.")
        elif over_budget_count == 1 and utilization <= 105.0:
            budget_pts = 14
            improvements.append(f"1 category exceeded budget. Overall spending remained near target.")
        elif over_budget_count <= 2:
            budget_pts = 8
            improvements.append(f"{over_budget_count} categories exceeded budgeted limits.")
        else:
            budget_pts = 2
            improvements.append(f"Multiple categories ({over_budget_count}) significantly exceeded budgets.")

        metric_str = f"{utilization:.1f}% utilized ({over_budget_count} over limit)"
    else:
        # If no explicit category budgets are set yet
        if income > 0 and expense <= income:
            budget_pts = 15
            improvements.append("Create category budgets to unlock the full 25 points for budget discipline.")
            metric_str = "No budgets set (Surplus intact)"
        else:
            budget_pts = 5
            improvements.append("No active budgets. Establishing monthly category budgets is recommended.")
            metric_str = "No budgets set"

    breakdown.append({
        'name': 'Budget Adherence',
        'score': budget_pts,
        'max_score': 25,
        'percentage': round((budget_pts / 25) * 100),
        'metric': metric_str,
        'description': 'Evaluates how closely you stick to planned category spending caps.'
    })

    # ----------------------------------------------------
    # 4. Emergency / Savings Goals Progress (15 points max)
    # ----------------------------------------------------
    if saving_goals:
        avg_progress = sum(g.progress_percentage for g in saving_goals) / len(saving_goals)
        has_emergency_fund = any('emergency' in g.goal_name.lower() for g in saving_goals)

        if avg_progress >= 75:
            savings_goal_pts = 15
            strengths.append(f"Excellent progress on saving goals (averaging {avg_progress:.1f}%).")
        elif avg_progress >= 50:
            savings_goal_pts = 12
            strengths.append(f"Solid progress across active saving goals ({avg_progress:.1f}%).")
        elif avg_progress >= 25:
            savings_goal_pts = 8
            improvements.append(f"Saving goals are at {avg_progress:.1f}% progress. Set recurring contributions.")
        else:
            savings_goal_pts = 4
            improvements.append(f"Early stage on saving goals ({avg_progress:.1f}%). Focus on your primary goal first.")

        if has_emergency_fund:
            strengths.append("Dedicated emergency fund goal actively tracked.")
        else:
            improvements.append("Establish a dedicated Emergency Fund covering 3-6 months of living expenses.")

        goal_metric = f"{avg_progress:.1f}% avg progress ({len(saving_goals)} goals)"
    else:
        savings_goal_pts = 3
        improvements.append("No active savings goals found. Create your first goal to track your wealth building.")
        goal_metric = "0 active goals"

    breakdown.append({
        'name': 'Savings & Goal Progress',
        'score': savings_goal_pts,
        'max_score': 15,
        'percentage': round((savings_goal_pts / 15) * 100),
        'metric': goal_metric,
        'description': 'Measures consistency and progress toward predefined saving milestones.'
    })

    # ----------------------------------------------------
    # 5. Overspending Check (10 points max)
    # ----------------------------------------------------
    if income > 0 and expense <= income:
        if expense <= income * 0.90:
            overspend_pts = 10
            strengths.append("Positive cash flow with a comfortable safety margin.")
        else:
            overspend_pts = 7
            improvements.append("Spending is close to total earnings. Monitor unexpected costs.")
        overspend_metric = f"${(income - expense):,.2f} surplus"
    elif income == 0 and expense == 0:
        overspend_pts = 5
        overspend_metric = "No activity"
    else:
        overspend_pts = 0
        deficit = expense - income
        improvements.append(f"Operating at a cash flow deficit of ${deficit:,.2f} this period.")
        overspend_metric = f"${deficit:,.2f} deficit"

    breakdown.append({
        'name': 'Cash Flow / Overspending',
        'score': overspend_pts,
        'max_score': 10,
        'percentage': round((overspend_pts / 10) * 100),
        'metric': overspend_metric,
        'description': 'Checks whether total monthly outlays remain comfortably below total income.'
    })

    # ----------------------------------------------------
    # Calculate Total Score & Tier
    # ----------------------------------------------------
    total_score = savings_pts + expense_pts + budget_pts + savings_goal_pts + overspend_pts
    total_score = max(0, min(100, total_score))

    if total_score >= 85:
        tier = "Excellent"
        badge_class = "success"
        summary = "Your financial health is outstanding! You demonstrate high savings discipline and healthy spending control."
    elif total_score >= 70:
        tier = "Good"
        badge_class = "primary"
        summary = "Your finances are in good shape with positive cash flow. Minor tweaks will bring you into the top tier."
    elif total_score >= 50:
        tier = "Fair"
        badge_class = "warning"
        summary = "You have a functioning baseline, but tight margins or budget overruns could pose a risk to unexpected shocks."
    else:
        tier = "Needs Attention"
        badge_class = "danger"
        summary = "Your finances require immediate attention. Focus on cutting discretionary expenses and establishing a positive monthly surplus."

    return {
        'score': total_score,
        'tier': tier,
        'badge_class': badge_class,
        'summary': summary,
        'breakdown': breakdown,
        'strengths': strengths,
        'improvements': improvements,
        'savings_rate': round(savings_rate, 1),
        'expense_ratio': round(expense_ratio, 1)
    }
