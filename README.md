# Flask & Python Projects

Eight small projects from my path into Python backend development: Flask web apps and APIs, SQLAlchemy models, and command-line tools. They are learning projects, not production systems. This page says what each one contains and where the rough edges are.

## Projects

| Project | What it is | Built with | Tests |
| --- | --- | --- | --- |
| [Best-Buy](./Best-Buy) | Store inventory CLI: three product types, three promotion types, a shopping cart and order totals | Python, `unittest` | 20 unit tests |
| [backend_api](./backend_api) | Blog post REST API (list, search, add, update, delete) with a small Flask front end | Flask, Flask-CORS, Faker | none |
| [masterblog](./masterblog) | Blog with create, read, update, delete and like, storing posts in a JSON file | Flask, WTForms, CKEditor | none |
| [db_app_api/library_app](./db_app_api) | Library site with authors, books, posts and user accounts, split into four Blueprints | Flask, SQLAlchemy, Flask-Login, WTForms, CKEditor | none |
| [library_app_production](./library_app_production) | The same library app, configured through environment variables and a Gunicorn `Procfile` | as above, plus Gunicorn | none |
| [movie_web_app_multi_storage](./movie_web_app_multi_storage) | Movie collection app whose users choose SQLite, JSON or CSV storage, with a JSON API | Flask, SQLAlchemy, Flask-Login, OMDb API | manual script |
| [storage-app-user](./storage-app-user) | Command-line movie collection manager using the OMDb API | Python, Requests | none |
| [data_scientist](./data_scientist) | Flight delay analysis. It now lives in its own repository: [flight-data-analysis](https://github.com/macraves/flight-data-analysis) | SQLAlchemy, matplotlib, seaborn, folium, Flask | in the new repo |

Each project has its own `requirements.txt` and README. Entry points: `Best-Buy/main.py`, `masterblog/app.py`, `db_app_api/library_app/app.py`, `library_app_production/main.py`, `storage-app-user/movie_user_app.py`, `movie_web_app_multi_storage/moviewebapp_latest/main.py`, and for the blog API `backend_api/FLASK-APIs/backend/backend_app.py`.

## What the code shows

- **Storage behind an interface.** `movie_web_app_multi_storage` defines an abstract `DataManagmentInterface` (in `datamanagement/storage_inheritance.py`) with separate SQLite, JSON and CSV managers. The app picks one when the user logs in.
- **Flask Blueprints.** The library app splits authors, books, posts and users into four Blueprints, each with its own routes and templates.
- **Authentication.** Flask-Login handles sessions in the library and movie apps.
- **Parameterised queries.** The flight analysis project passes values to SQL as bound parameters, and its tests check an injection-style input.
- **Object-oriented design.** `Best-Buy` uses an abstract promotion base class with percentage-discount, second-half-price and third-one-free subclasses.
- **Environment-based config.** `library_app_production` reads `SECRET_KEY` and `SQLALCHEMY_DATABASE_URI` from the environment, and its `Procfile` runs `gunicorn main:app`. I have not deployed it.
- **Documentation habits.** A script I ran over the repo counted 571 functions: 86% have a docstring and 27% have type hints.

## Known gaps

I would rather list these than have a reviewer find them.

- **Testing is thin.** Only `Best-Buy` has real automated tests (20, all passing). The movie app's `test_backend.py` is a manual script that needs the server running. The Flask apps have no tests.
- **Admin access is one hard-coded check.** In the library apps, `/users/admin` allows the user whose ID is `1`. There are no roles.
- **Demo secrets are committed.** `db_app_api` and `masterblog` set `SECRET_KEY` to a literal string. Only the production variant reads it from the environment.
- **Migrations are wired up but unused.** Flask-Migrate is initialised in the library apps, but there is no `migrations/` folder, so schema changes were not tracked.
- **A misleading name.** In the library apps, `MYSQL_URI` actually holds a SQLite path. Nothing here connects to MySQL.
- **Version handling in `backend_api` is simple.** A `VERSION` dictionary maps `"0"` to an in-memory post list and `"1.0"`, `"1.1"` and `"1.2"` to the same JSON loader. It is a version switch, not a schema-migration system.
- **I did not re-run the web apps when I rewrote this page.** I ran the `Best-Buy` tests and checked the other claims against the source.

## License

MIT. See [LICENSE](LICENSE).
