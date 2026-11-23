"""SQLAlchemy data models for the library app.

ORM objects, their relationships and the rules the database layer enforces.
"""

import os
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin, UserMixin


script_root = os.path.dirname(os.path.realpath(__file__))
data_folder_root = os.path.join(script_root, "data")

# Used only when SQLALCHEMY_DATABASE_URI is not set (see default_database_uri)
SQLITE_URI = f"sqlite:///{data_folder_root}/library.sqlite"

MIN_PUBLICATION_YEAR = 1
MAX_PUBLICATION_YEAR = 2100

db = SQLAlchemy()


def default_database_uri():
    """Create the local data folder and return the default SQLite URI.

    The folder is created here, not at import time, so importing this module
    has no side effects on the file system.

    Returns:
        str: SQLAlchemy URI of the local SQLite file.
    """
    os.makedirs(data_folder_root, exist_ok=True)
    return SQLITE_URI


def utcnow():
    """Return the current UTC time as a naive datetime.

    Replaces the deprecated ``datetime.utcnow`` and keeps the stored values
    naive, as they were before.

    Returns:
        datetime: Current UTC time without tzinfo.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AnonymousUser(AnonymousUserMixin):
    """Logged-out visitor. Never an admin, so templates can test is_admin."""

    is_admin = False


class User(db.Model, UserMixin):
    """A registered user, who owns many books and posts."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    about_user = db.Column(db.String(100), nullable=True)
    added_date = db.Column(db.DateTime, default=utcnow)
    # werkzeug scrypt hashes are 162 characters long
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(
        db.Boolean, nullable=False, default=False, server_default=db.false()
    )
    # Deleting a user deletes the books and posts they own
    books = db.relationship(
        "Book", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    posts = db.relationship(
        "Post", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def password(self):
        """Block reading the password.

        Raises:
            AttributeError: Always; only the hash is stored.
        """
        raise AttributeError("password is not a readable attribute!!!")

    @password.setter
    def password(self, password):
        """Hash and store a new password.

        Args:
            password (str): Plain text password.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check a plain text password against the stored hash.

        Args:
            password (str): Plain text password.

        Returns:
            bool: True when the password matches.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """Return a readable summary of the user."""
        return f"Name: '{self.name}', Email: '{self.email}', Added: '{self.added_date}'"


class Author(db.Model):
    """An author, who can write many books."""

    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.DateTime, nullable=True)
    death_date = db.Column(db.DateTime, nullable=True)
    added_date = db.Column(db.DateTime, default=utcnow)
    books = db.relationship("Book", backref="author", lazy=True)


class Book(db.Model):
    """A book with one author, added by one user."""

    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(100), nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    added_date = db.Column(db.DateTime, default=utcnow)
    cover_url = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    @validates("rating")
    def validate_rating(self, key, rating):
        """Check that the rating is between 0 and 5.

        Args:
            key (str): Column name, supplied by SQLAlchemy.
            rating (float): Rating to store.

        Returns:
            float: The validated rating.

        Raises:
            ValueError: If the rating is out of range.
        """
        if not 0 <= float(rating) <= 5:
            raise ValueError("Rating must be between 0 and 5.")
        return rating

    @validates("publication_year")
    def validate_publication_year(self, key, year):
        """Only whole years may reach the integer column.

        Args:
            key (str): Column name, supplied by SQLAlchemy.
            year (int | None): Year to store.

        Returns:
            int | None: The validated year.

        Raises:
            ValueError: If the value is not an integer year in range.
        """
        if year is None:
            return None
        if isinstance(year, bool) or not isinstance(year, int):
            raise ValueError("Publication year must be a whole number.")
        if not MIN_PUBLICATION_YEAR <= year <= MAX_PUBLICATION_YEAR:
            raise ValueError(
                f"Publication year must be between {MIN_PUBLICATION_YEAR} "
                f"and {MAX_PUBLICATION_YEAR}."
            )
        return year

    def __repr__(self) -> str:
        """Return a readable summary of the book."""
        return f"Book('{self.title}', '{self.author}', '{self.added_date}')"


# Create a Blog Post Model
class Post(db.Model):
    """A blog post written by one user."""

    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    added_date = db.Column(db.DateTime, default=utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Large text
    content = db.Column(db.Text, nullable=False)

    def __repr__(self) -> str:
        """Return a readable summary of the post."""
        return f"Blog Post('{self.title}', '{self.subtitle}', '{self.added_date}')"
