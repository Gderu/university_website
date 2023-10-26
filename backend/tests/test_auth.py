import pytest
from flask import session


@pytest.mark.parametrize(('username', 'password', 'role'), (
        ('111111111', '321123', 1),
        ('222222222', 'password', 2)
))
def test_login(client, auth, username, password, role):
    assert auth.login(username, password).status_code == 200

    with client:
        client.get('/')
        assert session['user']['id'] == int(username)
        assert session['user']['role'] == role


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
