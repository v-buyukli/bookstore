from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r"orders", views.OrdersViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("", include(router.urls)),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("callback/", views.callback, name="callback"),
    path("token/", views.token, name="token"),
    path("order/", csrf_exempt(views.OrderView.as_view())),
    path(
        "monobank/callback",
        csrf_exempt(views.OrderCallbackView.as_view()),
        name="mono_callback",
    ),
    path("books", csrf_exempt(views.BooksView.as_view()), name="books"),
    path("books/<int:id>", csrf_exempt(views.BookView.as_view()), name="book"),
    path("authors", csrf_exempt(views.AuthorsView.as_view()), name="authors"),
    path("authors/<int:id>", csrf_exempt(views.AuthorView.as_view()), name="author"),
]
