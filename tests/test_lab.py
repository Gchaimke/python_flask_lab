import pytest
from flask_lab.db import get_db
from flask import g, session


@pytest.mark.parametrize('path', (
    '/lab/create',
    '/lab/update/1',
    '/lab/delete/1',
))
def test_login_required(client, path):
    if 'delete' in path:
        response = client.post(path)
    else:
        response = client.get(path)
    assert response.headers["Location"] == "/"


@pytest.mark.parametrize('path', (
    '/lab/update/2',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).headers["Location"] == "/lab/"
    assert '2' not in client.post(path).headers["Location"]
