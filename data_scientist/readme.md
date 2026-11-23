# Flight Delay Analysis (archived copy)

This folder holds the original code, in `CodioSkySql/`. The maintained version now lives in its own repository, with a synthetic sample database, tests and a README that documents known issues:

**[macraves/flight-data-analysis](https://github.com/macraves/flight-data-analysis)**

## What the code does

- A command-line menu (`main.py`) built from the functions in `flight_data.py`. It draws delay charts with matplotlib and seaborn and saves a folium route map for one origin airport.
- A Flask API (`flight_data_app.py`) with routes to read, add, update and delete flights and to list flights by date.
- A data-access class (`data.py`) that runs every query through SQLAlchemy with bound parameters. The SQL lives in `query_list.py`.

The original course database is not included, so the code cannot run from this folder alone. Use the new repository, which generates a synthetic database.
