"""user related routes."""
from markupsafe import Markup
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from permissions import can_modify, flash_form_errors, is_admin
from allwebforms import LoginForm, UserForm, UserUpdateForm
from data_models import db, Author, Book, Post, User

# Create blueprints connection
user_bp = Blueprint("user", __name__, url_prefix="/users", template_folder="templates")


def find_conflict(username, email, exclude_id=None):
    """Find an existing account that already uses a username or email.

    Args:
        username (str): Wanted username.
        email (str): Wanted email address.
        exclude_id (int | None): User id to ignore, the one being edited.

    Returns:
        str | None: A message naming the clashing field, or None if both are free.
    """
    by_name = User.query.filter_by(username=username).first()
    if by_name and by_name.id != exclude_id:
        return "That username is already taken"
    by_email = User.query.filter_by(email=email).first()
    if by_email and by_email.id != exclude_id:
        return "That email is already registered"
    return None


def apply_profile(user, form):
    """Copy validated profile fields onto a user and save them.

    Args:
        user (User): Account to change.
        form (UserUpdateForm): Validated form holding the new values.

    Returns:
        bool: True when saved, False when a username or email clash was flashed.
    """
    username = form.username.data.strip()
    email = form.email.data.strip()
    conflict = find_conflict(username, email, exclude_id=user.id)
    if conflict:
        flash(conflict)
        return False
    user.name = form.name.data.title().strip()
    user.username = username
    user.email = email
    user.about_user = (form.about_user.data or "").strip()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("That username or email is already in use")
        return False
    return True


# Admin API
@user_bp.route("/admin")
@login_required
def admin():
    """Admin page."""
    if is_admin():
        authors = Author.query.all()
        books = Book.query.all()
        posts = Post.query.all()
        users = User.query.all()
        return render_template(
            "admin.html",
            header="Admin",
            authors=authors,
            books=books,
            posts=posts,
            users=users,
        )
    flash("You are not authorized to view this page")
    return redirect("/users")


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login route for the users."""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user)
            flash(f"{username} logged in successfully")
            return redirect(url_for("user.dashboard"))
        flash("Invalid username or password. Try again!")
    return render_template("user_login.html", header="Login", form=form)


# Create dashboard route
@user_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Dashboard route for the users."""
    user_id = current_user.id
    user = db.get_or_404(User, user_id)
    if current_user.id != user.id:
        flash("You can only update your own account")
        return redirect("/users")
    if user is None:
        flash("User not found")
        return redirect("/users")
    form = UserUpdateForm(obj=user)
    if form.validate_on_submit():
        if apply_profile(user, form):
            flash(Markup("<strong>{}</strong> has been updated").format(user.username))
        else:
            db.session.rollback()
    elif request.method == "POST":
        flash_form_errors(form)
    return render_template(
        "dashboard.html", header="Dashboard", form=form, user_id=user_id
    )


@user_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Logout route for the users."""
    logout_user()
    flash("User logged out successfully")
    return redirect("/users/login")


@user_bp.route("get_user/<int:user_id>/")
def get_user(user_id):
    """Get user."""
    user = db.get_or_404(User, user_id)
    if user is None:
        flash("User not found")
        return redirect("/users")
    return render_template("get_user.html", header="Get User", user=user)


@user_bp.route("/")
def users_all():
    """Users page."""
    users = User.query.all()
    return render_template("users_all.html", header="All Users", users=users)


@user_bp.route("/add", methods=["GET", "POST"])
def user_add():
    """Add user."""
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        conflict = find_conflict(username, email)
        if conflict:
            flash(conflict)
            return render_template("user_add.html", header="Add User", form=form)
        user = User(
            name=form.name.data.title().strip(),
            username=username,
            email=email,
            about_user=(form.about_user.data or "").strip(),
            password=form.password1.data.strip(),
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("That username or email is already in use")
            return render_template("user_add.html", header="Add User", form=form)
        flash(Markup("<strong>{}</strong> has been added").format(username))
        return redirect(url_for("user.login"))
    if request.method == "POST":
        flash_form_errors(form)
    return render_template("user_add.html", header="Add User", form=form)


@user_bp.route("/user/update/<int:user_id>/", methods=["GET", "POST"])
@login_required
def user_update(user_id):
    """Update user."""
    user = db.get_or_404(User, user_id)
    if not can_modify(user.id):
        flash("You can only change your own account")
        return redirect(url_for("user.users_all"))
    if user is None:
        flash("User not found")
        return redirect("/users")
    form = UserUpdateForm(obj=user)
    if form.validate_on_submit():
        if apply_profile(user, form):
            flash(Markup("<strong>{}</strong> has been updated").format(user.username))
            return redirect(url_for("user.users_all"))
    elif request.method == "POST":
        flash_form_errors(form)
    return render_template(
        "user_update.html", header="Update User", form=form, user_id=user_id
    )


@user_bp.route("/user/delete/<int:user_id>/", methods=["POST"])
@login_required
def user_delete(user_id):
    """Delete user."""
    user = db.get_or_404(User, user_id)
    if not can_modify(user.id):
        flash("You can only delete your own account")
        return redirect(url_for("user.users_all"))
    if user is None:
        flash("User not found")
        return redirect("/users")
    if user.is_admin and User.query.filter_by(is_admin=True).count() == 1:
        flash("The last admin account cannot be deleted")
        return redirect(url_for("user.users_all"))
    # Cascades to the books and posts the user owns
    db.session.delete(user)
    db.session.commit()
    flash(Markup("<strong>{}</strong> has been deleted").format(user.username))
    return redirect("/users")
