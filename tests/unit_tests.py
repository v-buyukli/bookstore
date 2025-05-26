import json
import pathlib
from unittest.mock import MagicMock

import pytest
import requests
import responses
from django.urls import reverse
from django.conf import settings
from api.models import Author, Book


root = pathlib.Path(__file__).parent


@pytest.fixture
def mocked():
    def inner(file_name):
        return json.load(open(root / "fixtures" / file_name))

    return inner


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
            author_fields = Author._meta.get_fields()
            book_fields = Book._meta.get_fields()

            if "books" in url:
                return {
                    book_fields[3].name: "test_b",
                    book_fields[4].name: "test_a",
                    book_fields[5].name: "test_g",
                    book_fields[6].name: 1000,
                    book_fields[7].name: 10,
                    book_fields[8].name: "2023-07-02",
                }
            elif "authors" in url:
                return {
                    author_fields[2].name: "test_n",
                }

    return APIClient()


def test_get_all_books(api_client):
    url = reverse("books")
    response = api_client.get(url)
    assert response.response.status_code == 200

    books = response.json(url)
    assert books["title"] == "test_b"
    assert books["author"] == "test_a"
    assert books["genre"] == "test_g"
    assert books["price"] == 1000
    assert books["quantity"] == 10
    assert books["publication_date"] == "2023-07-02"


def test_get_book_by_id(api_client):
    url = reverse("book", args=[0])
    response = api_client.get(url)
    assert response.response.status_code == 200

    book = response.json(url)
    assert book["title"] == "test_b"
    assert book["author"] == "test_a"
    assert book["genre"] == "test_g"
    assert book["price"] == 1000
    assert book["quantity"] == 10


def test_create_book(api_client):
    url = reverse("books")
    new_book = {
        "title": "new_b",
        "author": "new_a",
        "genre": "new_g",
        "price": 2000,
        "quantity": 5,
    }
    response = api_client.post(url, new_book)
    assert response.response.status_code == 201


def test_update_book(api_client):
    url = reverse("book", args=[0])
    upd_book = {
        "title": "upd_b",
        "author": "upd_a",
        "genre": "upd_g",
        "price": 2000,
        "quantity": 5,
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
    assert response.response.status_code == 200
    authors = response.json(url)
    assert authors["name"] == "test_n"


def test_get_author_by_id(api_client):
    url = reverse("author", args=[0])
    response = api_client.get(url)
    assert response.response.status_code == 200
    author = response.json(url)
    assert author["name"] == "test_n"


@responses.activate
def test_get_order_info(mocked):
    mocked_response = mocked("order_info.json")

    responses.add(
        responses.GET, f"{settings.API_URL}/orders/3", json=mocked_response, status=200
    )

    r = requests.get(f"{settings.API_URL}/orders/3")
    assert r.status_code == 200

    response_data = r.json()
    assert response_data["total_price"] == 5000
    assert response_data["invoice_id"] == "2307227joWLr4Da3Msdy"
    assert response_data["id"] == 3
    assert response_data["status"] == "success"


@responses.activate
def test_get_url_order(mocked):
    order_data = mocked("order_input.json")
    expected_result = mocked("order_url.json")

    responses.add(
        responses.POST,
        f"{settings.API_URL}/order/",
        json=expected_result,
    )

    response = requests.post(f"{settings.API_URL}/order/", json=order_data)
    response_data = response.json()
    assert response_data == expected_result
