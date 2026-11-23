# Library App

A Flask web application for managing authors, books and blog-style posts, with user accounts, search and optional book cover lookup by ISBN.

Status: the main project of this repository. It is a learning project and is not production-ready (see [Known limitations](#known-limitations)).

## What it does

- **Authors**: any logged-in user can add an author; only the admin can edit or delete one. Deleting an author also deletes that author's books.
- **Books**: logged-in users add books (title, author, ISBN, publication date, condition, rating from 0 to 5). If `RAPIDAPI_KEY` is set and an ISBN is entered, the cover URL is requested from the RapidAPI Book Cover API (`book/book_api.py`). Without the key, books are saved with no cover. The book list can be sorted by title or author.
- **Posts**: logged-in users write posts with a CKEditor rich-text field. HTML is sanitised when rendered.
- **Users**: registration, login, logout, a dashboard to edit your own profile, and an admin overview page.
- **Search**: the navbar search box posts to `/books/search`. A post content search also exists as a POST endpoint (`/posts/search`), but no page in the UI links to it.

## Security measures in the code

- **Authorization**: `permissions.py` provides `can_modify(owner_id)` (record owner or admin). It guards book, post and user update and delete. Author update and delete, and the `/users/admin` page, are admin only.
- **CSRF**: `CSRFProtect(app)` in `main.py` requires a token on every POST. Forms use `form.hidden_tag()`; the delete and logout buttons in `templates/_macros.html` include `csrf_token()`. A failed check is handled by a `CSRFError` handler that flashes a message and redirects to `/`.
- **XSS**: post content is passed through the `sanitize_html` Jinja filter (`nh3.clean`) wherever it is rendered. Flash messages that include user input are built with `Markup(...).format(...)`, which escapes the inserted value.
- **State-changing routes are POST only**: all delete routes and logout accept POST only (a GET returns 405).
- **Secrets from the environment**: `SECRET_KEY`, the database URI and `RAPIDAPI_KEY` are read from environment variables (loaded from `.env` by `python-dotenv`). The app raises `RuntimeError` at startup if `SECRET_KEY` is empty or unset.
- **Passwords**: stored as hashes using `werkzeug.security.generate_password_hash` with its defaults. With the pinned Werkzeug 3.1.6 this produced `scrypt:` hashes (checked), not PBKDF2. The plain password is never readable from the model.
- **Database access**: SQLAlchemy ORM through Flask-SQLAlchemy, with no hand-built SQL strings.

## Quick start

Tested on Python 3.12.6 on Windows. Python 3.14 does not work with the pinned dependencies (see [Known limitations](#known-limitations)), so create the virtual environment with Python 3.12 explicitly: on a machine where plain `python` is 3.14, `python -m venv .venv` builds a broken environment. Python 3.11 and macOS/Linux were not tested.

From the repository root, in PowerShell:

```powershell
cd library_app_production
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the printed value after `SECRET_KEY=` in `.env`, then start the app:

```powershell
python main.py
```

Open <http://127.0.0.1:5000/>. `main.py` starts Flask's built-in server on port 5000 with `debug=False`. On first start the app creates `data/library.sqlite` next to the code.

On macOS or Linux (not tested): `python3 -m venv .venv`, `source .venv/bin/activate`, `cp .env.example .env`.

The first account registered at `/users/add` gets user id 1 and is the admin (see [Known limitations](#known-limitations)).

## Configuration

Set these in `.env` (copy of `.env.example`) or in the process environment.

| Variable | Required | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Flask session and CSRF signing key. The app refuses to start without it. |
| `SQLALCHEMY_DATABASE_URI` | No | Database URL. Defaults to the SQLite file `data/library.sqlite`. A `postgres://` prefix is rewritten to `postgresql://` in `main.py`. |
| `RAPIDAPI_KEY` | No | Enables cover lookup by ISBN. Without it, new books get no cover. |

Generate a key with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

`.env` is for local use only and must not be committed.

## Routes

Blueprint prefixes are set in `main.py`. "Logged in" means `@login_required`; "owner or admin" means `can_modify`.

| Method | Path | Who |
| --- | --- | --- |
| GET | `/` | Anyone (overview of all content) |
| GET | `/date` | Anyone (returns the current date as JSON; POST is also accepted but needs a CSRF token) |
| GET | `/authors/`, `/authors/get_author/<id>/` | Anyone |
| GET, POST | `/authors/add` | Logged in |
| GET, POST | `/authors/update/<id>/` | Admin |
| POST | `/authors/delete/<id>/` | Admin |
| GET | `/books/`, `/books/get_book/<id>/` | Anyone |
| POST | `/books/search` | Anyone |
| GET, POST | `/books/add` | Logged in |
| GET, POST | `/books/book/update/<id>/` | Owner or admin |
| POST | `/books/book/delete/<id>/` | Owner or admin |
| GET | `/posts/`, `/posts/get_post/<id>/` | Anyone |
| POST | `/posts/search` | Anyone |
| GET, POST | `/posts/add` | Logged in |
| GET, POST | `/posts/post/update/<id>/` | Owner or admin |
| POST | `/posts/post/delete/<id>/` | Owner or admin |
| GET | `/users/`, `/users/get_user/<id>/` | Anyone (these pages show user emails, see Known limitations) |
| GET, POST | `/users/add` | Anyone (registration) |
| GET, POST | `/users/login` | Anyone |
| POST | `/users/logout` | Logged in |
| GET, POST | `/users/dashboard` | Logged in (own account) |
| GET, POST | `/users/user/update/<id>/` | Owner or admin |
| POST | `/users/user/delete/<id>/` | Owner or admin |
| GET | `/users/admin` | Admin |

## Project structure

```text
library_app_production/
├── main.py              # app setup, CSRF, sanitiser filter, blueprints, error handlers
├── permissions.py       # is_admin(), can_modify()
├── data_models.py       # User, Author, Book, Post (SQLAlchemy models)
├── allwebforms.py       # Flask-WTF forms
├── author/ book/ post/ user/   # one blueprint each: routes + templates
│   └── book/book_api.py        # RapidAPI cover lookup
├── templates/           # base, navbar, index, shared macros
├── static/css/
├── requirements.txt
├── Procfile
└── .env.example
```

Architecture notes:

- Each feature is a Flask blueprint (`author_bp`, `book_bp`, `post_bp`, `user_bp`) registered with a URL prefix in `main.py`.
- Authorization logic lives in one module, `permissions.py`, and the routes call it.
- Models are in `data_models.py`; forms are in `allwebforms.py`.
- `main.py` loads `.env` before importing the app modules, because `book_api.py` reads `RAPIDAPI_KEY` at import time.

## Deployment

The `Procfile` contains `web: gunicorn main:app`. No deployment has been done or verified. Gunicorn was installed but not run (I tested on Windows). Running `python main.py` is the only start method I tested.

A deploy would need at least:

- `SECRET_KEY` set in the host's environment, and `SQLALCHEMY_DATABASE_URI` for a hosted database.
- A database driver for that database. `requirements.txt` has no PostgreSQL or MySQL driver (for example `psycopg2`), so the app would fail to connect to Postgres until one is added.
- A fix for the `password_hash` column length before using a stricter database than SQLite (see [Known limitations](#known-limitations)).
- A decision on migrations, because the schema is created with `db.create_all()`.

## Testing

This app has no automated test suite. I searched the app directory for test files and found none.

## Known limitations

These were checked in the code. Where a limitation says "confirmed", I reproduced it by running the app; the others are read from the code.

- **Python 3.14 fails.** With the pinned `SQLAlchemy==2.0.25`, `import main` raised an `AssertionError` in SQLAlchemy on Python 3.14.2. The same requirements installed and ran on Python 3.12.6.
- **Book update page crashes for books with a publication year.** `BookForm.publication_year` is a `DateField` (`allwebforms.py:51`) but the model column is an `Integer` (`data_models.py:78`). On SQLite a date entered in the add form is stored as text such as `1965-01-01`, and `/books/book/update/<id>/` then fails with `'str' object has no attribute 'strftime'`. The update POST stores a bare year, which becomes an integer, and the page then fails with `'int' object has no attribute 'strftime'`. Books with no year load fine.
- **Book add requires a full date** (`YYYY-MM-DD`) in the "Publication Year" field because of the same `DateField`.
- **Admin is hard-coded** as user id 1 (`permissions.py:5`). Registration is open, so whoever registers first is the admin.
- **Empty search crashes.** Submitting an empty search to `/books/search` or `/posts/search` raises `UnboundLocalError` (`book/broutes.py:61`, `post/proutes.py:41`) and returns the 500 page. Confirmed on both `/books/search` and `/posts/search`.
- **Password column too short.** `password_hash` is `String(128)` (`data_models.py:34`) but the scrypt hash produced is 162 characters. SQLite does not enforce the length; databases that do (such as PostgreSQL) would reject it. Not tested on another database.
- **No migrations.** Flask-Migrate is initialised in `main.py`, but there is no `migrations/` folder, and `db.create_all()` runs at every start.
- **Misnamed variable.** `MYSQL_URI` in `data_models.py` holds a SQLite path.
- **Missing form fields crash the add routes.** Registration without an `about_user` field and book add without a `condition` field raise `AttributeError` (`NoneType` has no `strip` or `lower`). A browser always sends these fields, so this only affects hand-built requests.
- **Author add requires both dates.** `AuthorForm` has no `Optional()` on `birth_date` or `death_date` (`allwebforms.py:40-41`), so an empty date is rejected and the author is not created (confirmed). A living author can only be created through the book form, which creates missing authors.
- **Duplicate username or email returns 500.** Registering a username that already exists raises an unhandled `IntegrityError` (confirmed; `user/uroutes.py`). The dashboard and user update routes have the same gap.
- **User emails are public.** `/`, `/users/` and `/users/get_user/<id>/` show every user's email to anonymous visitors (confirmed on `/` and `/users/`).
- **Update routes skip validation.** The book, post and user update routes read `request.form` directly after the form check, so, for example, a book rating of 9 raises an uncaught `ValueError` and returns 500 (confirmed for books).
- **Cover lookup failures break book add.** With `RAPIDAPI_KEY` set and an ISBN entered, `get_book_cover_url` raises on any non-200 reply (`book/book_api.py`), and `book_add` catches only `BookError` and `ValueError`, so an API failure should return 500. Read from the code; not run, because no key was available.
- **No password change or reset.** The dashboard and update forms do not touch the password (read from the code).
- **Dead code.** The `/books/get_book_recommendation` route is commented out, `AIForm` and `book/templates/recommendation.html` are unused, and `book_api.py` contains an unused `send_request_to_openai` function that calls a different RapidAPI service.
- **Deprecated APIs.** The code uses `datetime.utcnow` and `Query.get`.

## License

MIT. See [LICENSE](../LICENSE).
