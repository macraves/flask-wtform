"""Regression tests for case OC005 (storage-app-user bugs).

All storage goes to pytest ``tmp_path``; OMDb and ``input``/``getpass`` are
mocked, so the real registry, STORAGE folder and API are never touched.
"""
import builtins

import pytest

import ioput
import movie_user_app as app
import movies_storage as ms
from storage import StorageCsv, StorageJson


@pytest.fixture(params=[StorageJson, StorageCsv], ids=["json", "csv"])
def storage(request, tmp_path):
    """Return an empty storage of each kind rooted in tmp_path."""
    return request.param(str(tmp_path / "user"))


def _answer(monkeypatch, text):
    """Make every ``input()`` call return ``text``."""
    monkeypatch.setattr(builtins, "input", lambda prompt="": text)


def _omdb(monkeypatch, **overrides):
    """Mock the OMDb lookup with a valid record plus ``overrides``."""
    record = {"Title": "Alien", "Year": "1979", "imdbRating": "8.5",
              "Poster": "http://x/a.jpg", "Response": "True"}
    record.update(overrides)
    monkeypatch.setattr(ms, "get_by_name", lambda name: dict(record))


# --- N/A rating on Add -----------------------------------------------------

def test_add_movie_with_na_rating_is_rejected_not_crash(storage, monkeypatch):
    """OMDb 'N/A' rating raises AppError (caught by the menu), stores nothing."""
    _omdb(monkeypatch, imdbRating="N/A")
    _answer(monkeypatch, "alien")
    with pytest.raises(app.AppError):
        app.MovieApp(storage).add_movie()
    assert storage.list_movies() == {}


def test_add_movie_with_valid_rating_still_works(storage, monkeypatch):
    """Control: a numeric rating is stored as before."""
    _omdb(monkeypatch)
    _answer(monkeypatch, "alien")
    assert "added successfully" in app.MovieApp(storage).add_movie()
    assert float(storage.list_movies()["Alien"]["imdbRating"]) == 8.5


# --- Stat on empty collection ---------------------------------------------

def test_stat_on_empty_collection_raises_function_error(storage):
    """Empty collection gives FunctionErrors, not a bare ValueError."""
    with pytest.raises(ms.FunctionErrors):
        ms.get_stat_movies(storage)


def test_stat_with_movies_still_works(storage):
    """Control: stats on a filled collection are unchanged."""
    storage.add_movie("A", "2000", 6.0, "p")
    storage.add_movie("B", "2001", 8.0, "p")
    out = ms.get_stat_movies(storage)
    assert "Max rating: 8.0" in out and "Min rating: 6.0" in out
    assert "Average rating: 7.00" in out


# --- Sort KeyError ---------------------------------------------------------

@pytest.mark.parametrize("choice", ["asc", "ASC", " Asc ", "desc", "DESC", "Desc"])
def test_sort_accepts_any_case(storage, monkeypatch, choice):
    """Any case and surrounding spaces of asc/desc sort without KeyError."""
    storage.add_movie("Low", "2000", 1.0, "p")
    storage.add_movie("High", "2001", 9.0, "p")
    _answer(monkeypatch, choice)
    lines = ms.get_sort_movies(storage).splitlines()
    first = "Low" if choice.strip().lower() == "asc" else "High"
    assert first in lines[0]


def test_sort_invalid_choice_raises_function_error(storage, monkeypatch):
    """Control: an invalid order still raises FunctionErrors."""
    _answer(monkeypatch, "sideways")
    with pytest.raises(ms.FunctionErrors):
        ms.get_sort_movies(storage)


# --- Password echo ---------------------------------------------------------

def test_password_is_read_without_echo(monkeypatch):
    """The password prompt uses getpass, the name prompt uses input."""
    seen = {}

    def fake_getpass(prompt=""):
        """Record the getpass prompt and return a fixed password."""
        seen["prompt"] = prompt
        return "s3cret"

    monkeypatch.setattr(ioput.getpass, "getpass", fake_getpass)

    def fake_input(prompt=""):
        """Fail if the password prompt ever goes through input()."""
        assert "password" not in prompt.lower(), "password read via input()"
        return "Bob"

    monkeypatch.setattr(builtins, "input", fake_input)
    data = app.get_name_and_password()
    assert data == {"username": "Bob", "password": "s3cret"}
    assert "password" in seen["prompt"].lower()


def test_empty_password_reprompts(monkeypatch):
    """An empty password is rejected and asked again."""
    answers = iter(["", "ok"])
    monkeypatch.setattr(ioput.getpass, "getpass", lambda prompt="": next(answers))
    assert ioput.read_password("pw: ") == "ok"


# --- HTML escaping and quoting --------------------------------------------

def test_title_is_escaped_in_html():
    """A hostile title cannot inject markup."""
    html_out = ms.create_movies_list_html(
        {"<script>alert(1)</script>": {"Year": "2000", "Poster": "p.jpg"}})
    assert "<script>" not in html_out
    assert "&lt;script&gt;" in html_out


def test_year_is_escaped_in_html():
    """Year comes from the API/CSV too and is escaped."""
    html_out = ms.create_movies_list_html(
        {"A": {"Year": "<b>1</b>", "Poster": "p.jpg"}})
    assert "<b>1</b>" not in html_out


def test_poster_is_quoted_and_cannot_break_out():
    """Poster is a quoted, escaped attribute; a space/onerror cannot add one."""
    poster = "x.jpg onerror=alert(1)"
    html_out = ms.create_movies_list_html(
        {"A": {"Year": "2000", "Poster": poster}})
    assert 'src="x.jpg onerror=alert(1)"' in html_out
    quote_poster = 'x.jpg" onerror="alert(1)'
    html_out = ms.create_movies_list_html(
        {"A": {"Year": "2000", "Poster": quote_poster}})
    assert '" onerror="' not in html_out
    assert "&quot;" in html_out


def test_normal_movie_html_still_renders():
    """Control: a normal movie keeps its title, year and poster."""
    html_out = ms.create_movies_list_html(
        {"Alien": {"Year": "1979", "Poster": "http://x/a.jpg"}})
    assert 'src="http://x/a.jpg"' in html_out
    assert ">Alien<" in html_out and ">1979<" in html_out
