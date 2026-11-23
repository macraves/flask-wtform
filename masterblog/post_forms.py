"""Creating Post Form with Flask-WTF"""

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, TextAreaField


class BlogForm(FlaskForm):
    """docs"""

    author = StringField("Author", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")
