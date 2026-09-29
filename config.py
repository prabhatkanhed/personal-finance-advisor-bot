import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / '.env')


class Config:
    """Base configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pfab-dev-secret-key-2026-production-ready')
    
    # Database URL with fallback to local SQLite database
    raw_db = os.environ.get('DATABASE_URL', '')
    if not raw_db:
        instance_dir = BASE_DIR / 'instance'
        instance_dir.mkdir(exist_ok=True)
        db_path = (instance_dir / 'personal_finance.db').resolve().as_posix()
        db_url = f"sqlite:///{db_path}"
    else:
        db_url = raw_db
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        elif db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:///:memory:"):
            # Normalize SQLite relative paths on Windows to absolute forward slashes
            rel_path = db_url[len("sqlite:///"):]
            if not os.path.isabs(rel_path):
                abs_p = (BASE_DIR / rel_path).resolve().as_posix()
                db_url = f"sqlite:///{abs_p}"

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Gemini API Key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()

    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600 * 24 * 14  # 14 days
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Valid for session lifetime

    # Application details
    APP_NAME = "Personal Finance Advisor Bot"
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration with in-memory database."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_SESSION_OPTIONS = {'expire_on_commit': False}
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
