import os

import pytest
import requests
from django.conf import settings


BASE_URL = os.getenv("API_URL", "https://bookstore0-80ca638e1301.herokuapp.com/api")
HEADERS = {
    "Content-Type": "application/json",
    "authorization": settings.AUTHORIZATION_HEADER,
}


@pytest.fixture
def book_data():
    return {
        "title": "test_book",
        "author": "test_author",
        "genre": "genre1",
        "price": 1000,
        "quantity": 10,
        "publication_date": "2020-07-07",
    }


@pytest.fixture
def created_book(book_data):
    response = requests.post(f"{BASE_URL}/books", json=book_data, headers=HEADERS)
    yield response
    book_id = response.json().get("id")
    requests.delete(f"{BASE_URL}/books/{book_id}", headers=HEADERS)


def test_create_book(created_book):
    response = created_book
    assert response.status_code == 201

    book_id = response.json().get("id")
    assert book_id is not None

    response = requests.get(f"{BASE_URL}/books/{book_id}")
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["title"] == "test_book"
    assert response_body["author"] == "test_author"
    assert response_body["genre"] == "genre1"
    assert response_body["price"] == 1000
    assert response_body["quantity"] == 10
    assert response_body["publication_date"] == "2020-07-07"


def test_get_all_books():
    response = requests.get(f"{BASE_URL}/books")
    assert response.status_code == 200
    if "no books yet" not in response.text:
        assert "test_book" in response.text


def test_get_book_by_id(created_book):
    response = created_book
    book_id = response.json().get("id")
    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 200
    assert "test_book" in response.text


def test_update_book(created_book):
    response = created_book
    book_id = response.json().get("id")

    updated_data = {
        "title": "updated_book",
        "author": "updated_author",
        "genre": "updated_genre",
        "price": 2000,
        "quantity": 5,
        "publication_date": "2023-01-01",
    }

    response = requests.put(
        f"{BASE_URL}/books/{book_id}", json=updated_data, headers=HEADERS
    )
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 200

    response_body = response.json()
    assert response_body["title"] == updated_data["title"]
    assert response_body["author"] == updated_data["author"]
    assert response_body["genre"] == updated_data["genre"]
    assert response_body["price"] == updated_data["price"]
    assert response_body["quantity"] == updated_data["quantity"]
    assert response_body["publication_date"] == updated_data["publication_date"]


def test_delete_book(created_book):
    response = created_book
    book_id = response.json().get("id")

    response = requests.delete(f"{BASE_URL}/books/{book_id}", headers=HEADERS)
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 404
    assert "book not found" in response.text


def test_get_all_authors():
    response = requests.get(f"{BASE_URL}/authors")
    assert response.status_code == 200
    assert "test_author" in response.text


def test_get_author_by_id():
    response = requests.get(f"{BASE_URL}/authors/91")
    assert response.status_code == 200
    assert "author" in response.text


def test_get_order_info():
    order_id = 3
    response = requests.get(f"{BASE_URL}/orders/{order_id}")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["total_price"] == 5000
    assert response_data["invoice_id"] == "2307227joWLr4Da3Msdy"
    assert response_data["id"] == order_id


def test_create_order():
    order_data = {"order": [{"book_id": 598, "quantity": 5}]}

    response = requests.post(f"{BASE_URL}/order/", json=order_data)
    response_data = response.json()

    assert "url" in response_data
    assert "id" in response_data
    assert isinstance(response_data["url"], str)
    assert isinstance(response_data["id"], int)
