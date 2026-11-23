"""Html form objects for flask app."""

from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Optional
from wtforms import (
    DateField,
    FloatField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
)
from data_models import MAX_PUBLICATION_YEAR, MIN_PUBLICATION_YEAR


class SearchForm(FlaskForm):
    """Search box in the navbar."""

    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AuthorForm(FlaskForm):
    """Author row properties. Birth and death dates are optional."""

    name = StringField("Name", validators=[DataRequired()])
    birth_date = DateField("Birth Date", format="%Y-%m-%d", validators=[Optional()])
    death_date = DateField("Death Date", format="%Y-%m-%d", validators=[Optional()])
    submit = SubmitField("Submit")


class BookUpdateForm(FlaskForm):
    """Fields of a book that can be changed after it was added."""

    title = StringField("Title", validators=[DataRequired()])
    publication_year = IntegerField(
        "Publication Year",
        validators=[
            Optional(),
            NumberRange(min=MIN_PUBLICATION_YEAR, max=MAX_PUBLICATION_YEAR),
        ],
    )
    condition = StringField("Condition", validators=[Optional()])
    rating = FloatField("Rating", validators=[Optional(), NumberRange(min=0, max=5)])
    submit = SubmitField("Submit")


class BookForm(BookUpdateForm):
    """Book row properties for adding a book."""

    author = StringField("Author", validators=[DataRequired()])
    isbn = StringField("ISBN", validators=[Optional()])


class LoginForm(FlaskForm):
    """Username and password of a registered user."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    """Email and password pair."""

    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    """Blog post written with the rich-text editor."""

    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserUpdateForm(FlaskForm):
    """Profile fields a user can change. The password is not part of it."""

    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    about_user = StringField("About User", validators=[Optional()])
    submit = SubmitField("Submit")


class UserForm(UserUpdateForm):
    """Registration form: the profile fields plus a confirmed password."""

    password1 = PasswordField(
        "password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must be matched"),
        ],
    )
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
