from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("callback/", views.callback, name="callback"),
    path("books", csrf_exempt(views.BooksView.as_view()), name="books"),
    path("books/<int:id>", csrf_exempt(views.BookView.as_view()), name="book"),
    path("authors", csrf_exempt(views.AuthorsView.as_view()), name="authors"),
    path("authors/<int:id>", csrf_exempt(views.AuthorView.as_view()), name="author"),
]
