import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config_by_name

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Application factory for Personal Finance Advisor Bot."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    
    # Load configuration
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)

    # Ensure the instance folder exists for SQLite storage
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access your financial dashboard.'
    login_manager.login_message_category = 'info'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.finance import finance_bp
    from app.routes.budget import budget_bp
    from app.routes.savings import savings_bp
    from app.routes.advisor import advisor_bp
    from app.routes.health import health_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(finance_bp, url_prefix='/finance')
    app.register_blueprint(budget_bp, url_prefix='/budgets')
    app.register_blueprint(savings_bp, url_prefix='/savings')
    app.register_blueprint(advisor_bp, url_prefix='/advisor')
    app.register_blueprint(health_bp, url_prefix='/health')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Template filters and utilities
    @app.template_filter('currency')
    def format_currency(value):
        try:
            val = float(value or 0)
            return f"${val:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.context_processor
    def inject_global_data():
        return {
            'app_name': app.config.get('APP_NAME', 'Personal Finance Advisor Bot'),
            'has_gemini_key': bool(app.config.get('GEMINI_API_KEY'))
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    # Create tables automatically on startup if they do not exist
    with app.app_context():
        db.create_all()

    return app
