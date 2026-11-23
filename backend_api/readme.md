# Blog Posts REST API (learning project)

A small Flask REST API for blog posts, stored in a JSON file, plus a tiny Flask frontend that calls it. It is a learning project and has known bugs, listed below.

## What is in it

- Backend API on port 5002 (`FLASK-APIs/backend/backend_app.py`).
- Frontend on port 5001 (`FLASK-APIs/frontend/frontend_app.py`). It serves one page whose JavaScript loads, adds and deletes posts through the API. The API base URL defaults to `http://127.0.0.1:5002/api` in the page.
- A hand-rolled "version" switch that changes which fields a post has (1.0, 1.1, 1.2).

Both apps bind to `127.0.0.1` by default. Set `FLASK_HOST` to change the host and `FLASK_DEBUG=1` to enable debug mode.

## Layout

```text
backend_api/
├── FLASK-APIs/
│   ├── backend/
│   │   ├── backend_app.py       # routes, sorting, error handler
│   │   ├── backend_methods.py   # JSON storage, validation, version upgrade
│   │   └── STORAGE/posts.json   # data file
│   ├── frontend/
│   │   ├── frontend_app.py
│   │   ├── static/              # main.js, styles.css
│   │   └── templates/           # index.html
│   ├── Limiter_error.txt        # note about the Flask-Limiter error
│   └── requirements.txt
├── create_doc.py                # writes template snippets to samples/template.json
├── requirements.txt
└── readme.md
```

## Run

Run each app from its own folder, because the imports are bare (`from backend_methods import ...`). Use two terminals. The commands are PowerShell.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install flask flask-cors faker
```

Backend:

```powershell
cd FLASK-APIs\backend
python backend_app.py
```

Frontend:

```powershell
cd FLASK-APIs\frontend
python frontend_app.py
```

Then open <http://127.0.0.1:5001>.

`flask flask-cors faker` are the packages the code uses. `pip install -r requirements.txt` also works but installs unneeded packages, see "Known limitations".

If `STORAGE/posts.json` does not exist, the backend creates it with an empty post list on the first request.

## Endpoints

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/posts` | List posts, with paging and sorting. |
| GET | `/api/posts/search` | Filter posts by field values. |
| POST | `/api/posts` | Create a post. JSON body needs `title` and `content`. |
| PUT | `/api/posts/<id>` | Replace the post with that id. Body needs `title` and `content`. |
| DELETE | `/api/posts/<id>` | Delete the post with that id. |

There is no `GET /api/posts/<id>`; it returns 405.

Errors are returned as `{"message": ..., "status_code": ...}` with that status code (400 for a bad body on POST or a request whose query parameters are all unknown, 404 for an unknown id on DELETE or an invalid PUT body, 415 for a non-JSON body on POST). A few inputs return a 500 instead, see "Known limitations".

Examples:

```powershell
Invoke-RestMethod "http://127.0.0.1:5002/api/posts?page=1&limit=5"

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5002/api/posts" `
  -ContentType "application/json" `
  -Body '{"title": "my post", "content": "hello"}'

Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:5002/api/posts/1"
```

### Query parameters on `GET /api/posts`

- `page` (default 1) and `limit` (default 10) slice the list. A non-numeric value falls back to the default.
- `sort` and `direction` (`asc` or `desc`). Only `sort=date` actually sorts, see "Known limitations".
- `id`, `title`, `content` and `author` filter by exact match. String values are title-cased before comparing, so `title=my post` matches the stored `My Post`. `date` is accepted but ignored.
- A request whose parameters are all unknown returns 400. Unknown parameters mixed with a valid one are silently ignored.
- `page` and `limit` are not validated: `page=0` returns an empty list and `limit=-1` slices oddly.

Stored string values are title-cased and stripped when a post is created or replaced, and again when listed.

## Versions

Set the `CHOSEN` constant near the top of `backend_app.py` (the code ships with `CHOSEN = 1.0`) and restart the backend.

| `CHOSEN` | Fields | Storage |
|----------|--------|---------|
| 1.0 | `id`, `title`, `content` | `STORAGE/posts.json` |
| 1.1 | adds `date` (`YYYY-MM-DD`) | same file |
| 1.2 | adds `author` | same file |
| 0 | `id`, `title`, `content` | in-memory list (broken, see below) |

When the file's stored `version` differs from `CHOSEN`, 1.1 and 1.2 add the new field to every stored post using a random date between 2000 and 2023 (1.1) or a fake name from Faker (1.2); the 1.2 step adds only `author`, so a 1.0 file upgraded straight to 1.2 gets no `date`. Switching to 1.0 when the file's version differs replaces ALL stored posts with 5 random ones. New posts get today's date and `Anonymous` as author when none is given, but only in 1.2 (in 1.1, POST creates posts with no `date`).

## Known limitations

Each of these was checked by running the code on a copy, through the Flask test client.

- Sorting: `sort=title`, `sort=id` and any non-date field leave the order unchanged. The non-date branch only sorts when `sort == "date"`, and it reads the misspelled `direcection` key, so `direction` is ignored there.
- Search: it is not substring search. Each value is title-cased and compared for equality. Several parameters are OR-combined, and a post matching more than one is returned more than once. `id=x` returns a 500 on both `/api/posts` and `/api/posts/search`, because the error handler cannot serialize the exception.
- Responses to POST, PUT and DELETE return a list of posts (the first 20), read before the change, so it does not show the new state.
- PUT replaces the whole post (and moves it to the end of the file); fields not sent are not kept. In 1.2 `date` and `author` are refilled with defaults. In 1.1 a PUT drops `date`, and any post without a `date` makes `sort=date` return 500 (`KeyError`).
- Version 0 is broken: with `CHOSEN = 0` the `version_keys` variable is never defined (GET and search) and `data` is unbound (POST, PUT, DELETE), so every endpoint returns 500.
- `requirements.txt` lists `logging`. `pip install -r requirements.txt` succeeds but installs an unrelated old PyPI package of that name (it took over two minutes here); the standard-library `logging` is still what the code imports. `Flask-Limiter` installs too, but all the limiter code is commented out in `backend_app.py` (see `FLASK-APIs/Limiter_error.txt`), so there is no rate limiting.
- The frontend loads posts on start-up only if a base URL is already stored in the browser's `localStorage`, so the first visit shows nothing until you trigger the load. It writes post titles and content into the page with `innerHTML` (`static/main.js`), which is an XSS risk. CORS is open to all origins.
- `create_doc.py` is not a documentation generator. It writes SSR and CSR Flask template snippets into `samples/template.json` next to the script.
- The frontend has no edit/update; its script only fetches, posts and deletes.

## License

MIT, see [LICENSE](../LICENSE).
