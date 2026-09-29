from datetime import datetime, timezone, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """User account model with secure credentials and isolated finance relations."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    incomes = db.relationship('Income', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    expenses = db.relationship('Expense', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    categories = db.relationship('ExpenseCategory', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    budgets = db.relationship('Budget', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    saving_goals = db.relationship('SavingGoal', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    summaries = db.relationship('FinancialSummary', backref='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password):
        """Hash and store user password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify user password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class ExpenseCategory(db.Model):
    """User-specific expense category."""
    __tablename__ = 'expense_categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default='#6366f1')
    icon = db.Column(db.String(50), default='bi-tag')

    # Relationships
    expenses = db.relationship('Expense', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<ExpenseCategory {self.name} (User {self.user_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'icon': self.icon
        }


class Income(db.Model):
    """Income entry model."""
    __tablename__ = 'incomes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False)  # Salary, Freelance, Investments, etc.
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<Income {self.source}: ${self.amount}>'

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'amount': round(self.amount, 2),
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description or ''
        }


class Expense(db.Model):
    """Expense entry model with category link."""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id', ondelete='SET NULL'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<Expense ${self.amount} on {self.date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else 'Uncategorized',
            'category_color': self.category.color if self.category else '#94a3b8',
            'amount': round(self.amount, 2),
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description or ''
        }


class Budget(db.Model):
    """Monthly budget definition by category or overall."""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Category name or "Overall"
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1 - 12
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<Budget {self.category} {self.month}/{self.year}: ${self.amount}>'

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'amount': round(self.amount, 2),
            'month': self.month,
            'year': self.year
        }


class SavingGoal(db.Model):
    """User savings target and tracking model."""
    __tablename__ = 'saving_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_name = db.Column(db.String(150), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    @property
    def progress_percentage(self):
        if self.target_amount <= 0:
            return 0.0
        return min(100.0, round((self.current_amount / self.target_amount) * 100, 1))

    @property
    def remaining_amount(self):
        return max(0.0, round(self.target_amount - self.current_amount, 2))

    @property
    def is_completed(self):
        return self.current_amount >= self.target_amount

    def __repr__(self):
        return f'<SavingGoal {self.goal_name}: ${self.current_amount}/${self.target_amount}>'

    def to_dict(self):
        return {
            'id': self.id,
            'goal_name': self.goal_name,
            'target_amount': round(self.target_amount, 2),
            'current_amount': round(self.current_amount, 2),
            'remaining_amount': self.remaining_amount,
            'progress_percentage': self.progress_percentage,
            'target_date': self.target_date.strftime('%Y-%m-%d'),
            'is_completed': self.is_completed
        }


class FinancialSummary(db.Model):
    """Archived or monthly snapshot summary for performance and AI evaluations."""
    __tablename__ = 'financial_summaries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_income = db.Column(db.Float, default=0.0)
    total_expenses = db.Column(db.Float, default=0.0)
    net_savings = db.Column(db.Float, default=0.0)
    savings_rate = db.Column(db.Float, default=0.0)
    health_score = db.Column(db.Integer, default=0)
    ai_insights = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def __repr__(self):
        return f'<FinancialSummary {self.month}/{self.year} (User {self.user_id})>'
