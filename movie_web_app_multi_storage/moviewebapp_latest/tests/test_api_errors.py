"""OC006 bug 5: API PUT and DELETE must answer with proper JSON, not 500."""
from datamanagement.sqlite_models import User
from tests.conftest import backend_api


def _make_user(api_client, username="bob", password="pw123"):
    """Create an SQLite user through the API and log in.

    Args:
        api_client (FlaskClient): API test client.
        username (str): Username to create.
        password (str): Password to create.

    Returns:
        int: The new user's id.
    """
    resp = api_client.post(
        "/api/user/add",
        json={
            "name": "Bob Doe",
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )
    assert resp.status_code == 200, resp.get_data(as_text=True)
    resp = api_client.post(
        "/api/login",
        json={"username": username, "password": password, "storage": "sqlite"},
    )
    assert resp.status_code == 200
    with backend_api.app.app_context():
        return User.query.filter_by(username=username).first().id


def test_put_updates_user_with_correct_password(api_client):
    """PUT with the current password and new fields returns 200 and persists."""
    uid = _make_user(api_client)
    resp = api_client.put(
        f"/api/user-update/{uid}", json={"name": "Robert", "password": "pw123"}
    )
    assert resp.status_code == 200, resp.get_data(as_text=True)
    with backend_api.app.app_context():
        assert User.query.get(uid).name == "Robert"


def test_put_wrong_password_is_403_json(api_client):
    """PUT with a wrong password is refused with JSON 403 and changes nothing."""
    uid = _make_user(api_client)
    resp = api_client.put(
        f"/api/user-update/{uid}", json={"name": "Hacker", "password": "bad"}
    )
    assert resp.status_code == 403
    assert "error" in resp.get_json()
    with backend_api.app.app_context():
        assert User.query.get(uid).name == "Bob Doe"


def test_put_missing_password_is_400_json(api_client):
    """PUT without a password is a 400 JSON error."""
    uid = _make_user(api_client)
    resp = api_client.put(f"/api/user-update/{uid}", json={"name": "Robert"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_put_empty_body_is_400_json(api_client):
    """PUT with {} is a 400 JSON error (used to be 500)."""
    uid = _make_user(api_client)
    resp = api_client.put(f"/api/user-update/{uid}", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_put_non_string_field_is_400_json(api_client):
    """PUT with a non-string field value is a 400 JSON error."""
    uid = _make_user(api_client)
    resp = api_client.put(
        f"/api/user-update/{uid}", json={"name": 5, "password": "pw123"}
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_put_duplicate_username_is_409_json(api_client):
    """PUT renaming to an existing username is a 409 JSON error."""
    uid = _make_user(api_client, "bob")
    other = backend_api.app.test_client()
    _make_user(other, "carol")
    resp = api_client.put(
        f"/api/user-update/{uid}", json={"username": "carol", "password": "pw123"}
    )
    assert resp.status_code == 409
    assert "error" in resp.get_json()


def test_delete_with_correct_password_removes_user(api_client):
    """DELETE with the right password returns 200 and removes the account."""
    uid = _make_user(api_client)
    resp = api_client.delete(f"/api/user-delete/{uid}", json={"password": "pw123"})
    assert resp.status_code == 200, resp.get_data(as_text=True)
    with backend_api.app.app_context():
        assert User.query.get(uid) is None


def test_delete_wrong_password_is_403_json(api_client):
    """DELETE with a wrong password is JSON 403 and keeps the user."""
    uid = _make_user(api_client)
    resp = api_client.delete(f"/api/user-delete/{uid}", json={"password": "bad"})
    assert resp.status_code == 403
    assert "error" in resp.get_json()
    with backend_api.app.app_context():
        assert User.query.get(uid) is not None


def test_delete_missing_body_is_400_json(api_client):
    """DELETE without a JSON body or password is a 400 JSON error."""
    uid = _make_user(api_client)
    resp = api_client.delete(f"/api/user-delete/{uid}")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_other_users_id_is_403(api_client):
    """Touching another user's id stays 403 for both verbs."""
    uid = _make_user(api_client)
    assert api_client.put(
        f"/api/user-update/{uid + 99}", json={"password": "x"}
    ).status_code == 403
    assert api_client.delete(
        f"/api/user-delete/{uid + 99}", json={"password": "x"}
    ).status_code == 403
