from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.models import User
from app.utils.forms import RegistrationForm, LoginForm, ProfileForm
from app.services.demo_service import seed_demo_data

auth_bp = Blueprint('auth', __name__)


def is_safe_url(target):
    """Ensure redirects stay on the local application host."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Welcome to Personal Finance Advisor Bot! Your financial planning journey begins now.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password. Please verify your credentials.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been safely signed out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Check if email is already used by another user
        existing_email = User.query.filter(User.email == form.email.data.strip().lower(), User.id != current_user.id).first()
        if existing_email:
            flash('That email address is already in use by another account.', 'danger')
            return render_template('profile.html', form=form)

        current_user.name = form.name.data.strip()
        current_user.email = form.email.data.strip().lower()

        # Handle password change if requested
        if form.new_password.data:
            if not form.current_password.data or not current_user.check_password(form.current_password.data):
                flash('Current password is required and must match to set a new password.', 'danger')
                return render_template('profile.html', form=form)
            current_user.set_password(form.new_password.data)
            flash('Your profile and password have been updated successfully.', 'success')
        else:
            flash('Your profile details have been saved.', 'success')

        db.session.commit()
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', form=form)


@auth_bp.route('/load-demo', methods=['POST'])
@login_required
def load_demo():
    """Optional action to load realistic sample financial records."""
    seed_demo_data(current_user.id)
    flash('Sample financial data (income, expenses, budgets, savings goals) loaded successfully!', 'success')
    return redirect(url_for('main.dashboard'))
