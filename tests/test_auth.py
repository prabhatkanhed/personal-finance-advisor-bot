def test_register_success(client):
    response = client.post(
        '/auth/register',
        data={
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'StrongPassword1',
            'confirm_password': 'StrongPassword1'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Welcome to Personal Finance Advisor Bot' in response.data or b'Financial Overview' in response.data


def test_register_duplicate_email(client, sample_user):
    response = client.post(
        '/auth/register',
        data={
            'name': 'Alice Clone',
            'email': 'alice@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        },
        follow_redirects=True
    )
    assert b'already exists' in response.data


def test_login_success(client, sample_user, auth):
    response = auth.login('alice@example.com', 'Password123!')
    assert response.status_code == 200
    assert b'Welcome back, Alice Tester' in response.data or b'Financial Overview' in response.data


def test_login_invalid_password(client, sample_user, auth):
    response = auth.login('alice@example.com', 'WrongPassword!')
    assert b'Invalid email or password' in response.data


def test_logout(client, sample_user, auth):
    auth.login('alice@example.com', 'Password123!')
    response = auth.logout()
    assert b'You have been safely signed out' in response.data or b'Sign In' in response.data


def test_protected_routes(client):
    protected_urls = [
        '/dashboard',
        '/finance/income',
        '/finance/expenses',
        '/finance/categories',
        '/budgets/',
        '/savings/',
        '/advisor/',
        '/health/'
    ]
    for url in protected_urls:
        response = client.get(url)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']
