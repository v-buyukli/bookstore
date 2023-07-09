from datetime import date

from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


def index(request):
    return HttpResponse("bookstore_api")


class BooksView(APIView):
    def get(self, request):
        if request.GET:
            params = {"title", "author", "genre"}
            if not set(request.GET.keys()).issubset(params):
                return JsonResponse(
                    {"error": "invalid query params"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = Book.objects.all()
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
                    {"msg": "no books found by filters"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            queryset = Book.objects.all()
            if not queryset:
                return JsonResponse({"msg": "no books yet"}, status=status.HTTP_200_OK)

        books = [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author.name,
                "genre": book.genre,
                "publication_date": book.publication_date,
            }
            for book in queryset
        ]
        return Response(books, status=status.HTTP_200_OK)

    def post(self, request):
        book_serializer = BookSerializer(data=request.data)
        book_serializer.is_valid(raise_exception=True)

        author_serializer = AuthorSerializer(data=request.data)
        author_serializer.is_valid(raise_exception=True)
        author_name = author_serializer.validated_data.get("author")
        author, created = Author.objects.get_or_create(name=author_name)

        book = Book.objects.create(
            title=book_serializer.validated_data["title"],
            author=author,
            genre=book_serializer.validated_data["genre"],
            publication_date=book_serializer.validated_data.get(
                "publication_date", date.today()
            ),
        )
        return JsonResponse(
            {"id": book.id, "msg": "book added successfully"},
            status=status.HTTP_201_CREATED,
        )


class BookView(APIView):
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
            return Response(book_data)
        except Book.DoesNotExist:
            return JsonResponse(
                {"error": "book not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, id):
        try:
            params = {"title", "author", "genre", "publication_date"}
            if not set(request.body.keys()).issubset(params):
                return JsonResponse(
                    {"error": "invalid query params"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            book_serializer = BookSerializer(data=request.data)
            book_serializer.is_valid(raise_exception=True)
            book = Book.objects.get(id=id)

            if "title" in request.body:
                book.title = book_serializer.validated_data["title"]
            if "author" in request.body:
                author_serializer = AuthorSerializer(data=request.data)
                author_serializer.is_valid(raise_exception=True)
                author_name = author_serializer.validated_data.get("author")
                author, created = Author.objects.get_or_create(name=author_name)
                book.author = author
            if "genre" in request.body:
                book.genre = book_serializer.validated_data["genre"]
            if "publication_date" in request.body:
                book.publication_date = book_serializer.validated_data.get(
                    "publication_date", date.today()
                )

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
    def get(self, request):
        if request.GET:
            params = {"name"}
            if not set(request.GET.keys()).issubset(params):
                return JsonResponse(
                    {"error": "invalid query params"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = Author.objects.all()
            name = request.GET.get("name")

            if name:
                queryset = queryset.filter(name__icontains=name)
            if not queryset.exists():
                return JsonResponse(
                    {"msg": "no authors found by filters"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            queryset = Author.objects.all()
            if not queryset:
                return JsonResponse(
                    {"msg": "no authors yet"}, status=status.HTTP_200_OK
                )

        authors = [
            {
                "id": author.id,
                "name": author.name,
            }
            for author in queryset
        ]
        return Response(authors, status=status.HTTP_200_OK)


class AuthorView(APIView):
    def get(self, request, id):
        try:
            author = Author.objects.get(id=id)
            author_data = {"id": author.id, "name": author.name}
            return Response(author_data)
        except Author.DoesNotExist:
            return JsonResponse(
                {"error": "author not found"}, status=status.HTTP_404_NOT_FOUND
            )
