"""Frontend application entry point."""
import os

from frontend.frontend_app import app


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
