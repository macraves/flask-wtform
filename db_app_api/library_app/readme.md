# Library Management System

Full-stack Flask application with user authentication, admin controls, and comprehensive CRUD operations for library management.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)

---

## Overview

Complete library management system built with Flask and SQLAlchemy ORM. Features user authentication with role-based access control, relational database design, and rich text editing capabilities. The first registered user (ID: 1) becomes the admin with full system privileges.

---

## Features

- **User Authentication**: Registration, login, password hashing with Werkzeug
- **Role-Based Access Control**: Admin (User ID 1) has exclusive author management rights
- **Multi-Entity CRUD**: Manage users, authors, books, and blog posts
- **Relational Database**: Foreign key relationships between entities
- **Rich Text Editing**: CKEditor integration for blog posts
- **Search Functionality**: Search across books, authors, and posts
- **Blueprint Architecture**: Modular application structure
- **Database Migrations**: Flask-Migrate for schema versioning
- **Responsive UI**: Bootstrap-styled templates with WTForms

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Flask | Web framework |
| SQLAlchemy | ORM and database management |
| Flask-Login | User session management |
| Flask-WTF | Form validation and CSRF protection |
| Flask-Migrate | Database migrations |
| Flask-CKEditor | Rich text editor |
| Bootstrap | Frontend styling |
| SQLite | Database engine |
| Werkzeug | Password hashing |

---

## Database Schema

### Users Table
- User authentication and profile management
- One-to-many relationship with Books and Posts

### Authors Table
- Author information with birth/death dates
- One-to-many relationship with Books
- Admin-only management

### Books Table
- ISBN, title, publication year, condition
- Foreign keys: `author_id`, `user_id`
- Many-to-one relationships

### Posts Table
- Blog posts with title, subtitle, content
- Foreign key: `author_id` (User)
- Rich text content support

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/macraves/flask-wtform.git
cd flask-wtform/db_app_api/library_app

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

1. Navigate to `http://localhost:5000`
2. Register the first user (becomes admin automatically)
3. Admin can now manage authors, books, users, and posts

---

## Application Structure

```
library_app/
├── app.py                   # Main application entry point
├── data_models.py           # SQLAlchemy models (User, Author, Book, Post)
├── allwebforms.py           # WTForms definitions
├── book_api.py              # Book-related API endpoints
├── author/
│   ├── aroutes.py           # Author blueprint routes
│   └── templates/           # Author-specific templates
├── book/
│   ├── broutes.py           # Book blueprint routes
│   └── templates/           # Book-specific templates
├── post/
│   ├── proutes.py           # Post blueprint routes
│   └── templates/           # Post-specific templates
├── user/
│   ├── uroutes.py           # User blueprint routes
│   └── templates/           # User-specific templates
├── templates/
│   ├── base.html            # Base template
│   ├── index.html           # Homepage
│   └── navbar.html          # Navigation bar
├── static/
│   └── css/
│       └── style.css        # Custom styles
├── data/
│   └── library.sqlite       # SQLite database (auto-created)
├── requirements.txt         # Python dependencies
└── readme.md                # This file
```

---

## User Roles

### Admin (User ID = 1)
- Full access to all features
- Exclusive author management (add/edit/delete)
- Can modify all books and posts
- User management capabilities

### Regular Users
- Manage own books and posts
- View all public content
- Cannot manage authors
- Profile management

---

## Key Routes

### Authentication
- `/users/register` - User registration
- `/users/login` - User login
- `/users/logout` - User logout
- `/users/dashboard` - User dashboard

### Authors (Admin Only)
- `/authors/all` - List all authors
- `/authors/add` - Add new author
- `/authors/<id>` - View author details
- `/authors/update/<id>` - Edit author
- `/authors/delete/<id>` - Delete author

### Books
- `/books/all` - List all books
- `/books/add` - Add new book
- `/books/<id>` - View book details
- `/books/update/<id>` - Edit book (owner only)
- `/books/delete/<id>` - Delete book (owner only)
- `/books/search` - Search books

### Posts
- `/posts/all` - List all blog posts
- `/posts/add` - Create new post
- `/posts/<id>` - View post
- `/posts/update/<id>` - Edit post (owner only)
- `/posts/delete/<id>` - Delete post (owner only)

---

## Configuration

### Database URI

Edit `data_models.py` to change database:

```python
# SQLite (default)
MYSQL_URI = f"sqlite:///{data_folder_root}/library.sqlite"

# MySQL example
MYSQL_URI = "mysql://username:password@localhost/library_db"
```

### Secret Key

Change in `app.py` for production:

```python
app.config["SECRET_KEY"] = "your-secret-key-here"
```

---

## Database Migrations

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

---

## Forms (WTForms)

### User Forms
- Registration form with password confirmation
- Login form with username/email
- Profile update form

### Book Forms
- Add/edit book with ISBN, title, author selection
- Publication year and condition fields
- Cover URL upload

### Post Forms
- CKEditor-powered content field
- Title and subtitle fields
- CSRF protection enabled

---

## Security Features

- **Password Hashing**: Werkzeug's `generate_password_hash`
- **CSRF Protection**: Flask-WTF automatic token generation
- **Session Management**: Flask-Login secure sessions
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **Access Control**: Route decorators for authentication

---

## Example Usage

### Adding a Book (Code)

```python
from data_models import Book, db

new_book = Book(
    isbn="978-0-123456-78-9",
    title="Python Programming",
    publication_year=2024,
    author_id=1,
    user_id=1
)
db.session.add(new_book)
db.session.commit()
```

### Querying with Relationships

```python
# Get all books by an author
author = Author.query.get(1)
author_books = author.books

# Get user's books
user = User.query.get(1)
user_books = user.books
```

---

## Known Limitations

- Single admin model (only User ID 1)
- No file upload for book covers (URL only)
- No multi-factor authentication
- Basic search functionality (no full-text search)

---

## Future Enhancements

- Multi-admin support with permission levels
- Book cover image upload and storage
- Advanced search with filters
- Book borrowing/lending system
- Reading list and favorites
- Export data to CSV/PDF
- Email verification for registration

---

## Acknowledgments

Built following Flask and database relationship tutorials from [Codecademy](https://www.codecademy.com). Special thanks to instructors for comprehensive guidance on SQLAlchemy ORM and Flask best practices.

---

## License

MIT License - see root [LICENSE](../../LICENSE) file.

---

## Author

[@macraves](https://github.com/macraves)
