# Movie Collection Manager - CLI Application

Command-line movie collection manager with multi-user support, OMDb API integration, and storage abstraction.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Requests](https://img.shields.io/badge/Requests-HTTP-green.svg)

---

## Overview

Python CLI application for managing personal movie collections with user authentication, OMDb API integration, and abstract storage pattern. Features user registry system, password validation, and HTML webpage generation for viewing collections in a browser.

---

## Features

- **Multi-User Support**: Individual user accounts with isolated movie collections
- **User Authentication**: Registration and login with password validation
- **Storage Abstraction**: Interface-based design supporting JSON and CSV backends
- **OMDb API Integration**: Automatic movie data fetching (title, year, rating, poster)
- **CLI Menu System**: Interactive command-line interface
- **Movie CRUD Operations**: Add, view, update, delete movies
- **HTML Generation**: Export collection to static webpage
- **Data Validation**: Input sanitization and error handling
- **Registry System**: Centralized user management

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.8+ | Core programming language |
| Requests | HTTP client for OMDb API |
| JSON | Default storage format |
| CSV | Alternative storage format |
| HTML | Static webpage generation |

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
cd flask-wtform/storage-app-user

# No external dependencies required (uses Python stdlib + requests)
pip install -r requirements.txt
```

---

## Configuration

### OMDb API Key

Set your API key in `movies_storage.py`:

```python
API_KEY = "your-omdb-api-key-here"
```

Or set as environment variable:

```bash
export OMDB_API_KEY="your-key"
```

---

## Usage

### Running the Application

```bash
python movie_user_app.py
```

### First-Time Setup

1. Run application
2. Select "Register" from main menu
3. Enter username and password
4. Choose storage type (JSON or CSV)
5. Login with credentials
6. Start managing your movie collection

---

## Menu Structure

### Main Menu

```
Movie Collection Manager
------------------------
1. Login
2. Register
3. Exit
```

### User Menu (After Login)

```
Movie Manager
-------------
1. List movies
2. Add movie
3. Delete movie
4. Update movie
5. Movie statistics
6. Random movie
7. Search movie
8. Movies sorted by rating
9. Generate website
0. Exit
```

---

## Project Structure

```
storage-app-user/
├── movie_user_app.py         # Main application and UserShell class
├── storage.py                # Storage implementations (JSON, CSV)
├── istorage.py               # IStorage abstract interface
├── movies_storage.py         # OMDb API integration
├── ioput.py                  # Input/output utilities
├── STORAGE/                  # User data storage (auto-created)
│   ├── registry/
│   │   └── registry.json     # User registry
│   └── <username>/
│       └── movies.json       # User's movie collection
├── _static/                  # HTML generation templates
│   └── index_template.html   # Webpage template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Architecture

### Abstract Interface Pattern

```python
class IStorage(ABC):
    @abstractmethod
    def list_movies(self): pass

    @abstractmethod
    def add_movie(self, title, year, rating, poster): pass

    @abstractmethod
    def delete_movie(self, title): pass

    @abstractmethod
    def update_movie(self, title, rating): pass
```

**Implementations:**
- `StorageJson` - JSON file storage (default)
- `StorageCsv` - CSV file storage

### Class Hierarchy

```
UserShell
├── Manages user authentication
├── Creates user directory structure
└── Connects user to MovieApp instance

MovieApp
├── Accepts IStorage instance
├── Performs CRUD operations
└── Integrates with OMDb API

IStorage (Abstract)
├── StorageJson
│   └── JSON file operations
└── StorageCsv
    └── CSV file operations
```

---

## Features in Detail

### User Registration

```python
# Creates:
# - User entry in registry/registry.json
# - User directory: STORAGE/<username>/
# - User storage file: STORAGE/<username>/movies.json
```

**Password Validation:**
- Minimum 6 characters
- Must contain letters and numbers
- Cannot be username

### Add Movie

1. Enter movie title
2. Application fetches data from OMDb API
3. Auto-populates: title, year, IMDb rating, poster URL
4. Saves to user's storage file

**OMDb API Response:**
```json
{
  "Title": "Inception",
  "Year": "2010",
  "imdbRating": "8.8",
  "Poster": "https://..."
}
```

### Movie Statistics

- Total number of movies
- Average rating
- Median rating
- Best and worst rated movies

### Random Movie

Selects random movie from collection with details.

### Search Movies

Search by partial title match (case-insensitive).

### Sort by Rating

Display all movies sorted by IMDb rating (descending).

### Generate Website

Creates static HTML page displaying movie collection:
- Movie posters in grid layout
- Title, year, and rating
- Responsive design
- Output: `<username>_movies.html`

---

## Data Storage Formats

### JSON Storage (`StorageJson`)

```json
{
  "Inception": {
    "rating": 8.8,
    "year": 2010,
    "poster": "https://...",
    "note": "Mind-bending thriller"
  },
  "The Matrix": {
    "rating": 8.7,
    "year": 1999,
    "poster": "https://..."
  }
}
```

### CSV Storage (`StorageCsv`)

```csv
title,year,rating,poster,note
Inception,2010,8.8,https://...,Mind-bending thriller
The Matrix,1999,8.7,https://...,
```

### User Registry

```json
{
  "users": {
    "john_doe": {
      "password": "hashed_password",
      "storage_type": "json",
      "created": "2024-01-15"
    }
  }
}
```

---

## Code Examples

### Adding a Movie (Manual)

```python
from storage import StorageJson

storage = StorageJson("STORAGE/username/movies.json")
storage.add_movie("Inception", "2010", 8.8, "https://poster-url")
```

### Listing Movies

```python
movies = storage.list_movies()
for title, data in movies.items():
    print(f"{title} ({data['year']}) - {data['rating']}/10")
```

### Updating Movie

```python
storage.update_movie("Inception", new_rating=9.0)
```

---

## Error Handling

Custom exception classes:

```python
class StorageError(Exception):
    """Storage operation errors"""

class AppError(Exception):
    """Application logic errors"""

class UserShellError(Exception):
    """User authentication errors"""

class FunctionErrors(Exception):
    """OMDb API errors"""
```

**Common Errors:**
- Movie not found in OMDb database
- Movie already exists in collection
- Invalid username or password
- Storage file corruption
- API rate limit exceeded

---

## Input Validation

### Movie Title

- Strips whitespace
- Converts to title case
- Checks for duplicates
- Validates against OMDb API

### Password

```python
def validate_password(password, username):
    if len(password) < 6:
        raise UserShellError("Password too short")
    if password == username:
        raise UserShellError("Password cannot be username")
    if not any(c.isalpha() for c in password):
        raise UserShellError("Password must contain letters")
    if not any(c.isdigit() for c in password):
        raise UserShellError("Password must contain numbers")
```

---

## HTML Webpage Generation

Generates static HTML page with:
- Grid layout of movie posters
- Title overlay on hover
- Year and rating display
- Responsive CSS
- Mobile-friendly design

**Output:** `<username>_movies.html`

---

## OMDb API Integration

### Fetching Movie Data

```python
def get_by_name(movie_name):
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise FunctionErrors("Movie not found")
```

### Response Handling

- Validates API response
- Extracts relevant fields
- Handles missing data gracefully
- Provides error messages for invalid titles

---

## Configuration Options

### Storage Type Selection

User chooses during registration:
- **JSON** (default): Fast, human-readable
- **CSV**: Spreadsheet compatible, exportable

### Directory Structure

Customizable in `movie_user_app.py`:

```python
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FOLDER_DIR = os.path.join(SCRIPT_DIR, "STORAGE")
```

---

## Troubleshooting

### OMDb API Errors

Check API key and quota:
```bash
curl "http://www.omdbapi.com/?t=Inception&apikey=YOUR_KEY"
```

### Storage File Corruption

Delete user storage file (movies.json/movies.csv) and restart.

### User Not Found

Check `STORAGE/registry/registry.json` for user entry.

---

## Future Enhancements

- Password hashing (bcrypt/Werkzeug)
- SQLite storage backend
- Movie notes and reviews
- Watchlist feature
- Import/export collection (JSON/CSV)
- Advanced search filters
- Movie recommendations
- Batch add from file
- Cloud storage integration (Google Drive, Dropbox)

---

## Comparison with Web Version

| Feature | CLI (This Project) | Web (`movie_web_app`) |
|---------|-------------------|---------------------|
| **Interface** | Command-line | Web browser |
| **Authentication** | File-based | Flask-Login |
| **Storage** | JSON, CSV | SQLite, JSON, CSV |
| **Deployment** | Local only | Web server |
| **HTML Output** | Static generation | Dynamic templates |

---

## Design Patterns

- **Abstract Factory**: IStorage interface
- **Strategy Pattern**: Interchangeable storage backends
- **Singleton**: Registry management
- **Template Method**: HTML generation

---

## License

MIT License - see root [LICENSE](../LICENSE) file.

---

## Author

[@macraves](https://github.com/macraves)
