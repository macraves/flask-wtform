# Flask & Python Projects

Eight small projects from my path into Python backend development: Flask web apps and APIs, SQLAlchemy models, and command-line tools. They are learning projects, not production systems. This page says what each one contains and where the rough edges are.

## Flagship

**[library_app_production](./library_app_production)** is the project to look at first: a Flask app for authors, books and posts with user accounts, owner-or-admin authorization, CSRF protection, sanitised rich-text input, and configuration through environment variables. Its README lists exactly what it does, how to run it, and its known limitations. It has a pytest suite (84 tests) that runs in GitHub Actions, and it has not been deployed.

## Other projects

These are learning exercises. Each README says so and lists its known limitations.

| Project | What it is | Built with | Tests |
| --- | --- | --- | --- |
| [Best-Buy](./Best-Buy) | Store inventory CLI: three product types, three promotion types, a shopping cart and order totals | Python, `unittest` | 20 unit tests |
| [backend_api](./backend_api) | Blog post REST API (list, search, add, update, delete) with a small Flask front end | Flask, Flask-CORS, Faker | none |
| [masterblog](./masterblog) | Blog with create, read, update, delete and like, storing posts in a JSON file | Flask, WTForms, CKEditor | 15 pytest tests, CI |
| [movie_web_app_multi_storage](./movie_web_app_multi_storage) | Movie collection app whose users choose SQLite, JSON or CSV storage, with a JSON API | Flask, SQLAlchemy, Flask-Login, OMDb API | manual script |
| [storage-app-user](./storage-app-user) | Command-line movie collection manager using the OMDb API | Python, Requests | none |
| [data_scientist](./data_scientist) | Flight delay analysis. It now lives in its own repository: [flight-data-analysis](https://github.com/macraves/flight-data-analysis) | SQLAlchemy, matplotlib, seaborn, folium, Flask | in the new repo |

Each project has its own `requirements.txt` and README. Entry points: `Best-Buy/main.py`, `masterblog/app.py`, `library_app_production/main.py`, `storage-app-user/movie_user_app.py`, `movie_web_app_multi_storage/moviewebapp_latest/main.py`, and for the blog API `backend_api/FLASK-APIs/backend/backend_app.py`.

## What the code shows

- **Storage behind an interface.** `movie_web_app_multi_storage` defines an abstract `DataManagmentInterface` (in `datamanagement/storage_inheritance.py`) with separate SQLite, JSON and CSV managers. The app picks one when the user logs in.
- **Flask Blueprints.** The library app splits authors, books, posts and users into four Blueprints, each with its own routes and templates.
- **Authentication.** Flask-Login handles sessions in the library and movie apps.
- **Parameterised queries.** The flight analysis project passes values to SQL as bound parameters, and its tests check an injection-style input.
- **Object-oriented design.** `Best-Buy` uses an abstract promotion base class with percentage-discount, second-half-price and third-one-free subclasses.
- **Authorization and web security.** The library apps check owner-or-admin rights in one module (`permissions.py`), require a CSRF token on every POST, sanitise rich-text post content with `nh3`, and accept only POST for deletes and logout. The movie apps check that users can only change their own accounts and movies.
- **Environment-based config.** No API key or secret is hard-coded: `SECRET_KEY` and the OMDb and RapidAPI keys come from environment variables or a local `.env` (each project that needs one ships a `.env.example`). `library_app_production` refuses to start without `SECRET_KEY`; the other Flask apps warn and fall back to a random key. Its `Procfile` runs `gunicorn main:app`, which I have not deployed.
- **Documentation habits.** A script I ran over the repo counted 571 functions: 86% have a docstring and 27% have type hints.

## Known gaps

I would rather list these than have a reviewer find them.

- **Testing is thin outside the flagship.** `library_app_production` has 84 pytest tests and `Best-Buy` has 20 unit tests. The movie app's `test_backend.py` is a manual script that needs the server running. The other Flask apps, including the frozen `db_app_api/library_app`, have no tests.
- **Admin in the flagship is a single flag.** `library_app_production` has an `is_admin` column set with `flask --app main make-admin <username>`; there are no finer roles. The frozen `db_app_api/library_app` still hard-codes user id `1` as the admin.
- **Known bugs are documented, not all fixed.** `db_app_api/library_app` (frozen) still crashes on the book update page and on an empty search, and has the other flagship bugs that were fixed; the movie app's add-review route returns 500; `backend_api` never sorts by title or content. Each project README lists its own bugs with the file and line.
- **Python version.** The flagship pins SQLAlchemy 2.0.31 and passes its tests on Python 3.12 and 3.14. `db_app_api/library_app` pins a release that does not import on Python 3.14 and was run on Python 3.12 only.
- **Plaintext passwords in the movie apps.** For JSON storage, `moviewebapp_latest` writes the password to `registry/registry.json` unhashed, and the older `using session` variant stores plaintext passwords throughout. `storage-app-user` and the library apps hash passwords.
- **No migrations.** The flagship's unused Flask-Migrate wiring was removed; schema changes to an existing database are manual and documented in its README. `db_app_api/library_app` still initialises Flask-Migrate without a `migrations/` folder.
- **A misleading name in the frozen copy.** In `db_app_api/library_app`, `MYSQL_URI` actually holds a SQLite path. Nothing here connects to MySQL.
- **Version handling in `backend_api` is simple.** A `VERSION` dictionary maps `"0"` to an in-memory post list and `"1.0"`, `"1.1"` and `"1.2"` to the same JSON loader. It is a version switch, not a schema-migration system.
- **How the READMEs were checked.** Each project README was rewritten from the code, then re-checked by a second reviewer who ran the setup steps and the documented routes on a clean copy. Real OMDb and RapidAPI calls were not exercised (no keys were used), and `gunicorn` and the `Procfile` were not run.

## License

MIT. See [LICENSE](LICENSE).
