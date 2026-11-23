"""One regression test per bug fixed in the flagship app."""
import requests
import sqlalchemy as sa

from book import book_api
from data_models import Author, Book, Post, User, db
from tests.conftest import PASSWORD

BOOK_FORM = {
    "title": "t",
    "author": "a",
    "isbn": "",
    "condition": "good",
    "rating": "3",
}
REGISTER = {
    "name": "n",
    "username": "newbie",
    "email": "new@example.com",
    "about_user": "",
    "password1": PASSWORD,
    "password2": PASSWORD,
}


# 1. Book year is an integer everywhere
def test_book_update_page_renders_with_integer_year(as_user, ids):
    """The update page shows the stored year instead of crashing."""
    html = as_user("alice").get(f"/books/book/update/{ids['book']}/").get_data(True)
    assert 'value="1974"' in html


def test_book_add_accepts_plain_year(as_user, app):
    """A plain year is stored as an int."""
    as_user("alice").post("/books/add", data={**BOOK_FORM, "publication_year": "1965"})
    with app.app_context():
        assert Book.query.filter_by(title="T").one().publication_year == 1965


def test_book_add_rejects_date_string_year(as_user, app):
    """A date string is refused and nothing is stored."""
    as_user("alice").post(
        "/books/add", data={**BOOK_FORM, "publication_year": "1965-01-01"}
    )
    with app.app_context():
        assert Book.query.count() == 1


def test_book_update_stores_year_and_rerenders(as_user, ids, app):
    """Updating the year stores an int and the page still renders afterwards."""
    alice = as_user("alice")
    alice.post(
        f"/books/book/update/{ids['book']}/",
        data={"title": "D", "publication_year": "1980", "rating": "2", "condition": "x"},
    )
    with app.app_context():
        assert Book.query.first().publication_year == 1980
    assert alice.get(f"/books/book/update/{ids['book']}/").status_code == 200


def test_legacy_date_string_year_still_renders(as_user, ids, app):
    """A row written by the old app (a date string) does not crash the pages."""
    with app.app_context():
        db.session.execute(sa.text("UPDATE books SET publication_year = '1965-01-01'"))
        db.session.commit()
    alice = as_user("alice")
    assert alice.get(f"/books/book/update/{ids['book']}/").status_code == 200
    assert alice.get("/books/").status_code == 200


# 2. Empty search
def test_empty_search_redirects_instead_of_500(client):
    """Empty searches flash and redirect for books and posts."""
    for url in ("/books/search", "/posts/search"):
        assert client.post(url, data={"searched": ""}).status_code == 302


def test_post_search_finds_content(client):
    """A valid post search renders results."""
    response = client.post("/posts/search", data={"searched": "hi"})
    assert response.status_code == 200
    assert "Hello" in response.get_data(as_text=True)


def test_cover_lookup_survives_list_json(monkeypatch):
    """Unexpected JSON shapes from the cover API never raise."""
    monkeypatch.setattr(book_api, "BOOK_API_KEY", "fake-key")

    class Reply:
        """Fake reply whose JSON is a list."""

        status_code = 200
        text = "[]"

        def json(self):
            """Return a list instead of an object."""
            return []

    monkeypatch.setattr(book_api.requests, "get", lambda *a, **k: Reply())
    assert book_api.find_cover_url("123") is None


# 3. Hash column width
def test_password_hash_fits_column():
    """The column is at least as wide as a scrypt hash."""
    user = User(password=PASSWORD)
    assert User.__table__.c.password_hash.type.length >= len(user.password_hash)


# 4. Duplicates
def test_duplicate_username_and_email_on_register(client, app):
    """Registering an existing username or email re-renders the form."""
    for override in ({"username": "alice"}, {"email": "alice@example.com"}):
        response = client.post("/users/add", data={**REGISTER, **override})
        assert response.status_code == 200
    with app.app_context():
        assert User.query.count() == 3


def test_duplicate_on_update_and_dashboard(as_user, ids, app):
    """Changing to a taken username or email flashes and changes nothing."""
    data = {"name": "n", "username": "bob", "email": "alice@example.com"}
    alice = as_user("alice")
    assert alice.post(f"/users/user/update/{ids['alice']}/", data=data).status_code == 200
    assert alice.post("/users/dashboard", data=data).status_code == 200
    with app.app_context():
        assert db.session.get(User, ids["alice"]).username == "alice"


# 5. Validation on update routes
def test_bad_rating_on_update_is_refused(as_user, ids, app):
    """Rating 9 is rejected cleanly."""
    response = as_user("alice").post(
        f"/books/book/update/{ids['book']}/",
        data={"title": "t", "rating": "9", "condition": "x"},
    )
    assert response.status_code == 200
    with app.app_context():
        assert Book.query.first().rating == 4.5


def test_missing_fields_do_not_crash(as_user, ids):
    """Hand-built requests with missing fields never cause a server error."""
    alice = as_user("alice")
    urls = (
        f"/books/book/update/{ids['book']}/",
        f"/posts/post/update/{ids['post']}/",
        f"/users/user/update/{ids['alice']}/",
    )
    for url in urls:
        for data in ({}, {"unrelated": "x"}):
            assert alice.post(url, data=data).status_code in (200, 302)


def test_register_without_about_user_works(client, app):
    """about_user is optional."""
    data = {k: v for k, v in REGISTER.items() if k != "about_user"}
    assert client.post("/users/add", data=data).status_code == 302
    with app.app_context():
        assert User.query.filter_by(username="newbie").one().about_user == ""


def test_book_add_without_condition_works(as_user, app):
    """The condition field is optional."""
    data = {k: v for k, v in BOOK_FORM.items() if k != "condition"}
    as_user("alice").post("/books/add", data=data)
    with app.app_context():
        assert Book.query.filter_by(title="T").count() == 1


# 6. Author without dates
def test_author_without_dates(as_user, app):
    """An author can be created with no dates at all."""
    response = as_user("alice").post("/authors/add", data={"name": "no dates"})
    assert response.status_code == 302
    with app.app_context():
        assert Author.query.filter_by(name="No Dates").one().death_date is None


# 7. Emails are private
def test_emails_hidden_from_anonymous(client, ids):
    """Anonymous visitors see no email addresses."""
    for url in ("/", "/users/", f"/users/get_user/{ids['alice']}/"):
        assert "@example.com" not in client.get(url).get_data(True)


def test_emails_visible_to_owner_and_admin_only(as_user, ids):
    """Owner and admin see the email, other users do not."""
    url = f"/users/get_user/{ids['alice']}/"
    assert "alice@example.com" in as_user("alice").get(url).get_data(True)
    assert "alice@example.com" in as_user("admin").get(url).get_data(True)
    assert "alice@example.com" not in as_user("bob").get(url).get_data(True)


# 9. Admin flag
def test_new_registrant_is_not_admin(client, app):
    """Registration never grants admin."""
    client.post("/users/add", data=REGISTER)
    with app.app_context():
        assert User.query.filter_by(username="newbie").one().is_admin is False


def test_make_admin_command(app):
    """The make-admin command promotes an existing user and rejects unknown ones."""
    runner = app.test_cli_runner()
    assert runner.invoke(args=["make-admin", "bob"]).exit_code == 0
    with app.app_context():
        assert User.query.filter_by(username="bob").one().is_admin is True
    assert runner.invoke(args=["make-admin", "nobody"]).exit_code != 0


# 10. Cover lookup failures
def test_book_add_survives_cover_timeout(as_user, app, monkeypatch):
    """A timeout from the cover API still saves the book, without a cover."""
    monkeypatch.setattr(book_api, "BOOK_API_KEY", "fake-key")

    def boom(*_args, **_kwargs):
        """Simulate a network timeout."""
        raise requests.Timeout("slow")

    monkeypatch.setattr(book_api.requests, "get", boom)
    as_user("alice").post("/books/add", data={**BOOK_FORM, "isbn": "123"})
    with app.app_context():
        assert Book.query.filter_by(title="T").one().cover_url is None


def test_book_add_survives_cover_error_status(as_user, app, monkeypatch):
    """A non-200, non-JSON reply from the cover API still saves the book."""
    monkeypatch.setattr(book_api, "BOOK_API_KEY", "fake-key")

    class Reply:
        """Fake HTTP reply with a non-JSON body."""

        status_code = 503
        text = "unavailable"

        def json(self):
            """Fail like a real non-JSON body."""
            raise ValueError("no json")

    monkeypatch.setattr(book_api.requests, "get", lambda *a, **k: Reply())
    as_user("alice").post("/books/add", data={**BOOK_FORM, "isbn": "123"})
    with app.app_context():
        assert Book.query.filter_by(title="T").count() == 1
    assert book_api.find_cover_url("123") is None


# 11. Deleting a user
def test_deleting_user_cascades_to_books_and_posts(as_user, ids, app):
    """Alice's books and posts go with her account, nobody is left orphaned."""
    as_user("alice").post(f"/users/user/delete/{ids['alice']}/")
    with app.app_context():
        assert User.query.filter_by(username="alice").count() == 0
        assert Book.query.count() == 0
        assert Post.query.count() == 0


def test_last_admin_cannot_be_deleted(as_user, ids, app):
    """The only admin account is protected."""
    as_user("admin").post(f"/users/user/delete/{ids['admin']}/")
    with app.app_context():
        assert db.session.get(User, ids["admin"]) is not None


# 2. LIKE wildcards in search are literal characters
def test_book_search_percent_is_literal(client):
    """A lone ``%`` matches nothing instead of every book and author."""
    html = client.post("/books/search", data={"searched": "%"}).get_data(True)
    assert "Dispossessed" not in html
    assert "Ursula" not in html


def test_book_search_underscore_is_literal(client):
    """``_`` no longer stands in for one arbitrary character."""
    html = client.post("/books/search", data={"searched": "d_spossessed"}).get_data(True)
    assert "Dispossessed" not in html


def test_book_search_plain_term_still_matches(client):
    """Escaping does not break ordinary substring search."""
    html = client.post("/books/search", data={"searched": "dispos"}).get_data(True)
    assert "Dispossessed" in html


def test_post_search_wildcards_are_literal(client):
    """The post search treats ``%`` and ``_`` literally too."""
    assert "Hello" not in client.post("/posts/search", data={"searched": "%"}).get_data(True)
    assert "Hello" not in client.post("/posts/search", data={"searched": "h_"}).get_data(True)
    assert "Hello" in client.post("/posts/search", data={"searched": "hi"}).get_data(True)
