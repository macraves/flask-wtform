"""post related routes."""
from markupsafe import Markup
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from permissions import can_modify, flash_form_errors
from allwebforms import PostForm, SearchForm
from data_models import db, Post

# Create blueprints connection
post_bp = Blueprint("post", __name__, url_prefix="/posts", template_folder="templates")


class PostError(Exception):
    """Post error."""

    def __init__(self, message):
        """Store the error message.

        Args:
            message (str): Error description.
        """
        self.message = message


def reset_post_form(form):
    """Reset pos form."""
    form.title.data = ""
    form.subtitle.data = ""
    form.content.data = ""


# Create search function for post content
@post_bp.route("/search", methods=["POST"])
def search():
    """Search function."""
    form = SearchForm()
    if not form.validate_on_submit():
        flash("Enter a search term")
        return redirect(url_for("index"))
    searched = form.searched.data
    posts = Post.query.filter(Post.content.like("%" + searched + "%"))
    posts = posts.order_by(Post.title).all()
    return render_template("post_search.html", searched=searched, posts=posts)


@post_bp.route("/get_post/<int:post_id>/")
def get_post(post_id):
    """Get post."""
    post = Post.query.get_or_404(post_id)
    if post is None:
        flash("post not found")
        return redirect("/")
    return render_template("get_post.html", post=post, post_id=post_id)


@post_bp.route("/")
def posts_all():
    """Posts page."""
    posts = Post.query.all()
    return render_template("posts_all.html", header="All posts", posts=posts)


@post_bp.route("/add", methods=["GET", "POST"])
@login_required
def post_add():
    """Add post."""
    if not current_user.is_authenticated:
        flash("You need to login first")
        return redirect(url_for("user.login"))
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data.title().strip(),
            subtitle=form.subtitle.data.strip(),
            content=form.content.data.strip(),
            author_id=current_user.id,
        )
        try:
            db.session.add(post)
            db.session.commit()
            flash(Markup("<strong>{}</strong> has been added").format(form.title.data))
            reset_post_form(form)
        except PostError:
            flash("Operation failed during the add process")
        return redirect("/posts")
    if request.method == "POST":
        flash_form_errors(form)
    return render_template("post_add.html", header="Add Post", form=form)


@post_bp.route("/post/update/<int:post_id>/", methods=["GET", "POST"])
@login_required
def post_update(post_id):
    """Update post."""
    post = Post.query.get_or_404(post_id)
    if post is None:
        flash("post not found")
        return redirect("/posts/all")
    if not can_modify(post.author_id):
        flash("You can only change your own posts")
        return redirect(url_for("post.posts_all"))
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data.title().strip()
        post.subtitle = form.subtitle.data.strip()
        post.content = form.content.data.strip()
        try:
            db.session.commit()
            flash(Markup("<strong>Post ID: {}</strong> has been updated").format(post.id))
        except PostError:
            flash("Operation failed during the update process")
        return redirect(url_for("post.posts_all"))
    if request.method == "POST":
        flash_form_errors(form)
    return render_template(
        "post_update.html", header="Update post", form=form, post_id=post_id
    )


@post_bp.route("/post/delete/<int:post_id>/", methods=["POST"])
@login_required
def post_delete(post_id):
    """Delete post."""
    post = Post.query.get_or_404(post_id)
    if post is None:
        flash("post not found")
        return redirect("/posts")
    if not can_modify(post.author_id):
        flash("You can only delete your own posts")
        return redirect(url_for("post.posts_all"))
    flash(Markup("<strong>Post ID: {}</strong> has been deleted").format(post.id))
    try:
        db.session.delete(post)
        db.session.commit()
    except PostError:
        flash("Operation failed during the delete process")
    return redirect("/posts")
