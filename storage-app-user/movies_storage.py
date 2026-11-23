"""Methods for stored objects in a file."""
import html
import os
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from storage import json

# Picks up OMDB_API_KEY from the nearest .env file in this or a parent folder
load_dotenv()
YOUR_API_KEY = os.environ.get("OMDB_API_KEY")
BASE_URL = "https://www.omdbapi.com"


class FunctionErrors(Exception):
    """FunctionErrors is a class for raising errors."""

    def __init__(self, message: object) -> None:
        """Create the error with a message.

        Args:
            message (object): Error description.
        """
        super().__init__(message)


def get_name_method_requests(method_name: str, movie_name: str) -> str:
    """Build the OMDb search URL for a movie name.

    Args:
        method_name (str): "name" string.
        movie_name (str): given string by user.

    Returns:
        str: returns whole url modified by user input.

    Raises:
        FunctionErrors: If OMDB_API_KEY is not set.
    """
    if not YOUR_API_KEY:
        raise FunctionErrors("OMDB_API_KEY environment variable is not set")
    method_api = {
        "name": f"{BASE_URL}/?{urlencode({'t': movie_name, 'apikey': YOUR_API_KEY})}"
    }
    if method_name in method_api:
        return method_api[method_name]
    return None


def get_by_name(movie_name: str) -> dict:
    """Fetch a movie from OMDb by title.

    Args:
        movie_name (str): given string by user.

    Returns:
        parsed_data: returns dictionary of movie.
    """
    request_api = get_name_method_requests("name", movie_name)
    if request_api is not None:
        try:
            response = requests.get(request_api, timeout=5)
            parsed_data = json.loads(response.text)
            # Check for HTTP error status codes
            response.raise_for_status()
            response_status = parsed_data.get("Response", "Unknown")
            title_status = parsed_data.get("Title", "Unknown")
            # Unvalid user text returns Response: False
            if not response_status == "True" or title_status == "Unknown":
                raise FunctionErrors(
                    f"Entered movie name: {movie_name} has no response")
            return parsed_data
        except requests.exceptions.RequestException as rer:
            raise FunctionErrors(
                f"Error requesting page {request_api}:\n\t--> {rer}") from rer
    return None


def get_sort_movies(instance):
    """Sort the stored movies by rating in the order the user picks.

    Args:
        instance: Storage instance providing list_movies().

    Returns:
        str: Numbered list of sorted movies.

    Raises:
        FunctionErrors: If the sorting input is not 'asc' or 'desc'.
    """
    data = instance.list_movies()
    valid_entries = {"asc": False, "desc": True}
    user_choice = input("Enter the order of sorting 'asc' or 'desc': ")
    if not user_choice.strip().lower() in valid_entries:
        raise FunctionErrors("Invalid sorting input")

    sorted_movies = sorted(
        data.items(), key=lambda x: float(x[1]['imdbRating']),
        reverse=valid_entries[user_choice])
    return "\n".join(
        f"{item[0]}. {item[1][0]}, Year: {item[1][1]['Year']}, Rating: {item[1][1]['imdbRating']}"
        for item in enumerate(sorted_movies, start=1))


def get_stat_movies(instance):
    """Return max, min and average rating of the stored movies.

    Args:
        instance: Storage instance providing list_movies().

    Returns:
        str: Formatted rating statistics.
    """
    data = instance.list_movies()
    max_rating = max(data.values(), key=lambda x: float(x['imdbRating']))
    min_rating = min(data.values(), key=lambda x: float(x['imdbRating']))
    average_rating = sum(float(item['imdbRating'])
                         for item in data.values()) / len(data)

    return f"""Max rating: {max_rating['imdbRating']}
Min rating: {min_rating['imdbRating']}
Average rating: {average_rating:.2f}"""


def create_movies_list_html(movies):
    """Create a list of movies in html format.

    Args:
        movies (dict): Movies keyed by title.

    Returns:
        str: HTML list items for the movie grid.
    """
    # target = "__TEMPLATE_MOVIE_GRID__"
    html_code = []
    for key, value in movies.items():
        template = '''<li>
            <div class="movie">
                <img class="movie-poster"
                     src={poster}
                     title=""/>
                <div class="movie-title">{title}</div>
                <div class="movie-year">{year}</div>
            </div>
        </li>'''
        title = key
        year = value["Year"]
        poster = value["Poster"]

        template = template.format(
            poster=poster, title=title, year=year)
        html_code.append(template)
    return "\n".join(html_code)


def replace_in_html(user, replacement):
    """Replace target in html file with replacement.

    Args:
        user: User object providing template and output paths.
        replacement (str): HTML to insert into the movie grid.
    """
    with open(user.get_html_index(), "r", encoding="utf-8") as current_html:
        with open(user.get_updated_path(), "w", encoding="utf-8") as new_html:
            source_html = current_html.read()
            owner = html.escape(user.user_name)
            updated_html = source_html.replace(
                "__TEMPLATE_TITLE__", f"{owner}'s Movie Database")
            updated_html = updated_html.replace(
                "__TEMPLATE_MOVIE_GRID__", replacement)
            new_html.write(updated_html)


def create_webpage(user, instance):
    """Generate the user's movie webpage.

    Args:
        user: User object providing template and output paths.
        instance: Storage instance providing list_movies().

    Returns:
        str: Success message.
    """
    movies_data = instance.list_movies()
    html_str = create_movies_list_html(movies_data)
    replace_in_html(user, html_str)
    return "HTML file created successfully"
