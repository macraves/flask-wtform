# Library Management System - Production Deployment

Production-ready version of the library management system with environment-based configuration and Gunicorn WSGI server.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Gunicorn](https://img.shields.io/badge/Gunicorn-WSGI-blue.svg)

---

## Overview

Production-optimized deployment of the full-stack Flask library management system. Features environment variable configuration for secure credential management, Gunicorn WSGI server for production performance, and deployment-ready structure for platforms like Heroku, Railway, or Render.

---

## Key Differences from Development Version

| Feature | Development (`db_app_api`) | Production (This Version) |
|---------|---------------------------|---------------------------|
| **Configuration** | Hardcoded in `app.py` | Environment variables |
| **Server** | Flask dev server | Gunicorn WSGI |
| **Secret Key** | Static string | Environment variable |
| **Database URI** | Hardcoded path | Environment variable |
| **Entry Point** | `app.py` | `main.py` |
| **Deployment** | Local only | Platform-ready (Heroku, etc.) |

---

## Features

All features from the base library management system, plus:

- **Environment Variable Configuration**: Secure credential management
- **Gunicorn WSGI Server**: Production-grade performance
- **Procfile**: Heroku/Railway deployment support
- **12-Factor App Compliance**: Separation of config from code
- **Production Error Handling**: Custom 404/500 error pages
- **Scalable Architecture**: Ready for cloud deployment

---

## Prerequisites

- Python 3.8 or higher
- Environment variable management (local: `.env` file, production: platform settings)
- Gunicorn (included in requirements.txt)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/macraves/flask-wtform.git
cd flask-wtform/library_app_production

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

### Environment Variables

Create a `.env` file in the project root (local development only):

```bash
# Database Configuration
SQLALCHEMY_DATABASE_URI=sqlite:///data/library.sqlite

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# Optional: MySQL/PostgreSQL
# SQLALCHEMY_DATABASE_URI=mysql://user:password@localhost/library_db
# SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/library_db
```

### Loading Environment Variables (Local Development)

Install `python-dotenv` and load in `main.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Usage

### Local Development

```bash
# Using Flask development server
python main.py
```

### Production (Gunicorn)

```bash
# Basic Gunicorn
gunicorn main:app

# With workers and binding
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# Recommended production settings
gunicorn -w 4 --threads 2 -b 0.0.0.0:8000 --log-level info main:app
```

**Gunicorn Options:**
- `-w 4`: 4 worker processes
- `--threads 2`: 2 threads per worker
- `-b 0.0.0.0:8000`: Bind to all interfaces on port 8000
- `--log-level info`: Logging level

---

## Deployment

### Heroku Deployment

1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set SQLALCHEMY_DATABASE_URI="your-database-uri"
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Initialize Database**
   ```bash
   heroku run python
   >>> from main import app, db
   >>> with app.app_context():
   >>>     db.create_all()
   ```

### Railway Deployment

1. Connect GitHub repository
2. Set environment variables in Railway dashboard
3. Railway auto-detects `Procfile` and deploys

### Render Deployment

1. Create new Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn main:app`
5. Configure environment variables

---

## Procfile

The `Procfile` tells platforms like Heroku how to run the app:

```
web: gunicorn main:app
```

**Explanation:**
- `web`: Dyno type (web process)
- `gunicorn`: WSGI HTTP server
- `main:app`: Module and Flask app instance

---

## Database Configuration

### SQLite (Development)

```bash
SQLALCHEMY_DATABASE_URI=sqlite:///data/library.sqlite
```

### PostgreSQL (Production Recommended)

```bash
# Heroku provides DATABASE_URL automatically
SQLALCHEMY_DATABASE_URI=${DATABASE_URL}

# Or manually set
SQLALCHEMY_DATABASE_URI=postgresql://user:password@host:5432/dbname
```

### MySQL

```bash
SQLALCHEMY_DATABASE_URI=mysql://user:password@host:3306/dbname
```

---

## Security Best Practices

### Secret Key Generation

```python
import secrets
print(secrets.token_hex(32))
# Output: 64-character random hex string
```

### Environment Variable Security

- **Never commit `.env` files to version control**
- Add `.env` to `.gitignore`
- Use platform-specific secret management in production
- Rotate keys regularly

### Database Security

- Use strong database passwords
- Restrict database access by IP (production)
- Enable SSL for database connections
- Regular backups

---

## Database Migrations in Production

```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade

# On Heroku
heroku run flask db upgrade
```

---

## Monitoring and Logging

### Gunicorn Logging

```bash
# Log to file
gunicorn main:app --log-file app.log --log-level info

# Access and error logs
gunicorn main:app --access-logfile access.log --error-logfile error.log
```

### Application Logging

Add to `main.py`:

```python
import logging

if not app.debug:
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

---

## Performance Optimization

### Recommended Gunicorn Workers

```python
# Formula: (2 x $num_cores) + 1
# For 2 cores: (2 x 2) + 1 = 5 workers
gunicorn -w 5 main:app
```

### Database Connection Pooling

Add to configuration:

```python
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
```

### Static File Serving

Use a CDN or nginx for static files in production.

---

## Troubleshooting

### Environment Variables Not Loading

```bash
# Check variables are set
echo $SECRET_KEY

# Heroku
heroku config

# Railway
railway variables
```

### Database Connection Errors

```bash
# Test database connection
python -c "from main import db; print('Connected')"
```

### Gunicorn Worker Timeout

```bash
# Increase timeout for slow operations
gunicorn main:app --timeout 120
```

---

## Project Structure

```
library_app_production/
├── main.py                  # Production entry point
├── Procfile                 # Platform deployment config
├── data_models.py           # SQLAlchemy models
├── allwebforms.py           # WTForms definitions
├── author/                  # Author blueprint
├── book/                    # Book blueprint
├── post/                    # Post blueprint
├── user/                    # User blueprint
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── requirements.txt         # Python dependencies
└── readme.md                # This file
```

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SQLALCHEMY_DATABASE_URI` | Database connection string | `sqlite:///data/library.sqlite` |
| `SECRET_KEY` | Flask secret key | `64-char-random-hex-string` |
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_DEBUG` | Debug mode | `False` |

---

## Migration from Development Version

1. Copy codebase from `db_app_api/library_app`
2. Change `app.py` to `main.py`
3. Replace hardcoded config with `os.environ.get()`
4. Add `Procfile`
5. Update `requirements.txt` with `gunicorn`
6. Test with `gunicorn main:app`
7. Deploy to platform

---

## License

MIT License - see root [LICENSE](../LICENSE) file.

---

## Author

[@macraves](https://github.com/macraves)
