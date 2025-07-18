import pytest
from flask import g, session
from flask_lab.db import get_db


@pytest.mark.skip(reason="No registration form")
def test_register_with_email(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'test', 'password': 'test'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

@pytest.mark.skip(reason="No registration form")
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input_no_email(client, username, password, message):
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
def test_register_validate_input_with_email(client, username, view_name, email, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'view_name': view_name,
              'email': email, 'password': password}
    )
    assert message in response.data


def test_block_ip_ranges(client, app):
    with app.app_context():
        good_ips = ['192.168.1.100', '2a02:e34:ec80:b790:bf99:b86b:617:7b66']
        for ip in good_ips:
            response = client.get('/auth/login', environ_base={'REMOTE_ADDR': ip})
            assert response.status_code == 200
        # Simulate a blocked IP address
        blocked_ips = ['141.95.0.0', '2a01:e34:ec80:b790:bf99:b86b:617:7b66']
        for ip in blocked_ips:
            response = client.get('/auth/login', environ_base={'REMOTE_ADDR': ip})
            assert response.status_code == 500


def test_block_php_and_wp_urls(client, app):
    with app.app_context():
        response = client.get(f'/auth/test.php', environ_base={'REMOTE_ADDR': '192.168.3.101'})
        assert response.status_code == 500
        wp_phrases = ['wp-admin', 'wp-login', 'wp-json', 'wp-content', 'wp-content']
        for wp_phrase in wp_phrases:
            response = client.get(f'/auth/{wp_phrase}', environ_base={'REMOTE_ADDR': '192.168.2.101'})
            assert response.status_code == 500
