# Movie Web App with Multi-Storage Support

Advanced Flask application demonstrating storage abstraction pattern with user authentication and OMDb API integration.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)

---

## Overview

Full-stack Flask movie management application showcasing advanced software architecture with **abstract base class pattern** for storage backends. Users can seamlessly switch between SQLite, JSON, or CSV storage without code changes. Features user authentication, OMDb API integration for movie data, and comprehensive CRUD operations.

---

## Key Features

- **Storage Abstraction**: Switch between SQLite, JSON, CSV without modifying application code
- **User Authentication**: Flask-Login with password hashing
- **Movie Database Integration**: OMDb API for fetching movie information
- **Multi-User Support**: Each user has isolated movie collections
- **User Registration**: Registry system with unique username validation
- **Rich Forms**: WTForms with validation and CSRF protection
- **Bootstrap UI**: Responsive, modern interface
- **Session Management**: Secure user sessions
- **Version Control**: Data versioning in JSON/CSV formats

---

## Architecture Highlights

### Abstract Base Class Pattern

```python
class DataManagementInterface(ABC):
    @abstractmethod
    def get_all_users(self): pass

    @abstractmethod
    def get_user_movies(self, user_id): pass

    @abstractmethod
    def add_user(self, user_data): pass

    @abstractmethod
    def add_movie(self, user_id, movie_data): pass
```

**Concrete Implementations:**
- `SqliteDataManager` - SQLAlchemy ORM with relational database
- `JsonDataManager` - JSON file storage with dict-based indexing
- `CsvDataManager` - CSV file storage with pandas integration

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Flask | Web framework |
| SQLAlchemy | ORM for SQLite backend |
| Flask-Login | User authentication |
| Flask-WTF | Form validation |
| Bootstrap | Frontend UI framework |
| OMDb API | External movie database |
| Requests | HTTP client for API calls |
| pandas | CSV data manipulation (optional) |

---

## Project Versions

### Latest Version (`moviewebapp_latest/`)
- Complete implementation with all three storage backends
- OMDb API integration
- User reviews and ratings
- Advanced error handling

### Session Version (`using session/`)
- Session-based state management
- Simplified authentication flow
- Experimental features

---

## Prerequisites

- Python 3.8 or higher
- OMDb API key (free at [omdbapi.com](http://www.omdbapi.com/))
- pip (Python package manager)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/macraves/flask-wtform.git
cd flask-wtform/movie_web_app_multi_storage

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

## Configuration

### OMDb API Key

1. Get free API key from [omdbapi.com](http://www.omdbapi.com/apikey.aspx)
2. Set in your environment or configuration file

### Storage Type Selection

Users choose storage type during registration:
- **SQLite**: Relational database (recommended for production)
- **JSON**: File-based key-value storage
- **CSV**: Spreadsheet-style storage

---

## Usage

### Running the Application

```bash
cd moviewebapp_latest
python main.py
```

**Frontend**: `http://localhost:5000`

**Backend API**: `http://localhost:5001`

### First-Time Setup

1. Navigate to `http://localhost:5000`
2. Click "Sign Up"
3. Enter username, password, and select storage type
4. Login with credentials
5. Start adding movies to your collection

---

## Project Structure

```
movie_web_app_multi_storage/
├── moviewebapp_latest/              # Main application
│   ├── main.py                      # Application entry point
│   ├── frontend/
│   │   ├── frontend_app.py          # Frontend Flask app
│   │   ├── movie_wtf.py             # WTForms definitions
│   │   ├── forms_and_session_methods.py
│   │   ├── templates/               # HTML templates
│   │   └── static/                  # CSS, JS, images
│   ├── backend/
│   │   ├── backend_api.py           # REST API endpoints
│   │   ├── request_movie.py         # OMDb API integration
│   │   └── user_app_methods.py      # User operations
│   ├── datamanagement/
│   │   ├── storage_inheritance.py   # Abstract base class
│   │   ├── sqlite_data_manager.py   # SQLite implementation
│   │   ├── json_data_manager.py     # JSON implementation
│   │   ├── csv_data_manager.py      # CSV implementation
│   │   └── sqlite_models.py         # SQLAlchemy models
│   ├── user/
│   │   └── user_instance.py         # User class
│   ├── data/                        # Storage files (auto-created)
│   └── test_backend.py              # API tests
├── using session/                   # Alternative session-based version
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## Features in Detail

### User Management

- **Registration**: Unique username validation, password hashing
- **Login**: Flask-Login session management
- **Dashboard**: Personalized user view
- **Storage Isolation**: Each user's movies stored independently

### Movie Operations

#### Add Movie
1. Search by title via OMDb API
2. Auto-populate: poster, year, director, genre
3. Manual entry option available
4. Add to personal collection

#### View Movies
- List all movies in collection
- Detailed view with poster and metadata
- Filter and search capabilities

#### Update Movie
- Edit movie details
- Update ratings and reviews
- Change movie information

#### Delete Movie
- Remove from collection
- Confirmation prompt

### OMDb API Integration

```python
def fetch_movie_data(title, api_key):
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    response = requests.get(url)
    return response.json()
```

---

## Storage Backend Details

### SQLite (Recommended)

**Advantages:**
- Relational integrity
- ACID compliance
- Query optimization
- Best for production

**Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    storage_type TEXT
);

CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    year INTEGER,
    poster_url TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### JSON

**Advantages:**
- Human-readable
- Version control friendly
- Easy debugging

**Structure:**
```json
{
  "version": 1.0,
  "users": {
    "1": {
      "name": "john_doe",
      "movies": [
        {"id": 1, "title": "Inception", "year": 2010}
      ]
    }
  }
}
```

### CSV

**Advantages:**
- Excel compatible
- Simple data export
- Lightweight

**Format:**
```csv
user_id,movie_id,title,year,poster_url
1,1,Inception,2010,http://...
1,2,The Matrix,1999,http://...
```

---

## API Endpoints (Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users |
| GET | `/api/users/<id>/movies` | Get user's movies |
| POST | `/api/users` | Add new user |
| POST | `/api/users/<id>/movies` | Add movie to user |
| PUT | `/api/movies/<id>` | Update movie |
| DELETE | `/api/movies/<id>` | Delete movie |

---

## Advanced Features

### Dynamic Storage Selection

Users select storage type at registration. Application instantiates appropriate backend:

```python
if storage_type == "sqlite":
    data_manager = SqliteDataManager()
elif storage_type == "json":
    data_manager = JsonDataManager()
elif storage_type == "csv":
    data_manager = CsvDataManager()
```

### User Registry System

Centralized user registry in `registry/registry.json`:
- Prevents duplicate usernames
- Stores password hashes
- Maps users to storage types

### Version Control

JSON and CSV files include version numbers for future schema migrations:

```python
{
    "version": 1.0,
    "users": {...}
}
```

---

## Security Features

- Password hashing with Werkzeug
- CSRF protection via Flask-WTF
- Session security with Flask-Login
- SQL injection prevention (SQLAlchemy ORM)
- Input validation on all forms

---

## Testing

```bash
cd moviewebapp_latest
python test_backend.py
```

**Test Coverage:**
- User registration and login
- Movie CRUD operations
- Storage backend switching
- API endpoint validation

---

## Configuration Options

### Frontend App (`frontend_app.py`)

```python
app.config["SECRET_KEY"] = "your-secret-key"
app.config["OMDB_API_KEY"] = "your-omdb-key"
```

### Backend API (`backend_api.py`)

```python
API_PORT = 5001
CORS_ORIGINS = "*"  # Configure for production
```

---

## Troubleshooting

### OMDb API Errors

Check API key and quota:
```bash
curl "http://www.omdbapi.com/?t=Inception&apikey=YOUR_KEY"
```

### Storage File Corruption

Delete `data/` directory and restart application (creates fresh files).

### Login Issues

Clear browser cookies or check `registry/registry.json` for user entry.

---

## Future Enhancements

- MongoDB storage backend
- Redis caching layer
- Movie recommendations engine
- Social features (share lists)
- Export/import movie lists
- Advanced search and filters
- Movie ratings aggregation
- Watchlist functionality

---

## Design Patterns Used

- **Abstract Factory**: Storage backend creation
- **Strategy Pattern**: Interchangeable storage algorithms
- **Singleton**: Database connection management
- **MVC Architecture**: Model-View-Controller separation
- **Blueprint Pattern**: Flask route modularization

---

## License

MIT License - see root [LICENSE](../LICENSE) file.

---

## Author

[@macraves](https://github.com/macraves)
