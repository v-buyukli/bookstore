from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import AuthorsView, AuthorView, BooksView, BookView, index, public, private


urlpatterns = [
    path("", index, name="index"),
    path("public", public, name="public"),
    path("private", private, name="private"),
    path("books", csrf_exempt(BooksView.as_view()), name="books"),
    path("books/<int:id>", csrf_exempt(BookView.as_view()), name="book"),
    path("authors", csrf_exempt(AuthorsView.as_view()), name="authors"),
    path("authors/<int:id>", csrf_exempt(AuthorView.as_view()), name="author"),
]
