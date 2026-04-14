# Flask & Python Portfolio

Professional portfolio showcasing full-stack Flask applications, REST APIs, database management, and Python development skills.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Projects Overview

| Project | Description | Tech Stack | Status | Quick Start |
|---------|-------------|------------|--------|-------------|
| **[backend_api](./backend_api)** | REST API with version control system for blog posts | Flask, Flask-CORS, Faker | ✅ Complete | [View README](./backend_api/readme.md) |
| **[db_app_api](./db_app_api)** | Full-stack library management system with admin controls | Flask, SQLAlchemy, WTForms, CKEditor | ✅ Complete | [View README](./db_app_api/Library%20app/readme.md) |
| **[first-deployment](./first-deployment)** | Production-ready library app with Gunicorn | Flask, SQLAlchemy, Gunicorn | ✅ Complete | [View README](./first-deployment/readme.md) |
| **[masterblog](./masterblog)** | Simple blog CRUD with JSON storage | Flask, WTForms | ✅ Complete | [View README](./masterblog/README.md) |
| **[movie_wep_app_multi_storage_support](./movie_wep_app_multi_storage_support)** | Movie management with multi-storage support (SQLite/JSON/CSV) | Flask, SQLAlchemy, Flask-Login, OMDb API | ✅ Complete | [View README](./movie_wep_app_multi_storage_support/README.md) |
| **[data_scientiest](./data_scientiest)** | SQLite flight data analysis with visualizations | SQLite3, SQLAlchemy, matplotlib, folium | ✅ Complete | [View README](./data_scientiest/readme.md) |
| **[Best-Buy](./Best-Buy)** | E-commerce inventory management CLI (Python OOP) | Python, unittest | ✅ Complete | [View README](./Best-Buy/README.md) |
| **[storage-app-user](./storage-app-user)** | Movie collection manager CLI with API integration | Python, Requests, OMDb API | ✅ Complete | [View README](./storage-app-user/README.md) |

---

## Key Skills Demonstrated

### Backend Development
- RESTful API design and implementation
- Version control in APIs
- Database design and ORM (SQLAlchemy)
- Authentication and authorization (Flask-Login)
- Blueprint architecture for modular Flask apps

### Data Management
- Multi-storage backend abstraction (SQLite, JSON, CSV)
- Database migrations (Flask-Migrate, Alembic)
- Parameterized SQL queries (SQL injection prevention)
- Relational database design with foreign keys

### Frontend Integration
- WTForms for form validation
- Bootstrap for responsive design
- CKEditor for rich text editing
- Jinja2 templating
- Session management

### DevOps & Deployment
- Gunicorn WSGI server configuration
- Environment variable management
- Production vs development configurations
- CORS handling

### Data Science & Visualization
- SQLite3 data analysis
- Matplotlib for charts
- Folium for geographic visualizations
- Data transformation and aggregation

---

## Quick Start

Each project contains its own `requirements.txt` and detailed README. General setup:

```bash
# Clone repository
git clone https://github.com/macraves/flask-wtform.git
cd flask-wtform

# Navigate to specific project
cd [project-name]

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application (check project README for specific commands)
python app.py  # or main.py depending on project
```

---

## Technology Stack

**Backend**: Python 3.8+, Flask 3.0+, SQLAlchemy 2.0, Flask-Login, Flask-Migrate

**Forms & Validation**: Flask-WTF, WTForms

**Database**: SQLite3, MySQL (configurable)

**Frontend**: Bootstrap, Jinja2, CKEditor

**APIs**: Flask-CORS, Requests, OMDb API

**Data Science**: matplotlib, folium, pandas

**Testing**: unittest, Faker

**Deployment**: Gunicorn

---

## Project Highlights

### Advanced Features
- **Abstract Storage Pattern**: Implemented in `movie_wep_app_multi_storage_support` for seamless switching between SQLite, JSON, and CSV backends
- **API Versioning**: Custom version control system in `backend_api` supporting multiple data schemas
- **Role-Based Access**: Admin controls in `db_app_api` with user-specific permissions
- **Production Ready**: Environment-based configuration in `first-deployment` with Gunicorn integration

### Best Practices
- Parameterized queries for SQL injection prevention
- Blueprint architecture for scalable Flask applications
- Comprehensive error handling with custom exception classes
- Type hints and docstrings for code documentation
- Unit testing coverage

---

## Contact & Links

**GitHub**: [@macraves](https://github.com/macraves)

**Repository**: [flask-wtform](https://github.com/macraves/flask-wtform)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Projects developed as part of continuous learning in web development and software engineering. Special thanks to the Flask and SQLAlchemy communities.
