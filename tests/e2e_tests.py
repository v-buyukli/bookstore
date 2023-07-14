import os

import pytest
import requests


BASE_URL = os.getenv("API_URL", "https://bookstore0-80ca638e1301.herokuapp.com/api")
authorization = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InlTa0hwY3RsTTZwOU5MQ0w3THVrVCJ9.eyJpc3MiOiJodHRwczovL2Rldi1jYTd4ODdkai51cy5hdXRoMC5jb20vIiwic3ViIjoiRk1HMXVGVU5sQkVlQ2MweHU4bWhIRGVIeDVQNTZmc2lAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vYm9va3N0b3JlL2FwaSIsImlhdCI6MTY4OTMyOTk1MSwiZXhwIjoxNjkwMzI5OTUwLCJhenAiOiJGTUcxdUZVTmxCRWVDYzB4dThtaEhEZUh4NVA1NmZzaSIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyJ9.yb54QT7iTkMqpdpACtvyaV_pkY_xABv4TUIBiEfDWJrv2ks_IdJO6dhqON4s6H3XFB23GOxpyMWovB-f0ILZE9sWYMmui2SMs9HKeHKgJM5Iv4dkXgdWK7PT_mKvVIpgBLhKQjf_zguklvr0pXHVN3FSCJHwzs1lIVEYLtTnsAH-Rak2azt6OXdBVuGv9wlgubQ7fKP3hU2j6GfCWzOMvyGxKM-LMo8rvCcrOu3Tx7rVRJPJu8YovSpzpDmzDshzi2FglkIZvjXqxdY_Y1qNEqcpyoKlN3tmbdzjTuvCZKQXfSaco6afuxXYQvkfKiXl4RRfG5psFGVwZg58_JfxXw'

headers = {
    'Content-Type': 'application/json',
    'authorization': authorization,
}


@pytest.fixture
def book_data():
    return {
        "title": "test_book",
        "author": "test_author",
        "genre": "genre1",
        "publication_date": "2020-07-07",
    }


@pytest.fixture
def created_book(book_data):
    response = requests.post(f"{BASE_URL}/books", json=book_data, headers=headers)
    yield response
    book_id = response.json().get("id")
    requests.delete(f"{BASE_URL}/books/{book_id}", headers=headers)


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
        "publication_date": "2023-01-01",
    }

    response = requests.put(f"{BASE_URL}/books/{book_id}", json=updated_data, headers=headers)
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

    response = requests.delete(f"{BASE_URL}/books/{book_id}", headers=headers)
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
    assert "author" in response.text
