"""Request book cover data from RapidAPI by book ISBN."""
import os

import requests


class ResponseError(Exception):
    """Raised when the book cover API returns a non-200 response."""

    def __init__(self, status_code, message):
        """Store the HTTP status code and error message.

        Args:
            status_code (int): HTTP status code returned by the API.
            message (str): Error message returned by the API.
        """
        self.status_code = status_code
        self.message = message


API_KEY = os.environ.get("RAPIDAPI_KEY")
BASE_URL = "https://book-cover-api2.p.rapidapi.com/api/public/books/v1/cover/url"


def get_book_cover_url(isbn):
    """Get a book cover URL by ISBN.

    Args:
        isbn (str): ISBN of the book.

    Returns:
        str | None: Cover URL, or None when no ISBN or no RAPIDAPI_KEY is set.

    Raises:
        ResponseError: If the API returns a non-200 status.
    """
    if not isbn or not API_KEY:
        return None
    querystring = {"isbn": isbn}

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "book-cover-api2.p.rapidapi.com",
    }

    response = requests.get(BASE_URL, headers=headers, params=querystring, timeout=5)
    if response.status_code != 200:
        raise ResponseError(
            status_code=response.status_code, message=response.json()["message"]
        )
    book_cover_json = response.json()
    return book_cover_json["url"]
