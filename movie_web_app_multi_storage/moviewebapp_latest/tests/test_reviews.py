"""OC006 bugs 1 and 2: review routes must not return 500."""
from datamanagement.sqlite_models import Review
from tests.conftest import add_movie, csrf_from, signup_and_signin


def test_add_review_get_renders_for_sqlite_user(client):
    """GET /add_review/movie/<id> returns 200 for the owner of the movie."""
    signup_and_signin(client, "sqlite")
    add_movie(client)
    resp = client.get("/add_review/movie/1")
    assert resp.status_code == 200


def test_add_review_post_saves_review(client, app):
    """POST /add_review/movie/<id> stores a Review and redirects."""
    signup_and_signin(client, "sqlite")
    add_movie(client)
    token = csrf_from(client, "/add_review/movie/1")
    resp = client.post(
        "/add_review/movie/1", data={"content": "great film", "csrf_token": token}
    )
    assert resp.status_code == 302
    with app.app_context():
        reviews = Review.query.all()
        assert [r.review_text for r in reviews] == ["great film"]
        assert reviews[0].user_id == 1


def test_add_review_without_session_redirects_to_signin(client):
    """No session: redirect to signin instead of a KeyError 500."""
    resp = client.get("/add_review/movie/1")
    assert resp.status_code == 302
    assert "/signin" in resp.headers["Location"]


def test_all_reviews_requires_login(client):
    """/all-reviews redirects anonymous visitors to signin."""
    resp = client.get("/all-reviews")
    assert resp.status_code == 302
    assert "/signin" in resp.headers["Location"]


def test_all_reviews_ok_for_sqlite_user(client):
    """/all-reviews returns 200 for a signed-in SQLite user."""
    signup_and_signin(client, "sqlite")
    assert client.get("/all-reviews").status_code == 200


def test_all_reviews_json_and_csv_users_get_message_not_500(client):
    """JSON and CSV users get a clear message because reviews are SQLite only."""
    for index, storage in enumerate(("json", "csv")):
        if index:
            client.post(
                "/signout", data={"csrf_token": csrf_from(client, "/dashboard")}
            )
        signup_and_signin(client, storage, username=f"user_{storage}")
        resp = client.get("/all-reviews")
        assert resp.status_code == 200, storage
        assert "SQLite" in resp.get_data(as_text=True), storage
