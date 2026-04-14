# Flight Data Analysis with SQLite

Data science project analyzing flight delay patterns using SQLite database with interactive visualizations.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)
![matplotlib](https://img.shields.io/badge/matplotlib-3.7-orange.svg)

---

## Overview

Python data analysis application for exploring flight delay patterns from SQLite database. Features parameterized SQL queries for security, matplotlib/seaborn for statistical visualizations, and folium for geographic heat maps. Includes both CLI interface and Flask REST API backend.

---

## Features

- **SQL Injection Prevention**: Parameterized queries using SQLAlchemy
- **Multiple Visualization Types**: Bar charts, scatter plots, heat maps, geographic maps
- **Flight Delay Analysis**: Analyze delays by origin, airline, time of day, and destination
- **Interactive CLI**: Dynamic function menu generated from module reflection
- **REST API**: Flask backend exposing query endpoints
- **Geographic Visualization**: Folium-based heat maps for flight routes
- **Statistical Analysis**: Percentage calculations and trend analysis

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| SQLite3 | Database engine |
| SQLAlchemy | ORM and query builder |
| pandas | Data manipulation and analysis |
| matplotlib | Chart generation |
| seaborn | Statistical visualizations |
| folium | Geographic heat maps |
| Flask | REST API backend |

---

## Prerequisites

- Python 3.8 or higher
- SQLite database with flight data (included or provide your own)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/macraves/flask-wtform.git
cd flask-wtform/data_scientist

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

### CLI Application

```bash
cd CodioSkySql
python main.py
```

**Menu Options:**
1. Show total delayed flights by origin (with bar chart)
2. Show scatter plot of delayed flights by all origins
3. Show percentage of delayed flights per airline
4. Show percentage of delayed flights per hour of day
5. Show scatter heat map (origin-destination)
6. Show heat map of delayed flights by airline
7. Exit

### Flask API Backend

```bash
cd CodioSkySql
python flight_data_app.py
```

**API Available**: `http://localhost:5000`

---

## Project Structure

```
data_scientist/
└── CodioSkySql/
    ├── main.py                 # CLI entry point
    ├── flight_data.py          # Analysis functions
    ├── flight_data_app.py      # Flask API backend
    ├── data.py                 # Database connection and queries
    ├── query_list.py           # SQL query definitions
    ├── main_plot.py            # Visualization functions
    ├── ioput.py                # Input/output utilities
    ├── requirements.txt        # Python dependencies
    └── README.md               # This file
```

---

## Analysis Functions

### Delay Analysis by Origin

Analyzes total delayed flights from a specific airport (IATA code).

```python
# Query delayed flights from JFK
show_total_delayed_flights_by_origin(data_manager)
# Input: JFK
# Output: Bar chart of delayed flight IDs
```

### Airline Delay Statistics

Calculates percentage of delayed flights per airline.

```python
show_plot_percentage_of_delayed_flight_per_airline(data_manager)
# Output: Bar chart comparing airline delay rates
```

### Time-of-Day Analysis

Shows delay patterns across 24-hour periods.

```python
show_plot_percentage_of_delayed_flight_per_hour_of_the_day(data_manager)
# Output: Line/bar chart of delays by hour
```

### Geographic Heat Maps

Visualizes flight routes with delay intensity using folium.

```python
show_heat_map_of_delayed_flights_by_airline(data_manager)
# Output: Interactive map with route heat mapping
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/delays/<origin>` | Get delayed flights by origin airport |
| GET | `/api/airlines/delays` | Get delay statistics per airline |
| GET | `/api/delays/hourly` | Get delay patterns by hour |
| GET | `/api/routes/heatmap` | Get route delay data for mapping |

---

## SQL Security

All queries use **parameterized queries** to prevent SQL injection:

```python
# Secure query example from data.py
def get_delayed_flights_by_origin(self, origin: str):
    query = text("""
        SELECT * FROM flights
        WHERE origin = :origin AND delayed = 1
    """)
    with self.engine.connect() as conn:
        return conn.execute(query, {"origin": origin}).fetchall()
```

---

## Database Schema

Expected flight data table structure:

```sql
CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY,
    origin TEXT,
    destination TEXT,
    airline TEXT,
    delayed INTEGER,  -- 0 or 1 (boolean)
    departure_time TEXT,
    arrival_time TEXT
);
```

---

## Visualization Examples

### Matplotlib Charts
- Bar charts for delay counts
- Scatter plots for origin-destination relationships
- Line charts for temporal patterns
- Seaborn-styled statistical plots

### Folium Maps
- Heat map overlays on geographic maps
- Color-coded intensity by delay frequency
- Interactive popups with route information

---

## Configuration

### Database Connection

Edit `data.py` to configure database path:

```python
class FlightData:
    def __init__(self, db_path="flights.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
```

### Query Customization

Add custom queries in `query_list.py`:

```python
CUSTOM_QUERY = """
    SELECT origin, COUNT(*) as total
    FROM flights
    WHERE delayed = 1
    GROUP BY origin
"""
```

---

## Example Output

```bash
$ python main.py

Flight Data Analysis Menu
-------------------------
1. Show total delayed flights by origin
2. Show scatter plot of delayed flights by all origins
3. Show percentage of delayed flights per airline
4. Show percentage of delayed flights per hour of day
5. Show scatter heat map
6. Show heat map of delayed flights by airline
7. Exit

Enter your choice: 1
Enter origin airport: JFK
[Bar chart displayed with matplotlib]
Plot is shown
```

---

## Testing

Run analysis functions with sample data:

```bash
# Test database connection
python -c "from data import FlightData; fd = FlightData(); print('Connected')"

# Test query execution
python -c "from flight_data import *; test_queries()"
```

---

## License

MIT License - see root [LICENSE](../LICENSE) file.

---

## Author

[@macraves](https://github.com/macraves)
