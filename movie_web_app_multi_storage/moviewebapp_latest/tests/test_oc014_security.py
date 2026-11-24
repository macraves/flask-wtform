"""OC014 regression tests for frontend and API security behavior."""
import re

import pytest

from tests.conftest import add_movie, csrf_from, signup_and_signin
from datamanagement.json_data_manager import JsonStorage


def test_movie_info_is_limited_to_owning_user(client):
    """Only the signed-in owner can view a movie's information page."""
    signup_and_signin(client, "sqlite", username="alice")
    add_movie(client)
    owner_response = client.get("/user/1/movie/1/info")
    assert owner_response.status_code == 200

    other_client = client.application.test_client()
    signup_and_signin(other_client, "sqlite", username="mallory")
    other_response = other_client.get("/user/1/movie/1/info")
    assert other_response.status_code == 403

    anonymous_response = client.application.test_client().get(
        "/user/1/movie/1/info"
    )
    assert anonymous_response.status_code == 403
    assert client.get("/user/1/movie/99/info").status_code == 404


def test_signup_while_logged_in_cannot_switch_storage_identity(client):
    """Signup cannot change the storage identity of an authenticated session."""
    signup_and_signin(client, "json", username="victim")
    add_movie(client)
    client.post("/signout", data={"csrf_token": csrf_from(client, "/dashboard")})
    signup_and_signin(client, "sqlite", username="attacker")
    token = csrf_from(client, "/signup")

    response = client.post(
        "/signup",
        data={
            "name": "New Account",
            "username": "new-json-user",
            "email": "new-json-user@example.com",
            "storage": "json",
            "password": "pw123",
            "confirm_password": "pw123",
            "csrf_token": token,
        },
    )

    assert response.status_code == 302
    assert client.get("/dashboard").status_code == 302
    assert client.get("/user/1/movie/1/info").status_code == 403
    delete_token = csrf_from(client, "/signup")
    client.post(
        "/users/1/delete_movie/1", data={"csrf_token": delete_token}
    )
    assert JsonStorage("movies").get_target_movie(1, 1) is not None


def test_get_signup_keeps_authenticated_session(client):
    """A GET to signup renders its form without ending the signed-in session."""
    signup_and_signin(client, "sqlite", username="victim")

    signup_response = client.get("/signup")

    assert signup_response.status_code == 200
    assert client.get("/dashboard").status_code == 200


def test_failed_signin_does_not_switch_authenticated_storage(client):
    """A failed signin cannot change storage for an existing login."""
    signup_and_signin(client, "json", username="victim")
    add_movie(client)
    token = csrf_from(client, "/signin")

    response = client.post(
        "/signin",
        data={
            "username": "missing-user",
            "password": "wrong",
            "storage": "sqlite",
            "csrf_token": token,
        },
    )

    assert response.status_code == 200
    assert client.get("/user/1/movie/1/info").status_code == 200


def test_signout_is_post_only_and_has_csrf_protected_ui(client):
    """Signout rejects GET and the authenticated UI submits a CSRF form."""
    signup_and_signin(client, "sqlite")
    assert client.get("/signout").status_code == 405
    html = client.get("/dashboard").get_data(as_text=True)
    assert re.search(
        r'<form[^>]*method="POST"[^>]*action="/signout"[^>]*>\s*'
        r'<input[^>]*name="csrf_token"',
        html,
    )
    token = csrf_from(client, "/dashboard")
    missing_token_response = client.post("/signout")
    assert missing_token_response.status_code == 400
    assert client.get("/dashboard").status_code == 200
    assert client.post("/signout", data={"csrf_token": token}).status_code == 302
    assert client.get("/dashboard").status_code == 302


def test_users_route_does_not_expose_names_to_anonymous_callers(client):
    """An anonymous request cannot read the users listing or its names."""
    signup_and_signin(client, "sqlite", username="distinctive-user")
    token = csrf_from(client, "/dashboard")
    client.post("/signout", data={"csrf_token": token})
    response = client.get("/users")
    assert response.status_code == 302
    assert "/signin" in response.headers["Location"]


def test_users_route_shows_only_the_signed_in_user(client):
    """An ordinary user sees only their own name and account links."""
    signup_and_signin(client, "sqlite", username="alice")
    other_client = client.application.test_client()
    signup_and_signin(other_client, "sqlite", username="bob")

    from datamanagement.sqlite_data_manager import SqliteStorage, db

    storage = SqliteStorage("movies")
    with client.application.app_context():
        alice = storage.find_user(username="alice")
        bob = storage.find_user(username="bob")
        assert alice is not None
        assert bob is not None
        alice_id = alice.id
        bob_id = bob.id
        bob.name = "Bob Doe"
        db.session.commit()

    response = client.get("/users")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Alice Doe" in html
    assert f"/user-update/{alice_id}" in html
    assert f"/user-delete/{alice_id}" in html
    assert "Bob Doe" not in html
    assert f"/user-update/{bob_id}" not in html
    assert f"/user-delete/{bob_id}" not in html


def test_api_session_cookie_and_cross_origin_policy_are_restricted(api_client):
    """Login cookies are restricted and API responses omit CORS headers."""
    api_client.post(
        "/api/user/add",
        json={"name": "Alice Doe", "username": "alice", "email": "alice@example.com", "password": "pw123"},
    )
    response = api_client.post(
        "/api/login",
        json={"username": "alice", "password": "pw123", "storage": "sqlite"},
        headers={"Origin": "https://untrusted.example"},
    )
    assert response.status_code == 200
    cookie = response.headers["Set-Cookie"]
    assert "SameSite=Lax" in cookie
    assert "HttpOnly" in cookie
    assert not any(
        name.startswith("Access-Control-Allow-") for name, _ in response.headers
    )

    preflight = api_client.options(
        "/api/login",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert not any(
        name.startswith("Access-Control-Allow-") for name, _ in preflight.headers
    )


@pytest.mark.parametrize(
    ("body", "content_type"),
    [
        ("username=alice", "text/plain"),
        ("username=alice", "application/x-www-form-urlencoded"),
        ("{invalid", "application/json"),
        ("[]", "application/json"),
        ('"str"', "application/json"),
        ("", "application/json"),
        ('{"username": 123, "password": "pw", "storage": "sqlite"}', "application/json"),
        ('{"username": "alice", "password": "pw", "storage": 123}', "application/json"),
        ('{"username": "alice", "storage": "sqlite"}', "application/json"),
        ('{"username": "alice", "password": 123, "storage": "sqlite"}', "application/json"),
        ('{"username": "alice", "password": null, "storage": "sqlite"}', "application/json"),
        ('{"username": "alice", "password": [], "storage": "sqlite"}', "application/json"),
    ],
)
def test_api_login_invalid_body_returns_json_client_error(api_client, body, content_type):
    """Malformed or mistyped login input receives a JSON 4xx response."""
    api_client.post(
        "/api/user/add",
        json={"name": "Alice Doe", "username": "alice", "email": "alice@example.com", "password": "pw123"},
    )
    response = api_client.post(
        "/api/login", data=body, content_type=content_type
    )
    assert 400 <= response.status_code < 500
    assert response.is_json
    assert "error" in response.get_json()


def test_api_login_valid_credentials_succeed(api_client):
    """Valid credentials remain able to log in successfully."""
    api_client.post(
        "/api/user/add",
        json={"name": "Alice Doe", "username": "alice", "email": "alice@example.com", "password": "pw123"},
    )
    response = api_client.post(
        "/api/login",
        json={"username": "alice", "password": "pw123", "storage": "sqlite"},
    )
    assert response.status_code == 200
