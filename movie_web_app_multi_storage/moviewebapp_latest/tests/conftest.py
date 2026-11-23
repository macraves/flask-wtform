"""Shared pytest fixtures: every test runs against temporary data files only."""
import os
import re
import shutil
import sys
import tempfile

import pytest

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

# Point every storage at a throw-away folder BEFORE the apps are imported,
# because the storage paths are computed at import time.
DATA_ROOT = tempfile.mkdtemp(prefix="oc006_data_")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ["OMDB_API_KEY"] = "dummy-key-never-used"

from datamanagement.storage_inheritance import DataManagmentInterface  # noqa: E402
from user.user_instance import User  # noqa: E402

DataManagmentInterface.logs_dir = os.path.join(DATA_ROOT, "data")
User.registry_dir = os.path.join(DATA_ROOT, "registry")
User.registry_file = os.path.join(User.registry_dir, "registry.json")

from frontend import frontend_app  # noqa: E402
from backend import backend_api  # noqa: E402
from datamanagement.sqlite_data_manager import db  # noqa: E402

FAKE_MOVIE = {
    "Title": "Fake Movie",
    "Year": "2000",
    "imdbRating": 7.5,
    "Poster": "http://example.invalid/p.jpg",
}


def fake_extract_movie_data(title):
    """Stub for the OMDb lookup so no network call is made.

    Args:
        title (str): Requested movie title (ignored).

    Returns:
        dict: A copy of the canned movie record.
    """
    return dict(FAKE_MOVIE)


frontend_app.extract_movie_data = fake_extract_movie_data
backend_api.extract_movie_data = fake_extract_movie_data


def pytest_sessionfinish(session, exitstatus):
    """Remove the temporary data folder after the test session.

    Args:
        session: pytest session (unused).
        exitstatus: pytest exit status (unused).
    """
    shutil.rmtree(DATA_ROOT, ignore_errors=True)


@pytest.fixture(autouse=True)
def clean_data():
    """Reset SQLite tables, JSON/CSV files and the registry before each test.

    Yields:
        None: Control to the test.
    """
    with frontend_app.app.app_context():
        db.drop_all()
        db.create_all()
    shutil.rmtree(DataManagmentInterface.logs_dir, ignore_errors=True)
    shutil.rmtree(User.registry_dir, ignore_errors=True)
    os.makedirs(DataManagmentInterface.logs_dir, exist_ok=True)
    with frontend_app.app.app_context():
        db.create_all()
    yield


@pytest.fixture
def app():
    """Return the frontend Flask app.

    Returns:
        Flask: The frontend application.
    """
    return frontend_app.app


@pytest.fixture
def client(app):
    """Return a frontend test client.

    Args:
        app (Flask): Frontend application.

    Returns:
        FlaskClient: Test client with cookies enabled.
    """
    return app.test_client()


@pytest.fixture
def api_client():
    """Return a REST API test client.

    Returns:
        FlaskClient: Test client for backend_api.
    """
    return backend_api.app.test_client()


def csrf_from(client, url):
    """GET a page and extract its hidden CSRF token.

    Args:
        client (FlaskClient): Client to use.
        url (str): Page that renders a form with a hidden csrf_token field.

    Returns:
        str: The token value.
    """
    html = client.get(url).get_data(as_text=True)
    return re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html).group(1)


def signup_and_signin(client, storage, username="alice", password="pw123"):
    """Create a user in the given storage through the real forms and sign in.

    Args:
        client (FlaskClient): Client to use.
        storage (str): One of csv, json, sqlite.
        username (str): Username to register.
        password (str): Password to register.

    Returns:
        None
    """
    token = csrf_from(client, "/signup")
    client.post(
        "/signup",
        data={
            "name": "Alice Doe",
            "username": username,
            "email": f"{username}@example.com",
            "storage": storage,
            "password": password,
            "confirm_password": password,
            "csrf_token": token,
        },
    )
    token = csrf_from(client, "/signin")
    client.post(
        "/signin",
        data={
            "username": username,
            "password": password,
            "storage": storage,
            "csrf_token": token,
        },
    )


def add_movie(client):
    """Add the canned movie through the real /movies/add form.

    Args:
        client (FlaskClient): Signed-in client.

    Returns:
        None
    """
    token = csrf_from(client, "/movies/add")
    client.post("/movies/add", data={"title": "x", "csrf_token": token})
