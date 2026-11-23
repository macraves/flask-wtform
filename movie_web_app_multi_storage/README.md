# Movie Web App with Multi-Storage

Learning project: a Flask movie-list app where each user chooses, at signup, whether their data lives in SQLite, a JSON file or CSV files. Movie details come from the OMDb API. This is a learning project, not a production application.

## Variants

| Folder | What it is | Status |
| --- | --- | --- |
| `moviewebapp_latest/` | Flask-Login frontend, reviews (SQLite only), separate JSON REST API | The one to run |
| `using session/` | Earlier version using only the Flask session | Partly broken, see Known limitations |

All commands below are PowerShell and are run from `moviewebapp_latest/` unless stated otherwise.

## Setup

`requirements.txt` pins every package the code imports (pandas is only needed by `moviewebapp_latest`, for CSV storage). I installed it into a fresh Python 3.12 virtual environment (`.python-version` pins 3.12, and CI uses it) and confirmed that `moviewebapp_latest` (frontend and API) and `using session` (frontend) import without errors; I did not run the servers for this check.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
```

Copy `../.env.example` to `.env` in the project folder (`movie_web_app_multi_storage/`) and fill it in. The code loads `.env` with python-dotenv.

| Variable | Needed for |
| --- | --- |
| `OMDB_API_KEY` | Required to add movies. Without it, adding a movie fails with the error `OMDB_API_KEY environment variable is not set`. Free key: <https://www.omdbapi.com/apikey.aspx> |
| `SECRET_KEY` | Optional. If unset, the app warns and uses a random key, so sessions reset on every restart. |

## Run the frontend

```powershell
python main.py
```

Open <http://127.0.0.1:5000>. Set `FLASK_DEBUG=1` to enable debug mode (`$env:FLASK_DEBUG = "1"`). Data is created on first run under `data/` (and `registry/` for JSON users); both are created inside `moviewebapp_latest/`.

Sign up with a name, username, a non-empty email (the label says "Optinal", but the field is required), password, a confirm-password field and a storage type typed into a text box (`csv`, `json` or `sqlite`). Sign in also asks for the storage type, because the app has no global user table: it looks the user up in the storage you name.

## Run the REST API

`backend/backend_api.py` is a separate Flask app from the frontend. Run directly it uses Flask's default port 5000, the same as the frontend, so the two cannot run side by side on defaults. I ran it on another port with the Flask CLI and logged in successfully:

```powershell
python -m flask --app backend.backend_api run --port 5001
```

The API only works with SQLite users, and shares `data/movies.db` with the frontend. Authentication is a session cookie set by `POST /api/login`, so clients must keep cookies (for example `requests.Session`).

| Method and path | Auth | Behaviour |
| --- | --- | --- |
| `POST /api/login` | none | JSON `username`, `password`, `storage`. Only `"sqlite"` is accepted; other values return an error message (with HTTP 200). Wrong credentials return 401. |
| `POST /api/user/add` | none | Creates an SQLite user from JSON (`name`, `username`, `email`, `password`). |
| `GET /api/users` | login | Lists all users (`id`, `name`, `username`, `email`). |
| `PUT /api/user-update/<id>` | login, own id only | Others get 403. Body must be a JSON object with only `name`, `username`, `email`, `password`; unknown fields return 400. `password` is the user's current password and is required: missing, non-string or an empty body `{}` returns 400, a wrong password returns 403, a duplicate username returns 409 (all JSON errors). Only `name`, `username` and `email` are changed; the stored password is not. |
| `DELETE /api/user-delete/<id>` | login, own id only | Others get 403. Takes the user's `password` in the JSON body; a missing or invalid body returns 400 and a wrong password returns 403 (JSON errors). |
| `GET /api/users/<id>/movies` | login | Returns that user's movies (`id`, `Title`, `Year`, `Rate`). Any logged-in user can read any user's list; there is no ownership check here. |
| `POST /api/movies/add` | login | JSON `title`; looks it up on OMDb and adds it to the logged-in user's list. |

Unauthenticated calls to login-protected routes are redirected (302) to the login route rather than answered with 401.

## Frontend routes (`moviewebapp_latest`)

| Route | Notes |
| --- | --- |
| `/`, `/signup`, `/signin`, `/signout` | Home and account flow |
| `/movies`, `/movies/add` | Own list; add by title via OMDb |
| `/dashboard`, `/users` | Own movies; all registered users in the current storage |
| `/users/<id>/movies`, `/user/<id>/movie/<id>/info` | View a user's list or one movie. The list route has no ownership check but its template shows "Not authorized access" to non-owners; the movie info page has no check and shows another user's movie |
| `/users/<id>/update_movie/<id>`, `/users/<id>/delete_movie/<id>` | Edit or delete a movie (owner only). Delete is POST-only with a CSRF token; a GET returns 405 |
| `/user-update/<id>`, `/user-delete/<id>` | Edit or delete the account (owner only, password re-entered) |
| `/add_review/movie/<id>`, `/all-reviews` | Reviews, SQLite storage only. Both need login (anonymous users are redirected to sign in); JSON and CSV users see a message instead of reviews |

## Storage

All three backends implement `DataManagmentInterface` (spelled this way in the code, in `datamanagement/storage_inheritance.py`), which declares only `get_all_users` and `get_user_movies` as abstract. The concrete classes are `SqliteStorage`, `JsonStorage` and `CsvStorage`, each with its own error class (`SqliteErrors`, `JsonStorageErrors`, `CsvStorageErrors`).

| Backend | File | Layout |
| --- | --- | --- |
| SQLite | `data/movies.db` | Tables `users` (`id`, `name`, `username`, `email`, `date_added`, `password_hash`), `movies` (`id`, `Title`, `Year`, `imdbRating`, `Poster`, `user_id`), `reviews` (`id`, `user_id`, `movie_id`, `review_text`) |
| JSON | `data/movies.json` | `{"version": 1.0, "users": {"<id>": {id, name, username, email, password, movies: [...]}}}`; `password` holds a hash |
| CSV | `data/users.csv`, `data/movies.csv` | users: `id,name,username,email,password,movies`; movies: `id,Title,Year,imdbRating,Poster,user_id` |

Movie records keep the OMDb key names `Title`, `Year`, `imdbRating` and `Poster`.

## Security

Present:

- Passwords are hashed (Werkzeug) in all three data stores.
- Most pages use `@login_required` (unauthenticated requests are redirected to sign in). Exceptions: home, signup and signin.
- Account edit and delete, and movie edit and delete, check that the URL's user id is the logged-in user (403 otherwise). The API checks the same for update and delete.
- The HTML forms are Flask-WTF forms with CSRF tokens, and the frontend app has `CSRFProtect` on; a sign-in POST or a movie delete POST without a token is not accepted (400).
- `SECRET_KEY` and `OMDB_API_KEY` come from the environment; `.env` is not committed.

Absent or weak:

- The JSON API has no CSRF protection and relies on a session cookie.
- `/signout` is a GET link, so a cross-site page can sign a user out.
- `/user/<id>/movie/<id>/info`, `/users` (names), `/api/users` and `/api/users/<id>/movies` let any logged-in user read other users' data (the `/users/<id>/movies` page hides the list in its template, but the route itself has no check).
- The registry file `registry/registry.json` now gets a password hash for new signups. A file written before this fix still holds plain-text passwords until it is removed or the user is created again; nothing rewrites it.
- No rate limiting, no HTTPS; the dev server is used.

## Tests

`moviewebapp_latest/tests/` holds 34 pytest tests (reviews, passwords, API errors, movie delete, `using session` import). They use temporary data files only and stub the OMDb call. From `moviewebapp_latest/`:

```powershell
pip install -r ..\requirements.txt pytest
python -m pytest tests -q -W ignore
```

GitHub Actions runs them on every pull request and on pushes to `main` (the `movie-app` job in `.github/workflows/tests.yml`, Python from `.python-version`). `test_backend.py` is not an automated test; it is an interactive menu script for manual API checks. It needs the API running on port 5000 (it hardcodes `http://127.0.0.1:5000`) and an SQLite user `admin` with password `123`, which nothing in the code creates. It starts its menu at import time (`main()` is called at module level). Its add-movie check posts keys `Title`/`Year`/... while the API reads `title`.

## Known limitations

- Reviews work only with SQLite storage; JSON and CSV users get a message on `/all-reviews` and have no review pages.
- The navbar search box is a form with no `action` and no backend route.
- The API supports SQLite users only; the API and the frontend both default to port 5000.
- The storage type is typed free-form at signup and sign-in. A typo at signup shows a validation message; at sign-in it raises a 500 error page.
- In JSON and CSV storage, ids come from list lengths (movies in JSON, users in CSV), so deleting and then adding can create duplicate ids; in CSV storage a duplicate user id then makes `get_all_users` drop one of the two users.
- `using session/` is an older variant:
  - `backend/user_app.py` now imports (it used the wrong module name and called `JsonStorage()` with no argument), but it is still broken beyond that: `/users` raises a `TypeError` once any user exists, and `/add_user` calls `User.get_id`, which does not exist.
  - Its frontend (`python main.py` from that folder) runs. SQLite and JSON signup and sign-in worked here (sign-in uses the `name` field); CSV signup returns HTTP 500 because `CsvStorage` has no `add_new_user`, and CSV sign-in returns 500 too.
  - It stores passwords in plain text: the SQLite `users.password` column, the JSON storage file and `registry/registry.json`.

## License

MIT, see [LICENSE](../LICENSE).
