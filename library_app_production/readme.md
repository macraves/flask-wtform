# Library App

A Flask web application for managing authors, books and blog-style posts, with user accounts, search and optional book cover lookup by ISBN.

Status: the main project of this repository. It is a learning project and is not production-ready (see [Known limitations](#known-limitations)).

## What it does

- **Authors**: any logged-in user can add an author; only the admin can edit or delete one. Deleting an author also deletes that author's books.
- **Books**: logged-in users add books (title, author, ISBN, publication year, condition, rating from 0 to 5). If `RAPIDAPI_KEY` is set and an ISBN is entered, the cover URL is requested from the RapidAPI Book Cover API (`book/book_api.py`). Without the key, or when the lookup fails or times out, the book is saved with no cover. The book list can be sorted by title or author.
- **Posts**: logged-in users write posts with a CKEditor rich-text field. HTML is sanitised when rendered.
- **Users**: registration, login, logout, a dashboard to edit your own profile, and an admin overview page. Email addresses are shown only to the account owner and to admins. Deleting an account also deletes the books and posts that user owns; the last admin account cannot be deleted.
- **Search**: the navbar search box posts to `/books/search`. A post content search also exists as a POST endpoint (`/posts/search`), but no page in the UI links to it.

## Security measures in the code

- **Authorization**: `permissions.py` provides `can_modify(owner_id)` (record owner or admin). Admin is the `is_admin` flag on the user, never granted by registration (see [Quick start](#quick-start)). It guards book, post and user update and delete. Author update and delete, and the `/users/admin` page, are admin only.
- **CSRF**: `CSRFProtect(app)` in `main.py` requires a token on every POST. Forms use `form.hidden_tag()`; the delete and logout buttons in `templates/_macros.html` include `csrf_token()`. A failed check is handled by a `CSRFError` handler that flashes a message and redirects to `/`.
- **XSS**: post content is passed through the `sanitize_html` Jinja filter (`nh3.clean`) wherever it is rendered. Flash messages that include user input are built with `Markup(...).format(...)`, which escapes the inserted value; all other flashes are plain strings that Jinja autoescapes.
- **State-changing routes are POST only**: all delete routes and logout accept POST only (a GET returns 405).
- **Secrets from the environment**: `SECRET_KEY`, the database URI and `RAPIDAPI_KEY` are read from environment variables (loaded from `.env` by `python-dotenv`). The app raises `RuntimeError` at startup if `SECRET_KEY` is empty or unset.
- **Passwords**: stored as hashes using `werkzeug.security.generate_password_hash` with its defaults. With the pinned Werkzeug 3.1.6 this produced `scrypt:` hashes (checked), not PBKDF2. The plain password is never readable from the model.
- **Database access**: SQLAlchemy ORM through Flask-SQLAlchemy, with no hand-built SQL strings.

## Quick start

Tested on Python 3.12.6 and 3.14.2 on Windows (the test suite passes on both with the pinned requirements). CI runs Python 3.12. Python 3.11 and macOS/Linux were not tested.

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

Register an account at `/users/add`, then make it an admin from the command line (registration never grants admin):

```powershell
flask --app main make-admin <username>
```

**Upgrading an existing database.** `db.create_all()` creates missing tables but does not alter existing ones, and there are no migrations. A database created by an earlier version needs the new column added by hand, then promote the old admin (user id 1):

```sql
ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0;
UPDATE users SET is_admin = 1 WHERE id = 1;
```

The `ALTER` statement was run against a SQLite table; it was not run on PostgreSQL. SQLite ignores the widened `password_hash` length. On PostgreSQL also run `ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(256);` (not tested). Books saved by an earlier version may hold a date string such as `1965-01-01` in `publication_year`; those rows still display and can be fixed by updating the book.

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
| GET | `/users/`, `/users/get_user/<id>/` | Anyone (emails are shown only to the owner and admins) |
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
├── permissions.py       # is_admin(), can_modify(), flash_form_errors()
├── data_models.py       # User, Author, Book, Post (SQLAlchemy models)
├── allwebforms.py       # Flask-WTF forms
├── author/ book/ post/ user/   # one blueprint each: routes + templates
│   └── book/book_api.py        # RapidAPI cover lookup
├── templates/           # base, navbar, index, shared macros
├── static/css/
├── tests/               # pytest suite
├── requirements.txt
├── requirements-dev.txt # runtime requirements plus pytest
├── pytest.ini
├── Procfile
└── .env.example
```

Architecture notes:

- Each feature is a Flask blueprint (`author_bp`, `book_bp`, `post_bp`, `user_bp`) registered with a URL prefix in `main.py`.
- Authorization logic lives in one module, `permissions.py`, and the routes call it.
- Models are in `data_models.py`; forms are in `allwebforms.py`.
- `main.py` loads `.env` before importing the app modules, because `book_api.py` reads `RAPIDAPI_KEY` at import time.
- The `data/` folder is created only when `SQLALCHEMY_DATABASE_URI` is unset, not when a module is imported.

## Deployment

The `Procfile` contains `web: gunicorn main:app`. No deployment has been done or verified. Gunicorn was installed but not run (I tested on Windows). Running `python main.py` is the only start method I tested.

A deploy would need at least:

- `SECRET_KEY` set in the host's environment, and `SQLALCHEMY_DATABASE_URI` for a hosted database.
- A database driver for that database. `requirements.txt` has no PostgreSQL or MySQL driver (for example `psycopg2`), so the app would fail to connect to Postgres until one is added.
- A plan for schema changes: the schema is created with `db.create_all()` and there are no migrations (see [Known limitations](#known-limitations)).

## Testing

From `library_app_production`, in PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest
```

88 tests passed on Python 3.14.2 (the earlier 84 also passed on 3.12.6; the 4 added for wildcard search were not run on 3.12 locally, CI runs 3.12). They use a temporary SQLite file and a test secret key, mock all network calls, and need no `.env`. They cover authorization (owner, other user, admin, anonymous), CSRF and method rules, HTML sanitising and escaping, rendering of every page, and one regression test per bug fixed. The tests were written alongside the fixes, so they were not run against the old code to show them failing first. GitHub Actions runs the same command on Python 3.12 (`.github/workflows/tests.yml` at the repository root).

## Known limitations

These were checked in the code. Where a limitation says "confirmed", I reproduced it by running the app; the others are read from the code.

- **Admin must be set from the command line.** There is no admin UI for promoting or demoting users, only `flask --app main make-admin <username>`.
- **No migrations.** Flask-Migrate was removed because it was initialised but never used (there was no `migrations/` folder). `db.create_all()` runs at every start and does not alter existing tables, so schema changes to an existing database are manual (see the upgrade note in [Quick start](#quick-start)).
- **No database driver for PostgreSQL or MySQL** in `requirements.txt`, although `main.py` rewrites `postgres://` to `postgresql://`. Only SQLite was run.
- **Legacy date-string years.** Rows written by an earlier version may hold a date string in `publication_year`. They display and update fine, but the column is typed as an integer and SQLite does not enforce that.
- **Posts are sanitised when rendered, not when stored.** Raw HTML is kept in the database.
- **No password change or reset.** The dashboard and update forms do not touch the password (read from the code).
- **Python versions.** SQLAlchemy 2.0.31 is the lowest 2.0 release that imports on Python 3.14 (2.0.30 and older failed; checked by installing each).

## License

MIT. See [LICENSE](../LICENSE).
