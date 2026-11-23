"""CSRF enforcement and HTTP method rules."""
import pytest

from data_models import Book
from tests.conftest import PASSWORD, csrf_token

DELETE_ROUTES = [
    "/books/book/delete/{book}/",
    "/posts/post/delete/{post}/",
    "/authors/delete/{author}/",
    "/users/user/delete/{alice}/",
]


@pytest.mark.parametrize("template", DELETE_ROUTES + ["/users/logout"])
def test_get_is_not_allowed_on_state_changing_routes(as_user, ids, template):
    """Deleting and logging out need POST."""
    assert as_user("admin").get(template.format(**ids)).status_code == 405


def test_post_without_token_is_refused(csrf_app, as_user, ids):
    """A POST with no CSRF token changes nothing and flashes an explanation."""
    client = as_user("alice")
    response = client.post(f"/books/book/delete/{ids['book']}/", follow_redirects=True)
    assert "form expired" in response.get_data(as_text=True)
    with csrf_app.app_context():
        assert Book.query.count() == 1


def test_post_with_token_works(csrf_app, as_user, ids):
    """The same POST with a valid token deletes the book."""
    client = as_user("alice")
    token = csrf_token(client, f"/books/book/update/{ids['book']}/")
    client.post(f"/books/book/delete/{ids['book']}/", data={"csrf_token": token})
    with csrf_app.app_context():
        assert Book.query.count() == 0


def test_login_needs_and_accepts_token(csrf_app, client):
    """Login fails without a token and succeeds with one."""
    data = {"username": "alice", "password": PASSWORD}
    refused = client.post("/users/login", data=data, follow_redirects=True)
    assert "form expired" in refused.get_data(as_text=True)
    token = csrf_token(client)
    accepted = client.post(
        "/users/login", data={**data, "csrf_token": token}, follow_redirects=True
    )
    assert "logged in successfully" in accepted.get_data(as_text=True)


def test_navbar_search_works_with_token(csrf_app, client):
    """The navbar search form posts a token and gets results."""
    token = csrf_token(client, "/")
    response = client.post(
        "/books/search", data={"searched": "dispo", "csrf_token": token}
    )
    assert response.status_code == 200
    assert "Dispossessed" in response.get_data(as_text=True)
