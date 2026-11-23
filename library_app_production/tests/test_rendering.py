"""Every page renders, including the update pages."""
import pytest

PUBLIC = [
    "/",
    "/books/",
    "/books/?sort=title&order=desc",
    "/books/?sort=author",
    "/books/get_book/{book}/",
    "/posts/",
    "/posts/get_post/{post}/",
    "/authors/",
    "/authors/get_author/{author}/",
    "/users/",
    "/users/get_user/{alice}/",
    "/users/login",
    "/users/add",
    "/date",
]
AUTHED = [
    "/books/add",
    "/books/book/update/{book}/",
    "/posts/add",
    "/posts/post/update/{post}/",
    "/authors/add",
    "/authors/update/{author}/",
    "/users/dashboard",
    "/users/user/update/{alice}/",
    "/users/admin",
]


@pytest.mark.parametrize("template", PUBLIC)
def test_public_pages_render(client, ids, template):
    """Public pages return 200 to anonymous visitors."""
    assert client.get(template.format(**ids)).status_code == 200


@pytest.mark.parametrize("template", AUTHED)
def test_authenticated_pages_render(as_user, ids, template):
    """Forms and the admin page return 200 for the admin."""
    assert as_user("admin").get(template.format(**ids)).status_code == 200


def test_missing_records_are_404(client):
    """Unknown ids give a 404, not a crash."""
    assert client.get("/books/get_book/999/").status_code == 404
