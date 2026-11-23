"""Regression tests for case OC009 (masterblog bugs)."""

import json

import pytest

from conftest import SEED, get_token


def load(path):
    """Read the JSON data file.

    Args:
        path: Path to the data file.

    Returns:
        object: The decoded JSON content.
    """
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("action", ["delete", "like"])
def test_state_changing_routes_reject_get(client, data_file, action):
    """Bug 1: delete and like must not be reachable with GET."""
    assert client.get(f"/blogs/{action}/1").status_code == 405
    assert load(data_file) == SEED


def test_delete_post_requires_csrf(client, data_file):
    """Bug 1: POST delete without a CSRF token is refused."""
    assert client.post("/blogs/delete/1").status_code == 400
    assert load(data_file) == SEED


def test_like_post_requires_csrf(client, data_file):
    """Bug 1: POST like without a CSRF token is refused."""
    assert client.post("/blogs/like/1").status_code == 400
    assert load(data_file) == SEED


def test_delete_post_with_token_deletes(client, data_file):
    """Bug 1: POST delete with a token removes the blog."""
    token = get_token(client)
    resp = client.post("/blogs/delete/1", data={"csrf_token": token})
    assert resp.status_code == 302
    assert [b["id"] for b in load(data_file)] == [2, 3]


def test_like_post_with_token_likes(client, data_file):
    """Bug 1: POST like with a token increments the like counter."""
    token = get_token(client)
    client.post("/blogs/like/1", data={"csrf_token": token})
    assert load(data_file)[0]["like"] == 1


def test_blog_page_uses_post_forms_with_token(client):
    """Bug 1: the blog page renders like/delete as POST forms with a token."""
    html = client.get("/blogs/1").get_data(as_text=True)
    assert html.count('method="post"') + html.count('method="POST"') >= 2
    assert html.count('name="csrf_token"') >= 2


def test_update_requires_csrf(client, data_file):
    """Bug 2: update POST without a CSRF token is refused."""
    resp = client.post(
        "/blogs/update/1", data={"author": "x", "title": "y", "content": "z"}
    )
    assert resp.status_code == 400
    assert load(data_file) == SEED


def test_update_validates_input(client, data_file):
    """Bug 2: update POST with empty fields is rejected, data unchanged."""
    token = get_token(client, "/blogs/update/1")
    resp = client.post(
        "/blogs/update/1",
        data={"csrf_token": token, "author": "", "title": "", "content": ""},
    )
    assert resp.status_code == 200
    assert load(data_file) == SEED


def test_update_valid_saves(client, data_file):
    """Bug 2: a valid, tokened update is saved."""
    token = get_token(client, "/blogs/update/1")
    resp = client.post(
        "/blogs/update/1",
        data={"csrf_token": token, "author": "New", "title": "Hello", "content": "c"},
    )
    assert resp.status_code == 302
    assert load(data_file)[0]["author"] == "New"


def test_500_handler_renders(client, monkeypatch):
    """Bug 3: an unhandled error yields a rendered 500 page, not a template error."""
    import blogs_routes

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(blogs_routes, "JsonBlog", boom)
    resp = client.get("/blogs")
    assert resp.status_code == 500
    assert "Internal Server Error" in resp.get_data(as_text=True)


def test_flash_is_escaped(client):
    """Bug 4: flashed messages are HTML-escaped."""
    with client.session_transaction() as sess:
        sess["_flashes"] = [("message", "<b>pwn</b>")]
    html = client.get("/").get_data(as_text=True)
    assert "&lt;b&gt;pwn&lt;/b&gt;" in html
    assert "<b>pwn</b>" not in html


def test_ids_not_reused_after_delete(client, data_file):
    """Bug 5: deleting the highest id must not let the next blog reuse it."""
    token = get_token(client)
    client.post("/blogs/delete/3", data={"csrf_token": token})
    client.post(
        "/blog_add",
        data={"csrf_token": token, "author": "a", "title": "t", "content": "c"},
    )
    assert [b["id"] for b in load(data_file)] == [1, 2, 4]


def test_corrupt_json_does_not_crash_or_get_overwritten(client, data_file):
    """Bug 6: corrupt JSON gives a graceful response and is left untouched."""
    data_file.write_text("{not json", encoding="utf-8")
    token = get_token(client)
    assert client.get("/blogs").status_code == 200
    assert client.get("/blogs/1").status_code == 404
    resp = client.post(
        "/blog_add",
        data={"csrf_token": token, "author": "a", "title": "t", "content": "c"},
    )
    assert resp.status_code == 503
    assert data_file.read_text(encoding="utf-8") == "{not json"


def test_no_dead_ckeditor_usage(client):
    """Bug 7: no never-initialised CKEditor field; plain textarea is rendered."""
    html = client.get("/blog_add").get_data(as_text=True)
    assert "ckeditor" not in html
    import post_forms

    assert not hasattr(post_forms, "CKEditorField")
