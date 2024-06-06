"""Creating Post Form with Flask-WTF"""

from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField


class BlogForm(FlaskForm):
    """docs"""

    author = StringField("Author", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")
