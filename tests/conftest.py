import pytest
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    """Create and configure a testing Flask app instance."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def app_context(app):
    """Ensure all tests run with an active application context."""
    with app.app_context():
        yield


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create and return a sample registered user."""
    user = User(name='Alice Tester', email='alice@example.com')
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    # Refresh to ensure id is loaded and not expired
    db.session.refresh(user)
    return user


@pytest.fixture
def sample_user_2(app):
    """Create and return a secondary user for isolation tests."""
    user = User(name='Bob Isolation', email='bob@example.com')
    user.set_password('Password123!')
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email='alice@example.com', password='Password123!'):
        return self._client.post(
            '/auth/login',
            data={'email': email, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)
