import os

import pytest
import requests


BASE_URL = os.getenv("API_URL", "https://bookcstore-p-caching-coebpzxhw.herokuapp.com/api")
# BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")


@pytest.fixture
def book_data():
    return {
        "title": "test_book",
        "author": "author1",
        "genre": "genre1",
        "publication_date": "2020-07-07",
    }


@pytest.fixture
def created_book(book_data):
    response = requests.post(f"{BASE_URL}/books", json=book_data)
    yield response
    book_id = response.json().get("id")
    requests.delete(f"{BASE_URL}/books/{book_id}")


def test_create_book(created_book):
    response = created_book
    assert response.status_code == 201

    book_id = response.json().get("id")
    assert book_id is not None

    response = requests.get(f"{BASE_URL}/books/{book_id}")
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["title"] == "test_book"
    assert response_body["author"] == "author1"
    assert response_body["genre"] == "genre1"
    assert response_body["publication_date"] == "2020-07-07"


def test_get_all_books():
    response = requests.get(f"{BASE_URL}/books")
    assert response.status_code == 200
    assert "test_book" in response.text


def test_get_book_by_id():
    response = requests.get(f"{BASE_URL}/books/1")
    assert response.status_code == 200
    assert "test_book" in response.text


def test_update_book(created_book):
    response = created_book
    book_id = response.json().get("id")

    updated_data = {
        "title": "updated_book",
        "author": "updated_author",
        "genre": "updated_genre",
        "publication_date": "2023-01-01",
    }

    response = requests.put(f"{BASE_URL}/books/{book_id}", json=updated_data)
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 200

    response_body = response.json()
    assert response_body["title"] == updated_data["title"]
    assert response_body["author"] == updated_data["author"]
    assert response_body["genre"] == updated_data["genre"]
    assert response_body["publication_date"] == updated_data["publication_date"]


def test_delete_book(created_book):
    response = created_book
    book_id = response.json().get("id")

    response = requests.delete(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 200

    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 404
    assert "book not found" in response.text


def test_get_all_authors():
    response = requests.get(f"{BASE_URL}/authors")
    assert response.status_code == 200
    assert "test_author" in response.text


def test_get_author_by_id():
    response = requests.get(f"{BASE_URL}/authors/1")
    assert response.status_code == 200
    assert "test_author" in response.text
