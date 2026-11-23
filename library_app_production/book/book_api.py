"""Request book cover data from RapidAPI by book ISBN."""
import logging
import os

import requests

logger = logging.getLogger(__name__)


class ResponseError(Exception):
    """Raised when the book cover API returns a non-200 response."""

    def __init__(self, status_code, message):
        """Store the HTTP status code and error message.

        Args:
            status_code (int): HTTP status code returned by the API.
            message (str): Error message returned by the API.
        """
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message


BOOK_API_KEY = os.environ.get("RAPIDAPI_KEY")
BOOK_COVER_API = "https://book-cover-api2.p.rapidapi.com/api/public/books/v1/cover/url"


def get_book_cover_url(isbn):
    """Get a book cover URL by ISBN.

    Args:
        isbn (str): ISBN of the book.

    Returns:
        str | None: Cover URL, or None when no ISBN or no RAPIDAPI_KEY is set.

    Raises:
        ResponseError: If the API returns a non-200 status.
        requests.RequestException: On network errors and timeouts.
    """
    if not isbn or not BOOK_API_KEY:
        return None
    querystring = {"isbn": isbn}

    headers = {
        "X-RapidAPI-Key": BOOK_API_KEY,
        "X-RapidAPI-Host": "book-cover-api2.p.rapidapi.com",
    }

    response = requests.get(
        BOOK_COVER_API, headers=headers, params=querystring, timeout=5
    )
    if response.status_code != 200:
        try:
            message = response.json().get("message", "")
        except (ValueError, AttributeError):
            message = response.text[:200]
        raise ResponseError(status_code=response.status_code, message=message)
    return response.json()["url"]


def find_cover_url(isbn):
    """Look up a cover URL without ever raising.

    A failed lookup must not stop a book from being saved.

    Args:
        isbn (str): ISBN of the book.

    Returns:
        str | None: Cover URL, or None when the lookup is not possible or fails.
    """
    try:
        return get_book_cover_url(isbn)
    except (
        requests.RequestException,
        ResponseError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        logger.warning("Cover lookup failed for ISBN %s: %s", isbn, exc)
        return None
