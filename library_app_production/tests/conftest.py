"""Shared fixtures: an isolated app, a fresh seeded database and test clients.

The environment is prepared before ``main`` is imported, because the app reads
its configuration at import time. The database is a temporary SQLite file, so
nothing is created inside the repository and no real ``.env`` value leaks in.
"""
import os
import re
import sys
import tempfile

import pytest
from werkzeug.security import generate_password_hash

_TMP_DIR = tempfile.mkdtemp(prefix="library_app_tests_")
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{_TMP_DIR}/test.sqlite"
# Empty values stop a developer's real .env from enabling network lookups
os.environ["RAPIDAPI_KEY"] = ""

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=wrong-import-position
from main import app as flask_app  # noqa: E402
from data_models import Author, Book, Post, User, db  # noqa: E402

PASSWORD = "correct horse battery"
TOKEN_RE = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')


@pytest.fixture(name="app")
def app_fixture():
    """Provide the app with an empty, freshly seeded database and CSRF off.

    Seeds ``admin`` (id 1, admin), ``alice`` and ``bob`` plus one author, one
    book and one post owned by alice.

    Yields:
        Flask: The configured application.
    """
    flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        password_hash = generate_password_hash(PASSWORD)
        for username, is_admin in (("admin", True), ("alice", False), ("bob", False)):
            db.session.add(
                User(
                    username=username,
                    name=username.title(),
                    email=f"{username}@example.com",
                    about_user="about",
                    password_hash=password_hash,
                    is_admin=is_admin,
                )
            )
        db.session.commit()
        author = Author(name="Ursula Le Guin")
        db.session.add(author)
        db.session.commit()
        db.session.add(
            Book(
                title="Dispossessed",
                condition="good",
                publication_year=1974,
                rating=4.5,
                author_id=author.id,
                user_id=User.query.filter_by(username="alice").one().id,
            )
        )
        db.session.add(
            Post(
                title="Hello",
                subtitle="Sub",
                content="<p>hi</p>",
                author_id=User.query.filter_by(username="alice").one().id,
            )
        )
        db.session.commit()
    yield flask_app
    with flask_app.app_context():
        db.session.remove()


@pytest.fixture(name="ids")
def ids_fixture(app):
    """Map seeded usernames and records to their ids.

    Args:
        app (Flask): The configured application.

    Returns:
        dict: ``admin``, ``alice``, ``bob``, ``author``, ``book`` and ``post`` ids.
    """
    with app.app_context():
        found = {u.username: u.id for u in User.query.all()}
        found["author"] = Author.query.first().id
        found["book"] = Book.query.first().id
        found["post"] = Post.query.first().id
    return found


def login_as(client, user_id):
    """Log a test client in by writing the session directly.

    Args:
        client (FlaskClient): Client to log in.
        user_id (int): Id of the user to act as.
    """
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


@pytest.fixture(name="client")
def client_fixture(app):
    """Return an anonymous client (CSRF off).

    Args:
        app (Flask): The configured application.

    Returns:
        FlaskClient: Test client.
    """
    return app.test_client()


@pytest.fixture(name="as_user")
def as_user_fixture(app, ids):
    """Return a factory that makes a logged-in client for a seeded username.

    Args:
        app (Flask): The configured application.
        ids (dict): Seeded ids.

    Returns:
        Callable[[str], FlaskClient]: Factory taking ``admin``, ``alice`` or ``bob``.
    """

    def factory(username):
        """Build a client logged in as the given seeded user."""
        client = app.test_client()
        login_as(client, ids[username])
        return client

    return factory


@pytest.fixture(name="csrf_app")
def csrf_app_fixture(app):
    """Turn CSRF protection on for the test, then off again.

    Args:
        app (Flask): The configured application.

    Yields:
        Flask: The application with CSRF enabled.
    """
    app.config["WTF_CSRF_ENABLED"] = True
    yield app
    app.config["WTF_CSRF_ENABLED"] = False


def csrf_token(client, url="/users/login"):
    """Fetch a page and extract its CSRF token.

    Args:
        client (FlaskClient): Client holding the session.
        url (str): Any page that renders a form.

    Returns:
        str: The token to send back in a POST.
    """
    html = client.get(url).get_data(as_text=True)
    match = TOKEN_RE.search(html)
    assert match, f"no csrf token on {url}"
    return match.group(1)
