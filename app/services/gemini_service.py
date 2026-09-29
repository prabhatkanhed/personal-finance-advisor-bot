"""
Gemini AI Financial Advisor Service.
Handles prompt construction, API communication with Google Gemini,
and robust fallback heuristics for budget generation and spending analysis.
"""

import os
import json
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "Disclaimer: All AI-generated insights, budget plans, and recommendations are provided "
    "for informational and educational purposes only. They do not constitute certified professional financial, "
    "legal, or investment advice. Always evaluate recommendations against your personal situation or consult "
    "a qualified financial planner."
)


def get_api_key():
    """Retrieve Gemini API key from environment or app config."""
    key = os.environ.get('GEMINI_API_KEY', '')
    if not key and current_app:
        key = current_app.config.get('GEMINI_API_KEY', '')
    return key.strip() if key else ''


def call_gemini_api(prompt, system_instruction=None, response_schema_json=False):
    """
    Calls the Google Gemini API with fallback across model endpoints.
    Returns (response_text, is_live_api).
    """
    api_key = get_api_key()
    if not api_key or api_key == 'your_gemini_api_key_here':
        logger.info("Gemini API key not configured. Using high-fidelity heuristic generator.")
        return None, False

    # Models to try in order of preference
    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        if response_schema_json:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts and 'text' in parts[0]:
                        return parts[0]['text'], True
            else:
                logger.warning(f"Gemini model {model} returned HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Failed to communicate with Gemini API ({model}): {str(e)}")

    return None, False


def analyze_user_finances(financial_data):
    """
    Generates a comprehensive AI spending analysis and financial recommendations.
    Accepts summarized financial data dictionary.
    """
    income = financial_data.get('month_income', 0.0)
    expenses = financial_data.get('month_expense', 0.0)
    savings = financial_data.get('month_savings', 0.0)
    balance = financial_data.get('current_balance', 0.0)
    top_categories = financial_data.get('top_categories', [])
    budgets_status = financial_data.get('budgets_status', [])
    goals = financial_data.get('goals', [])

    # Summarize data safely without personal identifiable details
    data_summary = {
        "monthly_income": income,
        "monthly_expenses": expenses,
        "monthly_savings": savings,
        "net_balance": balance,
        "top_spending_categories": [
            {"category": c.get('name'), "amount": c.get('amount'), "percentage": c.get('percentage')}
            for c in top_categories
        ],
        "budget_performance": [
            {
                "category": b.get('category'),
                "budget": b.get('budget_amount'),
                "spent": b.get('spent_amount'),
                "over_budget": b.get('is_over_budget')
            }
            for b in budgets_status
        ],
        "active_saving_goals": [
            {
                "goal": g.goal_name if hasattr(g, 'goal_name') else g.get('goal_name'),
                "target": g.target_amount if hasattr(g, 'target_amount') else g.get('target_amount'),
                "saved": g.current_amount if hasattr(g, 'current_amount') else g.get('current_amount')
            }
            for g in goals
        ]
    }

    prompt = f"""
You are an expert AI Personal Finance Advisor. Analyze this anonymized monthly financial summary:
{json.dumps(data_summary, indent=2)}

Please provide a detailed, well-structured financial evaluation in clean JSON format matching this schema:
{{
  "spending_analysis": "Detailed analysis of user spending habits, patterns, and expense-to-income ratio.",
  "overspending_detection": ["Key overspending issues or budget leakages detected, or 'No overspending detected'."],
  "budget_recommendations": ["Actionable recommendations for category budget adjustments."],
  "savings_recommendations": ["Specific actionable strategies to accelerate savings and hit active goals."],
  "cost_optimization_suggestions": ["Concrete practical ways to trim fixed or variable costs."],
  "emergency_fund_guidance": "Assessment of safety buffer and guidance on emergency fund sizing (3-6 months).",
  "personalized_insights": "A motivating executive summary and priority action plan for this month."
}}
"""

    system_instruction = (
        "You are an encouraging, pragmatic, and highly analytical personal finance coach. "
        "Provide realistic numbers and actionable advice. Respond strictly in valid JSON format."
    )

    ai_text, is_live = call_gemini_api(prompt, system_instruction=system_instruction, response_schema_json=True)

    if ai_text:
        try:
            # Strip markdown if present
            clean_text = ai_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            parsed = json.loads(clean_text)
            parsed['is_live_ai'] = True
            parsed['disclaimer'] = DISCLAIMER_TEXT
            return parsed
        except Exception as err:
            logger.warning(f"Error parsing Gemini response: {err}")

    # High-quality deterministic fallback engine
    return _generate_heuristic_financial_analysis(data_summary)


def generate_ai_budget(monthly_income, fixed_expenses, variable_expenses, savings_goal, financial_goals_text=""):
    """
    Generates a structured, balanced budget using the 50/30/20 framework customized
    to the user's input.
    """
    user_inputs = {
        "monthly_income": float(monthly_income or 0),
        "fixed_expenses": float(fixed_expenses or 0),
        "variable_expenses": float(variable_expenses or 0),
        "target_savings": float(savings_goal or 0),
        "user_goals": financial_goals_text.strip()
    }

    prompt = f"""
You are a master personal finance planner. Create an optimized monthly budget plan based on these user numbers:
- Monthly Income: ${user_inputs['monthly_income']}
- Fixed Expenses (Rent, Utilities, Insurance, Loans): ${user_inputs['fixed_expenses']}
- Variable Expenses (Groceries, Dining, Entertainment): ${user_inputs['variable_expenses']}
- Target Monthly Savings: ${user_inputs['target_savings']}
- User Goals: "{user_inputs['user_goals']}"

Return a strict JSON object with this exact structure:
{{
  "summary": "Brief explanation of this budget design and strategy.",
  "framework": "e.g. Optimized 50/30/20 Framework",
  "needs": {{
    "total": 0.00,
    "percentage": 0.0,
    "categories": [
      {{"name": "Housing & Rent", "amount": 0.00}},
      {{"name": "Utilities & Bills", "amount": 0.00}},
      {{"name": "Groceries", "amount": 0.00}},
      {{"name": "Transportation & Fuel", "amount": 0.00}},
      {{"name": "Healthcare & Insurance", "amount": 0.00}}
    ]
  }},
  "wants": {{
    "total": 0.00,
    "percentage": 0.0,
    "categories": [
      {{"name": "Dining Out & Takeaway", "amount": 0.00}},
      {{"name": "Entertainment & Hobbies", "amount": 0.00}},
      {{"name": "Shopping & Personal Care", "amount": 0.00}}
    ]
  }},
  "savings": {{
    "total": 0.00,
    "percentage": 0.0,
    "allocations": [
      {{"name": "General Savings / Investments", "amount": 0.00}},
      {{"name": "Emergency Fund", "amount": 0.00}}
    ]
  }},
  "emergency_fund_target": 0.00,
  "monthly_emergency_allocation": 0.00,
  "actionable_tips": [
    "Tip 1", "Tip 2", "Tip 3"
  ]
}}
Ensure the sum of needs total, wants total, and savings total matches monthly income within reasonable rounding.
"""

    system_instruction = "You are a budgeting expert. Output strictly valid JSON."

    ai_text, is_live = call_gemini_api(prompt, system_instruction=system_instruction, response_schema_json=True)

    if ai_text:
        try:
            clean_text = ai_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            parsed = json.loads(clean_text)
            parsed['is_live_ai'] = True
            parsed['disclaimer'] = DISCLAIMER_TEXT
            return parsed
        except Exception as err:
            logger.warning(f"Error parsing Gemini budget response: {err}")

    # Heuristic fallback generator
    return _generate_heuristic_budget(user_inputs)


def _generate_heuristic_financial_analysis(summary):
    """
    Intelligent heuristic fallback when live Gemini API is unreachable or key is unset.
    """
    income = summary['monthly_income']
    expenses = summary['monthly_expenses']
    savings = summary['monthly_savings']
    top_cats = summary['top_spending_categories']
    budgets = summary['budget_performance']

    overspending = []
    for b in budgets:
        if b.get('over_budget'):
            diff = b.get('spent', 0) - b.get('budget', 0)
            overspending.append(f"Category '{b.get('category')}' exceeded limit by ${diff:,.2f}.")

    if not overspending:
        if expenses > income and income > 0:
            overspending.append(f"Total spending (${expenses:,.2f}) exceeded income (${income:,.2f}) by ${expenses - income:,.2f}.")
        else:
            overspending.append("No overspending detected across active budgets. Well done!")

    # Spending analysis
    ratio = (expenses / income * 100) if income > 0 else 0
    if ratio < 60:
        spending_analysis = f"Your current spending is lean at {ratio:.1f}% of income, leaving healthy margins for savings and wealth creation."
    elif ratio <= 80:
        spending_analysis = f"Your spending accounts for {ratio:.1f}% of your monthly income. This is within standard living guidelines."
    else:
        spending_analysis = f"Your spending is elevated at {ratio:.1f}% of monthly income. Fixed and variable obligations leave little margin."

    # Budget recommendations
    budget_recs = [
        "Cap discretionary entertainment and dining out at 15% of your take-home pay.",
        "Set explicit monthly spending caps for your top 3 expense categories.",
        "Review recurring subscriptions quarterly and eliminate unused digital services."
    ]

    # Savings recommendations
    savings_rate = (savings / income * 100) if income > 0 else 0
    savings_recs = [
        f"Automate a transfer of at least 15-20% (${income * 0.20:,.2f}) on pay day directly into a high-yield account.",
        "Channel 50% of any unexpected windfalls, tax refunds, or bonuses directly towards your top goal."
    ]
    if savings_rate < 15:
        savings_recs.append("Increase your monthly savings contribution by 2-3% every two months.")

    # Cost optimization
    cost_opts = [
        "Meal prep lunches 3 days a week to trim monthly dining out costs by an estimated $150 - $250.",
        "Audit monthly utility bills and negotiate telecom/internet packages for promotional rates.",
        "Check insurance policies annually to compare competitive rates and bundling discounts."
    ]

    # Emergency fund
    monthly_burn = expenses if expenses > 0 else 2500
    emergency_target = monthly_burn * 3
    emergency_guidance = (
        f"Aim for an emergency cushion of 3 to 6 months of living expenses (approx. ${emergency_target:,.2f} to ${emergency_target * 2:,.2f}). "
        "Keep this in a dedicated, liquid high-yield savings account separate from your checking account."
    )

    insights = (
        f"Based on your current cash flow (${income:,.2f} income vs ${expenses:,.2f} expenses), your net monthly surplus is ${savings:,.2f}. "
        "Focus on sticking strictly to category boundaries and compounding your savings goals."
    )

    return {
        "spending_analysis": spending_analysis,
        "overspending_detection": overspending,
        "budget_recommendations": budget_recs,
        "savings_recommendations": savings_recs,
        "cost_optimization_suggestions": cost_opts,
        "emergency_fund_guidance": emergency_guidance,
        "personalized_insights": insights,
        "is_live_ai": False,
        "disclaimer": DISCLAIMER_TEXT
    }


def _generate_heuristic_budget(inputs):
    """
    Heuristic 50/30/20 budget generator.
    """
    income = inputs['monthly_income']
    if income <= 0:
        income = 4000.0  # sensible default calculation baseline

    # 50% Needs, 30% Wants, 20% Savings
    needs_total = round(income * 0.50, 2)
    wants_total = round(income * 0.30, 2)
    savings_total = round(income * 0.20, 2)

    needs_cats = [
        {"name": "Housing & Rent", "amount": round(needs_total * 0.55, 2)},
        {"name": "Groceries", "amount": round(needs_total * 0.22, 2)},
        {"name": "Utilities & Internet", "amount": round(needs_total * 0.13, 2)},
        {"name": "Transportation & Fuel", "amount": round(needs_total * 0.10, 2)}
    ]

    wants_cats = [
        {"name": "Dining & Takeout", "amount": round(wants_total * 0.45, 2)},
        {"name": "Entertainment & Subscriptions", "amount": round(wants_total * 0.30, 2)},
        {"name": "Shopping & Lifestyle", "amount": round(wants_total * 0.25, 2)}
    ]

    emergency_monthly = round(savings_total * 0.40, 2)
    general_savings = round(savings_total * 0.60, 2)
    emergency_target = round(needs_total * 3, 2)

    return {
        "summary": f"Structured 50/30/20 balanced budget plan modeled on ${income:,.2f} monthly net income.",
        "framework": "Balanced 50/30/20 Framework",
        "needs": {
            "total": needs_total,
            "percentage": 50.0,
            "categories": needs_cats
        },
        "wants": {
            "total": wants_total,
            "percentage": 30.0,
            "categories": wants_cats
        },
        "savings": {
            "total": savings_total,
            "percentage": 20.0,
            "allocations": [
                {"name": "General Savings & Goals", "amount": general_savings},
                {"name": "Emergency Fund Contribution", "amount": emergency_monthly}
            ]
        },
        "emergency_fund_target": emergency_target,
        "monthly_emergency_allocation": emergency_monthly,
        "actionable_tips": [
            "Transfer your savings allocation automatically on payday before spending on wants.",
            "Keep variable wants under your weekly limit by checking balances every Sunday.",
            "Allocate any work bonuses or tax returns directly to reach your 3-month emergency buffer faster."
        ],
        "is_live_ai": False,
        "disclaimer": DISCLAIMER_TEXT
    }
