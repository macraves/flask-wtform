"""MasterBlog Form app by Flask."""

import os
import secrets

from flask import Flask
from blogs_routes import posts


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

app.register_blueprint(posts, url_prefix="/")


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=5000,
    )
