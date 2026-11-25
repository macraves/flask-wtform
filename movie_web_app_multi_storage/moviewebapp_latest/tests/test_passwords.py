"""OC006 bug 3: no plaintext passwords in JSON storage or its registry."""
import json
import os

from datamanagement.json_data_manager import JsonStorage
from user.user_instance import User
from tests.conftest import csrf_from, signup_and_signin


def _read_json_users():
    """Return the users dict from the temporary JSON storage file.

    Returns:
        dict: Mapping of user id to stored record.
    """
    path = JsonStorage("movies")._filename
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["users"]


def test_json_signup_does_not_store_plaintext_anywhere(client):
    """Neither movies.json nor registry.json may contain the plaintext password."""
    signup_and_signin(client, "json", password="s3cretPW")
    with open(JsonStorage("movies")._filename, encoding="utf-8") as handle:
        assert "s3cretPW" not in handle.read()
    with open(User.registry_file, encoding="utf-8") as handle:
        registry = handle.read()
    assert "s3cretPW" not in registry
    assert "scrypt:" in registry or "pbkdf2:" in registry


def test_json_signin_still_works_after_hashing(client):
    """A hashed JSON user can sign in and reach their movie list."""
    signup_and_signin(client, "json", password="s3cretPW")
    assert client.get("/movies").status_code == 200


def _write_legacy_user(password):
    """Create a JSON user whose password is stored in plaintext (legacy data).

    Args:
        password (str): Plaintext password to store.

    Returns:
        None
    """
    storage = JsonStorage("movies")
    with open(storage._filename, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "version": 1.0,
                "users": {
                    "1": {
                        "id": 1,
                        "name": "Old User",
                        "username": "olduser",
                        "email": "o@example.com",
                        "password": password,
                        "movies": [],
                    }
                },
            },
            handle,
        )


def _signin(client, password):
    """Submit the sign-in form for the legacy JSON user.

    Args:
        client (FlaskClient): Client to use.
        password (str): Password to try.

    Returns:
        Response: The sign-in response.
    """
    token = csrf_from(client, "/signin")
    return client.post(
        "/signin",
        data={
            "username": "olduser",
            "password": password,
            "storage": "json",
            "csrf_token": token,
        },
    )


def test_legacy_plaintext_user_can_sign_in_and_is_rehashed(client):
    """Legacy plaintext entry: sign-in works once, then the entry is hashed."""
    _write_legacy_user("legacypw")
    resp = _signin(client, "legacypw")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/movies")
    stored = _read_json_users()["1"]["password"]
    assert stored != "legacypw"
    assert stored.startswith(("scrypt:", "pbkdf2:"))
    # second sign-in verifies against the new hash
    client.post("/signout", data={"csrf_token": csrf_from(client, "/dashboard")})
    assert _signin(client, "legacypw").status_code == 302


def test_legacy_plaintext_wrong_password_rejected_and_not_rehashed(client):
    """A wrong password against a legacy entry fails and leaves it untouched."""
    _write_legacy_user("legacypw")
    resp = _signin(client, "nope")
    assert resp.status_code == 200
    assert _read_json_users()["1"]["password"] == "legacypw"


def test_check_password_handles_plaintext_without_exception():
    """check_password returns a bool for legacy data instead of raising."""
    _write_legacy_user("legacypw")
    storage = JsonStorage("movies")
    assert storage.check_password(1, "legacypw") is True
    assert storage.check_password(1, "wrong") is False
    assert os.path.exists(storage._filename)
