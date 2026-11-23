"""Regression tests for the OC007 bugs in the blog backend API.

Every test runs against a temporary copy of the JSON store, never the real
``STORAGE/posts.json``. Run from ``backend/`` with ``python -m pytest tests``.
"""

import json
import os
import re
import sys

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

import backend_app  # noqa: E402
import backend_methods  # noqa: E402

FRONTEND_JS = os.path.join(BACKEND_DIR, "..", "frontend", "static", "main.js")

POSTS_V10 = [
    {"id": 1, "title": "Charlie", "content": "Aaa"},
    {"id": 2, "title": "Alpha", "content": "Ccc"},
    {"id": 3, "title": "Bravo", "content": "Bbb"},
]


def write_store(path, version, posts):
    """Write a store file with the given version and posts."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"version": version, "posts": posts}, handle)


@pytest.fixture
def store(tmp_path, monkeypatch):
    """Point the backend at a temporary store holding three v1.0 posts."""
    folder = tmp_path / "STORAGE"
    folder.mkdir()
    file_path = str(folder / "posts.json")
    write_store(file_path, 1.0, [dict(p) for p in POSTS_V10])
    monkeypatch.setattr(backend_methods, "FOLDER_PATH", str(folder))
    monkeypatch.setattr(backend_methods, "FILE_PATH", file_path)
    return file_path


@pytest.fixture
def client(store):  # pylint: disable=unused-argument
    """Flask test client bound to the temporary store."""
    backend_app.app.config["TESTING"] = True
    return backend_app.app.test_client()


def titles(response):
    """Return the list of titles in a JSON posts response."""
    return [post["title"] for post in response.get_json()]


def test_sort_by_title_asc_and_desc(client):
    """Non-date sorts must actually sort and honour ``direction``."""
    asc = client.get("/api/posts?sort=title&direction=asc")
    desc = client.get("/api/posts?sort=title&direction=desc")
    assert titles(asc) == ["Alpha", "Bravo", "Charlie"]
    assert titles(desc) == ["Charlie", "Bravo", "Alpha"]


def test_sort_by_content_and_id(client):
    """Sorting by content and by id works in both directions."""
    assert titles(client.get("/api/posts?sort=content")) == ["Charlie", "Bravo", "Alpha"]
    ids = [p["id"] for p in client.get("/api/posts?sort=id&direction=desc").get_json()]
    assert ids == [3, 2, 1]


def test_sort_by_unknown_key_is_400(client):
    """An unknown sort key is a client error, not a 500."""
    assert client.get("/api/posts?sort=nonsense").status_code == 400


def test_non_integer_id_is_400(client):
    """``id=x`` returns 400 with a JSON message, not 500."""
    for url in ("/api/posts?id=x", "/api/posts/search?id=x"):
        response = client.get(url)
        assert response.status_code == 400, url
        assert isinstance(response.get_json()["message"], str)


def test_sort_by_date_without_dates_is_400(client):
    """``sort=date`` on a store with no date field is 400, not KeyError/500."""
    assert client.get("/api/posts?sort=date").status_code == 400


def test_sort_by_date_with_dates_sorts(store, client):
    """``sort=date`` still works when every post has a date (v1.1)."""
    posts = [
        {"id": 1, "title": "A", "content": "x", "date": "2020-05-01"},
        {"id": 2, "title": "B", "content": "y", "date": "2019-01-01"},
    ]
    write_store(store, 1.1, posts)
    backend_app.CHOSEN = 1.1
    try:
        response = client.get("/api/posts?sort=date&direction=asc")
    finally:
        backend_app.CHOSEN = 1.0
    assert response.status_code == 200
    assert [p["id"] for p in response.get_json()] == [2, 1]


def test_check_version_never_destroys_posts(store):
    """A version mismatch on 1.0 must keep the real posts (data loss bug)."""
    write_store(store, 1.1, [{"id": 7, "title": "Keep", "content": "Me", "date": "2021-01-01"}])
    backend_methods.check_version(1.0)
    with open(store, encoding="utf-8") as handle:
        data = json.load(handle)
    assert [p["id"] for p in data["posts"]] == [7]
    assert data["version"] == 1.0


def test_get_after_downgrade_keeps_posts(store, client):
    """A plain GET after switching back to 1.0 must not wipe the store."""
    write_store(store, 1.2, [{"id": 9, "title": "Keep", "content": "Me", "author": "A"}])
    client.get("/api/posts")
    with open(store, encoding="utf-8") as handle:
        assert [p["id"] for p in json.load(handle)["posts"]] == [9]


def test_corrupt_store_is_not_overwritten(store):
    """A corrupt file must be left alone, not replaced or crash with AttributeError."""
    with open(store, "w", encoding="utf-8") as handle:
        handle.write("{not json")
    backend_methods.check_version(1.0)
    with open(store, encoding="utf-8") as handle:
        assert handle.read() == "{not json"


def test_upgrade_keeps_existing_dates(store):
    """Upgrading to 1.1 must only fill missing dates, never overwrite real ones."""
    write_store(store, 1.0, [
        {"id": 1, "title": "A", "content": "x", "date": "2001-02-03"},
        {"id": 2, "title": "B", "content": "y"},
    ])
    backend_methods.check_version(1.1)
    with open(store, encoding="utf-8") as handle:
        posts = json.load(handle)["posts"]
    assert posts[0]["date"] == "2001-02-03"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", posts[1]["date"])


def test_version_zero_endpoints(monkeypatch):
    """CHOSEN=0 (in-memory posts) must serve all routes without 500."""
    monkeypatch.setattr(backend_app, "CHOSEN", 0)
    monkeypatch.setattr(backend_app, "POSTS", [
        {"id": 1, "title": "Abc", "content": "Zz"},
        {"id": 2, "title": "Dcb", "content": "Tw"},
    ])
    test_client = backend_app.app.test_client()
    assert test_client.get("/api/posts").status_code == 200
    assert test_client.get("/api/posts?sort=title&direction=desc").status_code == 200
    assert test_client.get("/api/posts/search?title=Abc").status_code == 200
    created = test_client.post("/api/posts", json={"title": "New", "content": "Post"})
    assert created.status_code == 200
    assert test_client.put("/api/posts/1", json={"title": "Upd", "content": "Ated"}).status_code == 200
    assert test_client.delete("/api/posts/2").status_code == 200


def test_cors_rejects_foreign_origin(client):
    """A foreign Origin must not receive an allow-origin header."""
    evil = client.get("/api/posts", headers={"Origin": "http://evil.example"})
    assert "Access-Control-Allow-Origin" not in evil.headers
    local = client.get("/api/posts", headers={"Origin": "http://127.0.0.1:5001"})
    assert local.headers.get("Access-Control-Allow-Origin") == "http://127.0.0.1:5001"


def test_frontend_does_not_inject_html():
    """The post list must be built with textContent, not innerHTML templates."""
    with open(FRONTEND_JS, encoding="utf-8") as handle:
        source = handle.read()
    assert "${post." not in source
    assert "onclick" not in source
