from unittest.mock import MagicMock

import pytest
from django.urls import reverse


@pytest.fixture
def api_client():
    class APIClient:
        def __init__(self):
            self.response = None

        def get(self, url):
            self.response = MagicMock()
            self.response.status_code = 200
            return self

        def post(self, url, data):
            self.response = MagicMock()
            self.response.status_code = 201
            return self

        def put(self, url, data):
            self.response = MagicMock()
            self.response.status_code = 200
            return self

        def delete(self, url):
            self.response = MagicMock()
            self.response.status_code = 200
            return self

        def json(self, url):
            if "books" in url:
                return {
                    "title": "test_b",
                    "author": "test_a",
                    "genre": "test_g",
                    "publication_date": "2023-07-02",
                }
            elif "authors" in url:
                return {
                    "name": "test_n",
                }

    return APIClient()


def test_get_all_books(api_client):
    url = reverse("books")
    response = api_client.get(url)
    books = response.json(url)

    assert response.response.status_code == 200
    assert books["title"] == "test_b"
    assert books["author"] == "test_a"
    assert books["genre"] == "test_g"
    assert books["publication_date"] == "2023-07-02"


def test_get_book_by_id(api_client):
    url = reverse("book", args=[0])
    response = api_client.get(url)
    book = response.json(url)

    assert response.response.status_code == 200
    assert book["title"] == "test_b"
    assert book["author"] == "test_a"
    assert book["genre"] == "test_g"


def test_create_book(api_client):
    url = reverse("books")
    new_book = {"title": "new_b", "author": "new_a", "genre": "new_g"}
    response = api_client.post(url, new_book)
    assert response.response.status_code == 201


def test_update_book(api_client):
    url = reverse("book", args=[0])
    upd_book = {
        "title": "upd_b",
        "author": "upd_a",
        "genre": "upd_g",
        "publication_date": "2000-01-01",
    }
    response = api_client.put(url, upd_book)
    assert response.response.status_code == 200


def test_delete_book(api_client):
    url = reverse("book", args=[0])
    response = api_client.delete(url)
    assert response.response.status_code == 200


def test_get_all_authors(api_client):
    url = reverse("authors")
    response = api_client.get(url)
    authors = response.json(url)

    assert response.response.status_code == 200
    assert authors["name"] == "test_n"


def test_get_author_by_id(api_client):
    url = reverse("author", args=[0])
    response = api_client.get(url)
    author = response.json(url)

    assert response.response.status_code == 200
    assert author["name"] == "test_n"
