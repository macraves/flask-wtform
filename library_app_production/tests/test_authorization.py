"""Who may change what: owners, other users, the admin and anonymous visitors."""
import pytest

from data_models import Author, Book, Post, User, db

PROTECTED_POSTS = [
    "/books/add",
    "/books/book/update/{book}/",
    "/books/book/delete/{book}/",
    "/posts/add",
    "/posts/post/update/{post}/",
    "/posts/post/delete/{post}/",
    "/authors/add",
    "/authors/update/{author}/",
    "/authors/delete/{author}/",
    "/users/user/update/{alice}/",
    "/users/user/delete/{alice}/",
    "/users/dashboard",
    "/users/admin",
]


@pytest.mark.parametrize("template", PROTECTED_POSTS)
def test_anonymous_is_redirected_to_login(client, ids, template):
    """Anonymous visitors never reach a protected route."""
    method = "GET" if template == "/users/admin" else "POST"
    response = client.open(template.format(**ids), method=method)
    assert response.status_code == 302
    assert "/users/login" in response.headers["Location"]


def test_non_owner_cannot_delete_book(as_user, ids, app):
    """Bob cannot delete alice's book."""
    as_user("bob").post(f"/books/book/delete/{ids['book']}/")
    with app.app_context():
        assert Book.query.count() == 1


def test_non_owner_cannot_update_book(as_user, ids, app):
    """Bob cannot rename alice's book."""
    as_user("bob").post(
        f"/books/book/update/{ids['book']}/",
        data={"title": "Hacked", "rating": "1", "condition": "bad"},
    )
    with app.app_context():
        assert Book.query.first().title == "Dispossessed"


def test_owner_and_admin_can_update_book(as_user, ids, app):
    """Alice and the admin can both edit alice's book."""
    for who, title in (("alice", "By Alice"), ("admin", "By Admin")):
        as_user(who).post(
            f"/books/book/update/{ids['book']}/",
            data={"title": title, "rating": "3", "condition": "ok"},
        )
        with app.app_context():
            assert Book.query.first().title == title.title()


def test_non_owner_cannot_delete_post(as_user, ids, app):
    """Bob cannot delete alice's post."""
    as_user("bob").post(f"/posts/post/delete/{ids['post']}/")
    with app.app_context():
        assert Post.query.count() == 1


def test_non_owner_cannot_update_post(as_user, ids, app):
    """Bob cannot rewrite alice's post."""
    as_user("bob").post(
        f"/posts/post/update/{ids['post']}/",
        data={"title": "x", "subtitle": "y", "content": "z"},
    )
    with app.app_context():
        assert Post.query.first().title == "Hello"


def test_owner_can_delete_post(as_user, ids, app):
    """Alice can delete her own post."""
    as_user("alice").post(f"/posts/post/delete/{ids['post']}/")
    with app.app_context():
        assert Post.query.count() == 0


def test_non_owner_cannot_change_or_delete_account(as_user, ids, app):
    """Bob cannot edit or delete alice's account."""
    bob = as_user("bob")
    bob.post(
        f"/users/user/update/{ids['alice']}/",
        data={"name": "X", "username": "hacked", "email": "h@example.com"},
    )
    bob.post(f"/users/user/delete/{ids['alice']}/")
    with app.app_context():
        assert db.session.get(User, ids["alice"]).username == "alice"


def test_non_admin_cannot_touch_authors(as_user, ids, app):
    """Alice cannot update or delete an author."""
    alice = as_user("alice")
    alice.post(f"/authors/update/{ids['author']}/", data={"name": "Hacked"})
    alice.post(f"/authors/delete/{ids['author']}/")
    with app.app_context():
        assert Author.query.one().name == "Ursula Le Guin"


def test_admin_can_update_author(as_user, ids, app):
    """The admin can rename an author."""
    as_user("admin").post(f"/authors/update/{ids['author']}/", data={"name": "Renamed"})
    with app.app_context():
        assert Author.query.one().name == "Renamed"


def test_admin_author_delete_removes_books(as_user, ids, app):
    """Deleting an author also deletes that author's books."""
    as_user("admin").post(f"/authors/delete/{ids['author']}/")
    with app.app_context():
        assert Author.query.count() == 0
        assert Book.query.count() == 0


def test_admin_page_is_admin_only(as_user):
    """/users/admin shows for the admin and redirects everyone else."""
    assert as_user("admin").get("/users/admin").status_code == 200
    assert as_user("alice").get("/users/admin").status_code == 302
