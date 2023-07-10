import json
from datetime import date

from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


def index(request):
    return HttpResponse("bookstore_api")


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
