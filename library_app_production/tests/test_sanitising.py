"""User content is cleaned and escaped before it is shown."""
import pathlib

from data_models import Post, db

EVIL = (
    '<p>ok</p><script>alert(1)</script><img src=x onerror="alert(2)">'
    '<a href="javascript:alert(3)" onclick="alert(4)">link</a>'
)


def test_post_content_is_sanitised(as_user, ids, app):
    """Scripts, event handlers and javascript: URLs never reach the page."""
    with app.app_context():
        Post.query.first().content = EVIL
        db.session.commit()
    html = as_user("bob").get(f"/posts/get_post/{ids['post']}/").get_data(as_text=True)
    assert "<p>ok</p>" in html
    for needle in ("alert(", "onerror", "onclick", "javascript:"):
        assert needle not in html


def test_flash_escapes_title_but_keeps_markup(as_user):
    """A title with HTML is escaped inside the flash, the <strong> stays."""
    response = as_user("alice").post(
        "/posts/add",
        data={"title": "<b>evil", "subtitle": "s", "content": "c"},
        follow_redirects=True,
    )
    html = response.get_data(as_text=True)
    assert "<strong>&lt;b&gt;evil</strong>" in html
    assert "<b>evil" not in html


def test_templates_do_not_mark_user_content_safe():
    """No template pipes anything through the safe filter."""
    root = pathlib.Path(__file__).resolve().parent.parent
    templates = [
        p
        for folder in ("templates", "author", "book", "post", "user")
        for p in (root / folder).rglob("*.html")
    ]
    assert templates
    offenders = [
        str(p)
        for p in templates
        if "| safe" in p.read_text("utf-8") or "|safe" in p.read_text("utf-8")
    ]
    assert offenders == []
