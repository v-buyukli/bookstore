import json
from datetime import date
from functools import wraps
from urllib.parse import quote_plus, urlencode

import jwt
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def index(request):
    s = request.session.get("user")
    return render(
        request,
        "index.html",
        context={
            "session": s,
            "pretty": json.dumps(s, indent=4),
        },
    )


def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    return redirect(request.build_absolute_uri(reverse("index")))


def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )


def logout(request):
    request.session.clear()
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )


def get_token_auth_header(request):
    auth = request.META.get("HTTP_AUTHORIZATION", "None")
    parts = auth.split()
    token = parts[1]
    return token


def requires_scope(required_scope):
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse(
                {"message": "You don't have access to this resource"}
            )
            response.status_code = 403
            return response

        return decorated

    return require_scope


class BooksView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        params = {"title", "author", "genre"}
        if not set(request.GET.keys()).issubset(params):
            return JsonResponse(
                {"error": "invalid query params"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            queryset = Book.objects.all()
            if not queryset.exists():
                return JsonResponse({"msg": "no books yet"}, status=status.HTTP_200_OK)

        title = request.GET.get("title")
        author = request.GET.get("author")
        genre = request.GET.get("genre")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__name__icontains=author)
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        if not queryset.exists():
            return JsonResponse(
                {"msg": "no books found by filters"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        author_name = serializer.validated_data.pop("author")
        author, _ = Author.objects.get_or_create(name=author_name["name"])

        book = Book.objects.create(
            title=serializer.validated_data["title"],
            author=author,
            genre=serializer.validated_data["genre"],
            publication_date=serializer.validated_data.get(
                "publication_date", date.today()
            ),
        )
        cache.clear()
        return JsonResponse(
            {"id": book.id, "msg": "book added successfully"},
            status=status.HTTP_201_CREATED,
        )


class BookView(View):
    @method_decorator(cache_page(60 * 15))
    def get(self, request, id):
        try:
            book = Book.objects.get(id=id)
            book_data = {
                "id": book.id,
                "title": book.title,
                "author": book.author.name,
                "genre": book.genre,
                "publication_date": book.publication_date,
            }
            return JsonResponse(book_data)
        except Book.DoesNotExist:
            return JsonResponse(
                {"error": "book not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, id):
        try:
            book = Book.objects.get(id=id)
            try:
                request_body = json.loads(request.body)
            except ValueError:
                return JsonResponse(
                    {"error": "invalid json"}, status=status.HTTP_400_BAD_REQUEST
                )

            params = {"title", "author", "genre", "publication_date"}
            if not set(request_body.keys()).issubset(params):
                return JsonResponse(
                    {"error": "invalid query params"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if "title" in request_body:
                book.title = request_body["title"]
            if "author" in request_body:
                author_name = request_body["author"]
                author, created = Author.objects.get_or_create(name=author_name)
                book.author = author
            if "genre" in request_body:
                book.genre = request_body["genre"]
            if "publication_date" in request_body:
                try:
                    date.fromisoformat(request_body["publication_date"])
                except ValueError:
                    return JsonResponse(
                        {"error": "date should be yyyy-mm-dd"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                book.publication_date = request_body["publication_date"]

            book.save()
            cache.clear()
            return JsonResponse(
                {"msg": "book updated successfully"}, status=status.HTTP_200_OK
            )
        except Book.DoesNotExist:
            return JsonResponse(
                {"error": "book not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, id):
        try:
            book = Book.objects.get(id=id)
            book.delete()
            cache.clear()
            return JsonResponse(
                {"msg": "book deleted successfully"}, status=status.HTTP_200_OK
            )
        except Book.DoesNotExist:
            return JsonResponse(
                {"error": "book not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AuthorsView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        params = {"name"}
        if not set(request.GET.keys()).issubset(params):
            return JsonResponse(
                {"error": "invalid query params"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            queryset = Author.objects.all()
            if not queryset.exists():
                return JsonResponse(
                    {"msg": "no authors yet"}, status=status.HTTP_200_OK
                )

        name = request.GET.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        if not queryset.exists():
            return JsonResponse(
                {"msg": "no authors found by filters"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AuthorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthorView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request, id):
        try:
            author = Author.objects.get(id=id)
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        except Author.DoesNotExist:
            return JsonResponse(
                {"error": "author not found"}, status=status.HTTP_404_NOT_FOUND
            )
