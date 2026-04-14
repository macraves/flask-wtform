# MasterBlog - Flask Blog Application

Simple blog application with CRUD operations, WTForms validation, and JSON file storage.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![WTForms](https://img.shields.io/badge/WTForms-3.0-orange.svg)

---

## Overview

Lightweight Flask blog application demonstrating core web development concepts: routing, template rendering, form handling, and CRUD operations. Uses JSON file persistence for simplicity and WTForms for validation and CSRF protection.

---

## Features

- **Complete CRUD Operations**: Create, read, update, and delete blog posts
- **Form Validation**: WTForms with CSRF protection
- **Flash Messages**: User feedback for successful operations
- **JSON Storage**: Lightweight file-based persistence
- **Blueprint Architecture**: Modular route organization
- **Responsive Templates**: Clean, organized UI
- **Auto-capitalization**: Title and author fields automatically formatted

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Flask | Web framework |
| WTForms | Form validation and rendering |
| JSON | Data persistence |
| Jinja2 | Template engine |
| Blueprint | Route modularization |

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/macraves/flask-wtform.git
cd flask-wtform/masterblog

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Running the Application

```bash
python app.py
```

**Application URL**: `http://localhost:5000`

### First-Time Setup

1. Application automatically creates `data/` directory
2. `blogs.json` file created on first post addition
3. Start adding blog posts immediately

---

## Project Structure

```
masterblog/
├── app.py                      # Main application entry point
├── blogs_routes.py             # Blog routes blueprint
├── json_post_management.py     # JSON file operations
├── post_forms.py               # WTForms definitions
├── templates/
│   ├── index.html              # Homepage
│   ├── blog_add.html           # Add blog form
│   ├── blogs_all.html          # List all blogs
│   ├── blog_update.html        # Update blog form
│   └── blog_detail.html        # Single blog view
├── static/
│   └── css/
│       └── style.css           # Custom styles
├── data/
│   └── blogs.json              # Blog data storage (auto-created)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Homepage/Welcome page |
| `/blogs/blog_add` | GET, POST | Add new blog post |
| `/blogs/blogs` | GET | List all blog posts |
| `/blogs/blog/<id>` | GET | View single blog post |
| `/blogs/blog_update/<id>` | GET, POST | Update blog post |
| `/blogs/blog_delete/<id>` | POST | Delete blog post |

---

## Form Fields

### BlogForm (WTForms)

```python
class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')
```

**Validation:**
- All fields required
- Automatic title case for title and author
- Content whitespace trimming
- CSRF token protection

---

## Data Storage

### JSON Structure

```json
[
  {
    "id": 1,
    "title": "My First Blog Post",
    "author": "John Doe",
    "content": "This is the content of my first blog post."
  },
  {
    "id": 2,
    "title": "Flask Tutorial",
    "author": "Jane Smith",
    "content": "Learn Flask with this comprehensive guide."
  }
]
```

### JsonBlog Class

Handles all JSON file operations:
- `load_blogs()` - Read from file
- `save_the_blog()` - Write to file
- `append_to_blogs(data)` - Add new blog
- `update_blog(blog_id, updated_data)` - Update existing
- `delete_blog(blog_id)` - Remove blog

---

## Features in Detail

### Create Blog Post

1. Navigate to `/blogs/blog_add`
2. Fill in title, author, and content
3. Submit form (validated with WTForms)
4. Blog auto-assigned unique ID
5. Redirected to all blogs view with success message

### Read Blog Posts

- **List View** (`/blogs/blogs`): See all posts
- **Detail View** (`/blogs/blog/<id>`): Read full post content

### Update Blog Post

1. Click "Edit" button on blog
2. Form pre-populated with existing data
3. Make changes and submit
4. Validation applied
5. Redirected with success message

### Delete Blog Post

1. Click "Delete" button on blog
2. Confirmation required
3. Post removed from JSON file
4. Redirected with success message

---

## Configuration

### Secret Key

Change in `app.py` for production:

```python
app.config["SECRET_KEY"] = "your-secret-key-here"
```

### File Path

Modify in `blogs_routes.py`:

```python
FILE_PATH = os.path.join(folder_to_save, "blogs.json")
```

### Host and Port

Edit in `app.py`:

```python
app.run(debug=True, host="0.0.0.0", port=5000)
```

---

## Code Examples

### Adding a Blog (Programmatic)

```python
from json_post_management import JsonBlog

blog_manager = JsonBlog(file_path="data/blogs.json")

new_blog = {
    "title": "Python Tips",
    "author": "Developer",
    "content": "Here are some Python tips..."
}

blog_manager.append_to_blogs(new_blog)
blog_manager.save_the_blog()
```

### Updating a Blog

```python
blog_manager.update_blog(
    blog_id=1,
    updated_data={
        "title": "Updated Title",
        "content": "Updated content..."
    }
)
```

---

## Flash Messages

Success messages displayed after operations:

```python
flash("Form Submitted successfully")
flash("Blog updated successfully")
flash("Blog deleted successfully")
```

---

## Blueprint Architecture

Routes organized with Flask Blueprint:

```python
posts = Blueprint("blog", __name__,
                 url_prefix="/blogs",
                 template_folder="templates")
```

**Benefits:**
- Modular route organization
- Namespace isolation
- Easier testing and maintenance

---

## Error Handling

- **404 Errors**: Invalid blog IDs return abort(404)
- **Form Validation**: WTForms prevents invalid submissions
- **File Operations**: JSON file auto-created if missing
- **CSRF Protection**: Automatic token validation

---

## Future Enhancements

- User authentication and authorization
- Categories and tags
- Search functionality
- Pagination for blog lists
- Markdown support for content
- Image upload for blog posts
- Database backend (SQLite/PostgreSQL)
- Comments system
- Social sharing buttons

---

## Development Tips

### Debug Mode

Debug mode is **enabled** by default. Disable for production:

```python
app.run(debug=False)
```

### Testing Locally

```bash
# Run on all network interfaces
python app.py

# Access from other devices on network
http://<your-ip>:5000
```

---

## Troubleshooting

### Port Already in Use

Change port in `app.py`:

```python
app.run(debug=True, port=5001)
```

### JSON File Corruption

Delete `data/blogs.json` and restart app (creates fresh file).

### Forms Not Submitting

Check CSRF token is present in templates:

```html
{{ form.hidden_tag() }}
```

---

## License

MIT License - see root [LICENSE](../LICENSE) file.

---

## Author

[@macraves](https://github.com/macraves)
