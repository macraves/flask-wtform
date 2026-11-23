# Library App (learning project)

> **Frozen historical copy.** This folder is not receiving fixes. The bugs listed under Known limitations below were fixed in [`library_app_production`](../../library_app_production/readme.md), not here. Use that app.

A small Flask app for managing authors, books, blog-style posts and users, backed by SQLite. It is the development predecessor of the main app in [`library_app_production`](../../library_app_production/readme.md). It has the same CSRF, authorization and HTML-sanitising measures, but not that app's mandatory `SECRET_KEY` check: this one warns and falls back to a random key. Read that README for the detailed security and deployment story. This one only describes what is in this folder.

## Quick start

Tested on Python 3.12 with a fresh virtual environment. Python 3.14 failed: the pinned `SQLAlchemy==2.0.23` raises an `AssertionError` on import.

```powershell
cd db_app_api\library_app
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

The app then listens on <http://127.0.0.1:5000/>. On first start it creates `data/library.sqlite` next to `data_models.py` and runs `db.create_all()`. `.env` is loaded with `python-dotenv` at the top of `app.py`.

| Variable | Required | Effect |
| --- | --- | --- |
| `SECRET_KEY` | No | If empty, a random key is generated with a warning and sessions reset on every restart. |
| `RAPIDAPI_KEY` | No | Enables book cover lookup by ISBN (RapidAPI Book Cover API). Without it books are saved with no cover. |
| `FLASK_DEBUG` | No | Debug mode is on only when it equals `1`. |

## Routes

Each blueprint is mounted under its own prefix. "Login" means `@login_required`.

| Prefix | Route | Methods | Access |
| --- | --- | --- | --- |
| `/` | `/` | GET | public |
| `/` | `/date` | GET, POST | public, returns JSON date |
| `/authors` | `/`, `/get_author/<id>/` | GET | public |
| `/authors` | `/add` | GET, POST | login |
| `/authors` | `/update/<id>/` | GET, POST | admin only |
| `/authors` | `/delete/<id>/` | POST | admin only, also deletes the author's books |
| `/books` | `/`, `/get_book/<id>/` | GET | public (`/books/?sort=title\|author&order=asc\|desc`) |
| `/books` | `/search` | POST | public |
| `/books` | `/add` | GET, POST | login |
| `/books` | `/book/update/<id>/`, `/book/delete/<id>/` | GET/POST, POST | owner or admin |
| `/posts` | `/`, `/get_post/<id>/` | GET | public |
| `/posts` | `/search` | POST | public |
| `/posts` | `/add` | GET, POST | login |
| `/posts` | `/post/update/<id>/`, `/post/delete/<id>/` | GET/POST, POST | owner or admin |
| `/users` | `/`, `/get_user/<id>/` | GET | public |
| `/users` | `/add` | GET, POST | public (this is registration) |
| `/users` | `/login` | GET, POST | public |
| `/users` | `/logout` | POST | login |
| `/users` | `/dashboard` | GET, POST | login, edits your own profile |
| `/users` | `/admin` | GET | admin only |
| `/users` | `/user/update/<id>/`, `/user/delete/<id>/` | GET/POST, POST | the user themselves or admin |

Deletes, logout and both search endpoints accept POST only. A GET returns 405.

## Permissions

`permissions.py` defines the admin as the user with `id == 1`. `can_modify(owner_id)` is true for the record owner or the admin. Books are owned through `Book.user_id`, posts through `Post.author_id`.

## Security measures present

- CSRF protection on every POST through `CSRFProtect`. A missing or expired token redirects to `/` with a flash message. Delete and logout buttons are small POST forms carrying the token.
- Post content is rendered through a `sanitize_html` filter built on `nh3`. A test post containing `<script>` and an `onclick` attribute came back with both removed.
- Flash messages that include user input are built with `Markup(...).format(...)`, which escapes the inserted values.
- Passwords are stored with `werkzeug.security.generate_password_hash` (scrypt hashes in the test database) and checked with `check_password_hash`.
- Delete and logout are POST-only, and update/delete routes check ownership or admin status on the server.

## Structure

```text
library_app/
  app.py            app setup, CSRF, nh3 filter, blueprints, error handlers
  data_models.py    SQLAlchemy models: User, Author, Book, Post; MYSQL_URI
  allwebforms.py    Flask-WTF forms
  permissions.py    is_admin(), can_modify()
  book_api.py       RapidAPI cover lookup
  author/ book/ post/ user/   blueprint (aroutes.py etc.) plus templates
  templates/        base, navbar, index, shared macros
  static/css/       style.css
  requirements.txt
  .env.example
```

The stack is Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Login, Flask-WTF, Flask-CKEditor, Flask-Migrate and `nh3`, as pinned in `requirements.txt`.

## Known limitations

The crashes below were reproduced with the Flask test client on a copy of the code; the others were confirmed by reading the code.

- **Book update page crashes.** `BookForm.publication_year` is a `DateField` (`YYYY-MM-DD`, in `allwebforms.py`) but `Book.publication_year` is an integer column. The add form stores a date string such as `2000-01-01`, adding a bare year such as `1999` fails validation, and the update POST stores a bare year. Rendering a stored integer in the `DateField` then makes `GET /books/book/update/<id>/` return 500 with `'int' object has no attribute 'strftime'`. Books with no year load fine.
- **Unhandled errors return 500.** Registering a username or email that already exists raises an unhandled `IntegrityError`. The update routes and the dashboard read `request.form` directly and skip form validation, so a missing field such as `about_user` raises `AttributeError`.
- **Deleting a user orphans their records.** Their books and posts keep existing with the owner set to `NULL`, so only the admin can edit them afterwards.
- **Admin is hard-coded.** The admin is whoever has user id 1, and on a fresh database that is the first person to register at `/users/add`.
- **Migrations are not set up.** `Flask-Migrate` is initialised in `app.py`, but there is no `migrations/` folder. The schema comes only from `db.create_all()`.
- **Misleading name.** `MYSQL_URI` in `data_models.py` holds a SQLite path. There is no MySQL support.
- **Search crashes on bad input.** `POST /books/search` and `POST /posts/search` return 500 when the form is empty or fails validation, because the result variables are never assigned.
- **Post search has no UI.** The only search form (in the navbar) posts to the book search. The posts search route exists but no page links to it.
- **No tests.**
- **Not for production.** `python app.py` uses Flask's development server.

## License

MIT, see [LICENSE](../../LICENSE).
