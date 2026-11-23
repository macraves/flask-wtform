# storage-app-user

Learning project: a command-line movie
collection with one account per user. Movie details are looked up through the
OMDb API and stored in a JSON or CSV file, chosen each time you run the program.
It is a learning exercise, not production software.

## Setup

Requires Python 3 and a free OMDb API key (<https://www.omdbapi.com/apikey.aspx>).

```powershell
pip install -r requirements.txt
Copy-Item .env.example .env
```

Put the key in `.env` as `OMDB_API_KEY=...`, or set it as an environment
variable. The key is only needed for the Add menu item; without it Add reports
`OMDB_API_KEY environment variable is not set`. `requirements.txt` lists
`requests` and `python-dotenv`.

Run from this folder:

```powershell
python movie_user_app.py
```

## First-run flow

The program asks, in order:

1. `Have you been registed before y/n: ` (the typo is in the code). Any answer
   containing a `y` counts as yes.
2. If no: `Do you want to sign in y/n: `. Yes starts registration (despite the
   wording), no ends the program with `APPLICATION IS ABORTED`.
3. `Please Enter your name: ` and `Please enter your password: `.
4. `Please enter file extension (json/csv): `.

Details:

- Usernames are lower-cased and must match `^[a-z0-9_-]{1,32}$`, because they
  become folder and file names. Anything else aborts the program.
- Registering an existing username aborts with `User is already registered!!`.
  Signing in as an unknown user aborts with `User is not registered!!`.
- Passwords are stored as a salted PBKDF2-HMAC-SHA256 hash (600,000
  iterations). A legacy record with a plaintext `password` field is converted to
  a hash on the first successful sign-in.
- A wrong password does not allow a retry: the program prints
  `Password is not correct!! Aborted` and exits.
- An extension other than `json` or `csv` aborts the program.

## Menu

After sign-in the program loops on this menu until you choose 8:

```text
1. List Movies
2. Add Movie
3. Delete Movie
4. Update Movie
5. Sort Movies
6. Stat Movies
7. Generate User Webpage
8. exit
```

- Add asks for a title, looks it up on OMDb and stores title, year, imdbRating
  and poster. Titles are stored title-cased; duplicates are rejected. A movie
  whose rating OMDb reports as `N/A` is rejected with
  `Movie rating is not available: N/A`.
- Delete asks for a title. Update asks for a title and a new rating (a number).
- Sort asks for `asc` or `desc` (any case) and orders by rating.
- Stat prints only the maximum, minimum and average rating; on an empty
  collection it reports `No movies in database`.
- Generate User Webpage writes an HTML page for the signed-in user.
- Errors raised as `AppError`, `StorageError` or `FunctionErrors` are printed
  and the menu continues.

## Where data lives

All paths are relative to this folder and created on demand:

| Path | Content |
| --- | --- |
| `registry/<user>/registry.json` | username, salt, password hash |
| `STORAGE/<user>.json` or `STORAGE/<user>.csv` | the user's movies |
| `_static/<user>.html` | generated page, uses `_static/style.css` |

The page is built from `_static/index_template.html`. Movie records use the
keys `Title`, `Year`, `imdbRating` and `Poster`. JSON files key each movie by
title; CSV files have the header `Title,Year,imdbRating,Poster`.

## Code layout

- `movie_user_app.py`: `MovieApp` (menu operations on a storage object),
  `UserShell` (registry, password check, paths), the sign-in flow and the menu
  loop. Defines `AppError` and `UserShellError`.
- `storage.py`: `StorageJson` and `StorageCsv`, both implementing the abstract
  `IStorage` from `istorage.py`. Defines `StorageError`.
- `movies_storage.py`: OMDb request, sort, stats and HTML generation. Defines
  `FunctionErrors`.
- `ioput.py`: input helpers that re-prompt on invalid entries.

## Tests

```powershell
pip install pytest
python -m pytest tests -q
```

The tests use temporary folders and mocked OMDb, `input` and `getpass`; they
never touch `registry/`, `STORAGE/` or the real API.

## Known limitations

- The `N/A` rating fix was tested with a mocked OMDb response, not the real API.
- Poster values are HTML-escaped and quoted but not checked for a URL scheme or
  for OMDb's `N/A` placeholder.

## License

MIT, see [LICENSE](../LICENSE).
