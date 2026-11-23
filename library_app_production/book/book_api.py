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
        raise ResponseError(
            status_code=response.status_code, message=response.json()["message"]
        )
    book_cover_json = response.json()
    return book_cover_json["url"]


def send_request_to_openai(prompt):
    """Send text to the RapidAPI AI content detector.

    Args:
        prompt (str): Text to analyse.

    Returns:
        dict: Parsed JSON response from the API.
    """
    url = "https://ai-content-detector-ai-gpt.p.rapidapi.com/api/detectText/"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": BOOK_API_KEY,
        "X-RapidAPI-Host": "ai-content-detector-ai-gpt.p.rapidapi.com",
    }
    payload = {"text": prompt}

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    return response.json()


def main():
    """Run a manual check of the content detector request."""
    user_prompt = """Suggest me 3 books about Python programming language.
    Consider for beginners and advanced programmers."""
    response_data = send_request_to_openai(user_prompt)
    print("OpenAI'respond:")
    print(response_data)


if __name__ == "__main__":
    main()
