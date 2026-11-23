"""OC006 bug 6: deleting a movie must be POST-only and CSRF protected."""
import re

import pytest

from datamanagement.sqlite_models import Movie
from tests.conftest import add_movie, csrf_from, signup_and_signin


@pytest.mark.parametrize("storage", ["sqlite", "json"])
def test_get_delete_is_not_allowed_and_keeps_movie(client, app, storage):
    """A GET to the delete URL is 405 and the movie survives."""
    signup_and_signin(client, storage)
    add_movie(client)
    resp = client.get("/users/1/delete_movie/1")
    assert resp.status_code == 405
    assert "Fake Movie" in client.get("/movies").get_data(as_text=True)


@pytest.mark.parametrize("storage", ["sqlite", "json"])
def test_post_without_csrf_token_is_rejected(client, storage):
    """A POST without a CSRF token is 400 and the movie survives."""
    signup_and_signin(client, storage)
    add_movie(client)
    resp = client.post("/users/1/delete_movie/1")
    assert resp.status_code == 400
    assert "Fake Movie" in client.get("/movies").get_data(as_text=True)


@pytest.mark.parametrize("storage", ["sqlite", "json"])
def test_post_with_csrf_token_deletes(client, app, storage):
    """A POST carrying the page's CSRF token deletes the movie."""
    signup_and_signin(client, storage)
    add_movie(client)
    token = csrf_from(client, "/movies")
    resp = client.post("/users/1/delete_movie/1", data={"csrf_token": token})
    assert resp.status_code == 302
    assert "card-title" not in client.get("/movies").get_data(as_text=True)


def test_movies_page_uses_post_form_not_link(client):
    """The list page renders a POST form for delete and no delete anchor."""
    signup_and_signin(client, "sqlite")
    add_movie(client)
    html = client.get("/movies").get_data(as_text=True)
    assert not re.search(r'<a[^>]*delete_movie', html)
    assert not re.search(r'<a[^>]*href="[^"]*/delete_movie/', html)
    assert re.search(
        r'<form[^>]*method="POST"[^>]*action="/users/1/delete_movie/1"', html
    )


@pytest.mark.parametrize(
    "url", ["/user/1/movie/1/info", "/users/1/movies", "/add_review/movie/1"]
)
def test_other_pages_use_post_form(client, url):
    """Every page offering Delete uses a POST form carrying a CSRF token."""
    signup_and_signin(client, "sqlite")
    add_movie(client)
    html = client.get(url).get_data(as_text=True)
    assert not re.search(r'href="[^"]*/delete_movie/', html)
    assert re.search(
        r'<form[^>]*method="POST"[^>]*action="/users/1/delete_movie/1"[^>]*>\s*'
        r'<input[^>]*name="csrf_token"',
        html,
    )


def test_other_user_cannot_delete(client, app):
    """A signed-in user cannot delete another user's movie (403)."""
    signup_and_signin(client, "sqlite", username="alice")
    add_movie(client)
    client.get("/signout")
    signup_and_signin(client, "sqlite", username="mallory")
    token = csrf_from(client, "/movies/add")
    resp = client.post("/users/1/delete_movie/1", data={"csrf_token": token})
    assert resp.status_code == 403
    with app.app_context():
        assert Movie.query.count() == 1
