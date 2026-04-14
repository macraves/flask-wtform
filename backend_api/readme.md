# Backend API with Version Control

RESTful API demonstrating API versioning patterns for blog post management with CRUD operations.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)

---

## Overview

Flask REST API implementing a custom version control system for managing blog posts. The project demonstrates API evolution through multiple versions, transitioning from in-memory storage to JSON file persistence with incremental schema changes.

---

## Features

- **API Versioning System**: Custom versioning (v0, v1.0, v1.1, v1.2) supporting schema evolution
- **CRUD Operations**: Complete create, read, update, delete functionality for blog posts
- **Multiple Storage Backends**: In-memory (v0) and JSON file storage (v1.0+)
- **Pagination & Sorting**: Configurable page size with sort by title/content/date
- **Search Functionality**: Search posts by title, content, or author
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Data Validation**: Schema validation for post creation and updates

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Flask | Web framework and REST API |
| Flask-CORS | Cross-origin resource sharing |
| Faker | Random sample data generation |
| Python logging | Application logging |

---

## API Versions

| Version | Schema | Storage |
|---------|--------|---------|
| v0 | `id, title, content` | In-memory list |
| v1.0 | `id, title, content` | JSON file |
| v1.1 | `id, title, content, date` | JSON file with timestamps |
| v1.2 | `id, title, content, date, author` | JSON file with author field |

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/macraves/flask-wtform.git
cd flask-wtform/backend_api

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

### Running the Backend API

```bash
cd FLASK-APIs/backend
python backend_app.py
```

**Backend API**: `http://localhost:5002`

### Running the Frontend

```bash
cd FLASK-APIs/frontend
python frontend_app.py
```

**Frontend**: `http://localhost:5001`

### Changing API Version

Edit `backend_app.py` and modify the `CHOSEN` variable:

```python
CHOSEN = 1.2  # Use version 1.2 (id, title, content, date, author)
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts` | Retrieve all posts (with pagination/sorting) |
| GET | `/api/posts/<id>` | Retrieve single post by ID |
| POST | `/api/posts` | Create new post |
| PUT | `/api/posts/<id>` | Update existing post |
| DELETE | `/api/posts/<id>` | Delete post by ID |
| GET | `/api/posts/search` | Search posts by query parameters |

### Query Parameters

- `page` - Page number (default: 1)
- `limit` - Posts per page (default: 10)
- `sort` - Sort field (title, content, date)
- `direction` - Sort direction (asc, desc)

---

## Project Structure

```
backend_api/
├── FLASK-APIs/
│   ├── backend/
│   │   ├── backend_app.py       # Main API application
│   │   ├── backend_methods.py   # Helper functions
│   │   └── posts.json           # JSON data storage (v1.0+)
│   ├── frontend/
│   │   └── frontend_app.py      # Frontend application
│   ├── Limiter_error.txt        # Rate limiter notes
│   └── requirements.txt         # Backend dependencies
├── create_doc.py                # Documentation generator
├── requirements.txt             # Project dependencies
└── readme.md                    # This file
```

---

## Configuration

### Switching Between Versions

Modify `CHOSEN` variable in `backend_app.py`:

```python
CHOSEN = 1.2  # Current version
VERSION = {
    "0": global_posts,    # In-memory
    "1.0": load_json,     # JSON file
    "1.1": load_json,     # + date field
    "1.2": load_json      # + author field
}
```

### Version Keys

```python
if CHOSEN == 1.0:
    version_keys = ["id", "title", "content"]
if CHOSEN == 1.1:
    version_keys = ["id", "title", "content", "date"]
if CHOSEN == 1.2:
    version_keys = ["id", "title", "content", "date", "author"]
```

---

## Example Requests

### Create Post (v1.2)

```bash
curl -X POST http://localhost:5002/api/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Blog Post",
    "content": "This is the content",
    "author": "John Doe"
  }'
```

### Get All Posts with Pagination

```bash
curl "http://localhost:5002/api/posts?page=1&limit=5&sort=date&direction=desc"
```

### Search Posts

```bash
curl "http://localhost:5002/api/posts/search?title=blog"
```

---

## Known Issues

- Flask-Limiter integration incomplete (see `Limiter_error.txt`)
- Rate limiting currently disabled

---

## License

MIT License - see root [LICENSE](../LICENSE) file.

---

## Author

[@macraves](https://github.com/macraves)
