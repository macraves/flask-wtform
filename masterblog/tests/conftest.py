"""Shared pytest fixtures for the masterblog tests.

Every test works on a temporary copy of the JSON data; the real
``masterblog/data/blogs.json`` is never touched.
"""

import json
import os
import re
import sys

import pytest

MASTERBLOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MASTERBLOG_DIR)
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import app as app_module  # noqa: E402
import blogs_routes  # noqa: E402

SEED = [
    {"id": 1, "title": "One", "author": "Ann", "content": "first"},
    {"id": 2, "title": "Two", "author": "Bob", "content": "second"},
    {"id": 3, "title": "Three", "author": "Cy", "content": "third"},
]


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    """Create a seeded JSON data file in tmp_path and point the routes at it.

    Args:
        tmp_path: pytest temporary directory.
        monkeypatch: pytest monkeypatch fixture.

    Returns:
        pathlib.Path: The temporary data file.
    """
    path = tmp_path / "blogs.json"
    path.write_text(json.dumps(SEED), encoding="utf-8")
    monkeypatch.setattr(blogs_routes, "FILE_PATH", str(path))
    return path


@pytest.fixture
def client(data_file):
    """Return a Flask test client bound to the temporary data file.

    Args:
        data_file: The seeded temporary data file fixture.

    Returns:
        flask.testing.FlaskClient: Client with CSRF protection left enabled.
    """
    app_module.app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
    return app_module.app.test_client()


def get_token(client, url="/blog_add"):
    """Fetch a page and extract its CSRF token.

    Args:
        client: Flask test client.
        url (str): Page that renders a CSRF token.

    Returns:
        str: The CSRF token value.
    """
    html = client.get(url).get_data(as_text=True)
    tag = re.search(r'<input[^>]*name="csrf_token"[^>]*>', html)
    assert tag, f"no csrf_token input on {url}"
    return re.search(r'value="([^"]+)"', tag.group(0)).group(1)
