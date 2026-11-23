# MasterBlog

Learning project: a
small Flask blog that stores posts in a JSON file. It has no users or
authentication, and it is not meant for production use.

## Features

- Add, list, view, update and delete blog posts
- Like a post (a counter stored on the post)
- Posts stored in `data/blogs.json`: the `data/` folder is created at start-up and the file the first time a post route is used
- Forms built with Flask-WTF; CSRF protection is on for every POST
- Routes kept in a Flask blueprint (`blogs_routes.py`)

## Quick start

Requires Python 3 (checked with Python 3.12). From the `masterblog` folder, in
PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open <http://127.0.0.1:5000/>.

## Configuration

Read in `app.py`:

| Variable      | Effect                                                                                              |
| ------------- | --------------------------------------------------------------------------------------------------- |
| `SECRET_KEY`  | Flask secret key. If unset, a warning is issued and a random key is used, so sessions reset on restart |
| `FLASK_DEBUG` | Debug mode is on only when set to `1`                                                               |
| `FLASK_HOST`  | Host to bind, default `127.0.0.1`                                                                   |

The port is fixed at 5000. PowerShell example:

```powershell
$env:SECRET_KEY = "change-me"
python app.py
```

## Routes

`blogs_routes.py` declares the blueprint with `url_prefix="/blogs"`, but
`app.py` registers it with `url_prefix="/"`, which overrides it. The real URLs
(listed from the app's URL map) are:

| URL                      | Methods   | Purpose                                  |
| ------------------------ | --------- | ---------------------------------------- |
| `/`                      | GET       | Home page                                |
| `/blog_add`              | GET, POST | Add form and submit                      |
| `/blogs`                 | GET       | List all posts                           |
| `/blogs/<int:idx>`        | GET       | Show one post                            |
| `/blogs/update/<int:idx>` | GET, POST | Edit a post                              |
| `/blogs/delete/<int:idx>` | POST      | Delete a post, then redirect to the list |
| `/blogs/like/<int:idx>`   | POST      | Increment the like counter               |

An unknown post id returns a 404 page rendered from `templates/errors.html`.

## Project layout

```text
masterblog/
  app.py                    app setup, config, blueprint registration
  blogs_routes.py           routes
  json_post_management.py   JsonBlog storage class
  post_forms.py             BlogForm
  requirements.txt
  static/css/styles.css
  templates/                base, navbar, index, blog_add, blog_get,
                            blog_update, blogs_all, errors
  data/blogs.json           created at runtime
```

## Data and code notes

- `BlogForm` has `author`, `title`, `content` (a plain `TextAreaField`) and `submit`.
  The first three are `DataRequired`. CKEditor is not used.
- `JsonBlog` has `read_blog_data()`, `append_to_blogs(data)` and
  `save_the_blog()`. The posts are in its `blogs` list. There are no
  `load_blogs`, `update_blog` or `delete_blog` methods; the routes edit the list
  and call `save_the_blog()`.
- Each post is a dictionary with `id`, `title`, `author`, `content` and an
  optional `like` count.
- On add, title and author are stripped and title-cased; update title-cases the title and author too.
- Post content is rendered escaped by Jinja, so HTML typed into a post is shown
  as text.

## Requirements and front end

`requirements.txt` lists the packages the code imports: Flask, Flask-WTF
and WTForms, plus Werkzeug, pinned (it also comes in as a Flask dependency).
Bootstrap 5.3.3 is loaded from the jsDelivr CDN in `templates/base.html`, so the
pages need internet access to look right.

## Known limitations

- Delete has no confirmation. The like route renders the post page directly
  instead of redirecting, so refreshing the page after a like re-submits it.
- The update route title-cases the content (`<b>World</b>` became `<B>World</B>`).
- If `blogs.json` is corrupt, pages show it as empty, saving returns a 503 page
  and the file is never overwritten. Ids come from a `blogs.json.next_id`
  counter file next to the data file, so deleted ids are not reused.
- The 404 handler is registered on the blueprint, so URLs outside it get
  Flask's default 404 page.
- Tests: `python -m pytest masterblog/tests` (they use a temporary data file).

## License

MIT, see [LICENSE](../LICENSE).
