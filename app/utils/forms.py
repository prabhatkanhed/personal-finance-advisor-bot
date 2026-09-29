from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    """User account registration form."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message="Password must be at least 6 characters.")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('An account with this email address already exists.')


class LoginForm(FlaskForm):
    """User account authentication form."""
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Keep me signed in')
    submit = SubmitField('Sign In')


class ProfileForm(FlaskForm):
    """User profile update form."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    current_password = PasswordField('Current Password (only needed to change password)', validators=[Optional()])
    new_password = PasswordField('New Password (leave blank to keep unchanged)', validators=[Optional(), Length(min=6)])
    submit = SubmitField('Update Profile')


class IncomeForm(FlaskForm):
    """Income entry form."""
    source = StringField('Income Source', validators=[DataRequired(), Length(max=100)], default='Primary Salary')
    amount = DecimalField('Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message="Amount must be positive.")], places=2)
    date = DateField('Date Received', validators=[DataRequired()], default=date.today)
    description = StringField('Description / Notes', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save Income')


class ExpenseForm(FlaskForm):
    """Expense entry form."""
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    amount = DecimalField('Amount ($)', validators=[DataRequired(), NumberRange(min=0.01, message="Amount must be positive.")], places=2)
    date = DateField('Date of Expense', validators=[DataRequired()], default=date.today)
    description = StringField('Description / Vendor', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save Expense')


class CategoryForm(FlaskForm):
    """Expense Category management form."""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=100)])
    color = StringField('Color Accent', validators=[DataRequired(), Length(max=20)], default='#6366f1')
    icon = StringField('Icon Identifier', validators=[Optional(), Length(max=50)], default='bi-tag')
    submit = SubmitField('Save Category')


class BudgetForm(FlaskForm):
    """Monthly budget setting form."""
    category = SelectField('Budget Category', validators=[DataRequired()])
    amount = DecimalField('Monthly Budget Cap ($)', validators=[DataRequired(), NumberRange(min=1.0, message="Budget must be at least $1.00.")], places=2)
    month = SelectField('Month', coerce=int, validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=2020, max=2099)])
    submit = SubmitField('Save Budget')


class SavingGoalForm(FlaskForm):
    """Saving Goal tracking form."""
    goal_name = StringField('Goal Title', validators=[DataRequired(), Length(min=2, max=150)])
    target_amount = DecimalField('Target Goal Amount ($)', validators=[DataRequired(), NumberRange(min=1.0)], places=2)
    current_amount = DecimalField('Current Saved Amount ($)', validators=[Optional(), NumberRange(min=0.0)], default=0.0, places=2)
    target_date = DateField('Target Completion Date', validators=[DataRequired()])
    submit = SubmitField('Save Goal')


class AddFundsForm(FlaskForm):
    """Quick deposit / addition to a saving goal."""
    amount = DecimalField('Deposit Amount ($)', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    submit = SubmitField('Deposit to Goal')


class AIBudgetGenerationForm(FlaskForm):
    """Input form for generating an AI-optimized budget."""
    monthly_income = DecimalField('Monthly Take-Home Income ($)', validators=[DataRequired(), NumberRange(min=100.0)], places=2)
    fixed_expenses = DecimalField('Estimated Fixed Expenses ($)', validators=[Optional(), NumberRange(min=0.0)], default=0.0, places=2)
    variable_expenses = DecimalField('Estimated Variable Expenses ($)', validators=[Optional(), NumberRange(min=0.0)], default=0.0, places=2)
    savings_goal = DecimalField('Target Monthly Savings ($)', validators=[Optional(), NumberRange(min=0.0)], default=0.0, places=2)
    financial_goals = TextAreaField('Your Financial & Lifestyle Goals', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Generate My Budget with AI')
