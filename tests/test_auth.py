import pytest
from flask import g, session
from flask_lab.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'test', 'password': 'test'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/lab/"

    with client:
        client.get('/')
        assert session['user_id']
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect'),
    ('test', 'a', b'Incorrect'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={
            'username': 'testuser',
            'view_name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpassword'
        }
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with app.app_context():
        user = get_db().execute(
            "SELECT * FROM user WHERE username = 'testuser'",
        ).fetchone()
        assert user is not None
        assert user['username'] == 'testuser'
        assert user['email'] == 'test@example.com'


@pytest.mark.parametrize(('username', 'view_name', 'email', 'password', 'message'), (
    ('', 'Test User', 'test@example.com', 'testpassword', b'Username is required.'),
    ('testuser', 'Test User', 'test@example.com', '', b'Password is required.'),
))
def test_register_validate_input(client, username, view_name, email, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'view_name': view_name,
              'email': email, 'password': password}
    )
    assert message in response.data
