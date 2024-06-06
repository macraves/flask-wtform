"""MasterBlog Form app by Flask"""

from flask import Flask
from blogs_routes import posts


app = Flask(__name__)
app.config["SECRET_KEY"] = "blog post"

app.register_blueprint(posts, url_prefix="/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
