import json
from datetime import date

from django.http import HttpResponse, JsonResponse
from django.views import View

from .models import Author, Book


def index(request):
    return HttpResponse("bookstore_api")


class BooksView(View):
    def get(self, request):
        if request.GET:
            params = {"title", "author", "genre"}
            if not set(request.GET.keys()).issubset(params):
                return JsonResponse({"error": "invalid query params"}, status=400)

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
            if not queryset:
                return JsonResponse({"msg": "no books found by filters"}, status=404)
        else:
            queryset = Book.objects.all()
            if not queryset:
                return JsonResponse({"msg": "no books yet"}, status=200)

        books = []
        for book in queryset:
            books.append(
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author.name,
                    "genre": book.genre,
                    "publication_date": book.publication_date,
                }
            )
        return JsonResponse(books, safe=False, status=200)

    def post(self, request):
        try:
            request_body = json.loads(request.body)
        except ValueError:
            return JsonResponse({"error": "invalid json"}, status=400)

        title = request_body.get("title")
        author_name = request_body.get("author")
        genre = request_body.get("genre")
        publication_date = request_body.get("publication_date")

        params = {"title", "author", "genre", "publication_date"}
        if not set(request_body.keys()).issubset(params):
            return JsonResponse({"error": "invalid query params"}, status=400)
        if not title:
            return JsonResponse({"error": "missing title field"}, status=400)
        if not author_name:
            return JsonResponse({"error": "missing author field"}, status=400)
        author, created = Author.objects.get_or_create(name=author_name)
        if not genre:
            return JsonResponse({"error": "missing genre field"}, status=400)
        if publication_date:
            try:
                date.fromisoformat(publication_date)
            except ValueError:
                return JsonResponse({"error": "date should be yyyy-mm-dd"}, status=400)
        if not publication_date:
            publication_date = date.today()

        book = Book.objects.create(
            title=title,
            author=author,
            genre=genre,
            publication_date=publication_date,
        )
        return JsonResponse(
            {"id": book.id, "msg": "book added successfully"}, status=201
        )


class BookView(View):
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
            return JsonResponse({"error": "book not found"}, status=404)

    def put(self, request, id):
        try:
            book = Book.objects.get(id=id)
            try:
                request_body = json.loads(request.body)
            except ValueError:
                return JsonResponse({"error": "invalid json"}, status=400)

            params = {"title", "author", "genre", "publication_date"}
            if not set(request_body.keys()).issubset(params):
                return JsonResponse({"error": "invalid query params"}, status=400)

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
                        {"error": "date should be yyyy-mm-dd"}, status=400
                    )
                book.publication_date = request_body["publication_date"]
            book.save()
            return JsonResponse({"msg": "book updated successfully"}, status=200)
        except Book.DoesNotExist:
            return JsonResponse({"error": "book not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, id):
        try:
            book = Book.objects.get(id=id)
            book.delete()
            return JsonResponse({"msg": "book deleted successfully"}, status=200)
        except Book.DoesNotExist:
            return JsonResponse({"error": "book not found"}, status=404)


class AuthorsView(View):
    def get(self, request):
        if request.GET:
            params = {"name"}
            if not set(request.GET.keys()).issubset(params):
                return JsonResponse({"error": "invalid query params"}, status=400)
            queryset = Author.objects.all()
            name = request.GET.get("name")
            if name:
                queryset = queryset.filter(name__icontains=name)
            if not queryset:
                return JsonResponse({"msg": "no authors found by filters"}, status=404)
        else:
            queryset = Author.objects.all()
            if not queryset:
                return JsonResponse({"msg": "no authors yet"}, status=200)

        authors = []
        for author in queryset:
            authors.append(
                {
                    "id": author.id,
                    "name": author.name,
                }
            )
        return JsonResponse(authors, safe=False, status=200)


class AuthorView(View):
    def get(self, request, id):
        try:
            author = Author.objects.get(id=id)
            author_data = {"id": author.id, "name": author.name}
            return JsonResponse(author_data)
        except Author.DoesNotExist:
            return JsonResponse({"error": "author not found"}, status=404)
