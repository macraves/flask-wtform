"""book related routes."""
from markupsafe import Markup
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from permissions import can_modify, flash_form_errors
from sqlalchemy import asc, desc, func
from allwebforms import BookForm, BookUpdateForm, SearchForm
from data_models import db, Book, Author
from book.book_api import find_cover_url


# Create blueprints connection
book_bp = Blueprint("book", __name__, url_prefix="/books", template_folder="templates")


class BookError(Exception):
    """book error."""

    def __init__(self, message):
        """Store the error message.

        Args:
            message (str): Error description.
        """
        self.message = message


def reset_book_form(form):
    """Reset pos form."""
    form.title.data = ""
    form.author.data = ""
    form.isbn.data = ""
    form.publication_year.data = ""
    form.condition.data = ""
    form.rating.data = ""
    return form


@book_bp.route("/search", methods=["POST"])
def search():
    """Search book by title or author by name."""
    form = SearchForm(request.form)
    if not form.validate_on_submit():
        flash("Enter a search term")
        return redirect(url_for("index"))
    searched = form.searched.data.lower().strip()
    books = Book.query.filter(func.lower(Book.title).like(f"%{searched}%")).all()
    authors = Author.query.filter(func.lower(Author.name).like(f"%{searched}%")).all()
    return render_template(
        "search.html", searched=searched, books=books, authors=authors
    )


@book_bp.route("/get_book/<int:book_id>/")
def get_book(book_id):
    """Get book."""
    book = Book.query.get_or_404(book_id)
    if book is None:
        flash("book not found")
        return redirect("/")
    return render_template("get_book.html", book=book, book_id=book_id)


@book_bp.route("/", methods=["GET"])
def books_all():
    """Books page."""
    valid_sort_params = ["title", "author"]
    sort_param = request.args.get("sort")
    if sort_param in valid_sort_params:
        order_param = request.args.get("order", "asc")
        order_function = asc if order_param == "asc" else desc
        if sort_param == "author":
            # Bellow methods sometimes does not give the expected result
            # books = Book.query.order_by(order_function(Book.author_id.name)).all()
            books = (
                Book.query.join(Author)
                .order_by(order_function(getattr(Author, "name")))
                .all()
            )
        else:
            books = Book.query.order_by(order_function(getattr(Book, sort_param))).all()
    else:
        books = Book.query.all()
    return render_template("books_all.html", header="All Books", books=books)


@book_bp.route("/add", methods=["GET", "POST"])
@login_required
def book_add():
    """Add book."""
    if not current_user.is_authenticated:
        flash("You need to login first")
        return redirect(url_for("user.login"))
    form = BookForm()
    if form.validate_on_submit():
        author_name = form.author.data.title().strip()
        isbn = (form.isbn.data or "").strip()
        # query to checj author if exists
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.commit()
        try:
            book = Book(
                title=form.title.data.title().strip(),
                condition=(form.condition.data or "").lower().strip(),
                author=author,
                user_id=current_user.id,
                isbn=isbn,
                publication_year=form.publication_year.data,
                rating=form.rating.data if form.rating.data else 0,
                cover_url=find_cover_url(isbn),
            )

            db.session.add(book)
            db.session.commit()
            flash(Markup("<strong>{}</strong> has been added").format(form.title.data))
            form = reset_book_form(form)
        except BookError:
            flash("Operation failed during the add process")
        except ValueError:
            flash("Rating must be float between 0 and 5.")
    elif request.method == "POST":
        flash_form_errors(form)
    return render_template("book_add.html", header="Add book", form=form)


@book_bp.route("/book/update/<int:book_id>/", methods=["GET", "POST"])
@login_required
def book_update(book_id):
    """Update a book.

    Only title, publication year, rating and condition can change, so the ISBN
    and author are not part of the update form.
    """
    book = Book.query.get_or_404(book_id)
    if book is None:
        flash("book not found")
        return redirect("/books/all")
    if not can_modify(book.user_id):
        flash("You can only change your own books")
        return redirect(url_for("book.books_all"))
    form = BookUpdateForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data.title().strip()
        book.publication_year = form.publication_year.data
        book.rating = form.rating.data if form.rating.data is not None else 0
        book.condition = (form.condition.data or "").lower().strip()
        try:
            db.session.commit()
            flash(Markup("<strong>book ID: {}</strong> has been updated").format(book.id))
        except BookError:
            flash("Operation failed during the update process")
        return redirect(url_for("book.books_all"))
    if request.method == "POST":
        flash_form_errors(form)
    return render_template(
        "book_update.html", header="Update book", form=form, book_id=book_id
    )


@book_bp.route("/book/delete/<int:book_id>/", methods=["POST"])
@login_required
def book_delete(book_id):
    """Delete book."""
    book = Book.query.get_or_404(book_id)
    if book is None:
        flash("book not found")
        return redirect("/books")
    if not can_modify(book.user_id):
        flash("You can only delete your own books")
        return redirect(url_for("book.books_all"))
    flash(Markup("<strong>book ID: {}</strong> has been deleted").format(book.id))
    try:
        db.session.delete(book)
        db.session.commit()
    except BookError:
        flash("Operation failed during the delete process")
    return redirect("/books")
