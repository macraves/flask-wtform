"""Request book api by book.isbn """
import requests


class ResponseError(Exception):
    """Response error"""

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


BOOK_API_KEY = "4dc8562986mshccc0808b0cb1c09p140dedjsndf480963b592"
BOOK_COVER_API = "https://book-cover-api2.p.rapidapi.com/api/public/books/v1/cover/url"


def get_book_cover_url(isbn):
    """Get book cover by isbn"""
    if not isbn:
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
    """OpenAI GPT API'"""
    url = "https://ai-content-detector-ai-gpt.p.rapidapi.com/api/detectText/"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "4dc8562986mshccc0808b0cb1c09p140dedjsndf480963b592",
        "X-RapidAPI-Host": "ai-content-detector-ai-gpt.p.rapidapi.com",
    }
    payload = {"text": prompt}

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    return response.json()


def main():
    """Main flow of the program."""
    user_prompt = """Suggest me 3 books about Python programming language.
    Consider for beginners and advanced programmers."""
    response_data = send_request_to_openai(user_prompt)
    print("OpenAI'respond:")
    print(response_data)


if __name__ == "__main__":
    main()
