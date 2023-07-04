from datetime import date

from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name")


class BookSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.name")

    class Meta:
        model = Book
        fields = ("id", "title", "author", "genre", "publication_date")


class BooksView(APIView):
    def get(self, request):
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
                {"msg": "no books found by filters"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        author_name = serializer.validated_data.get("author")
        author, created = Author.objects.get_or_create(name=author_name)

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


class BookView(APIView):
    def get(self, request, id):
        try:
            book = Book.objects.get(id=id)
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return JsonResponse(
                {"error": "book not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, id):
        try:
            book = Book.objects.get(id=id)
            serializer = BookSerializer(book, data=request.data, partial=True)
            if not serializer.is_valid():
                return JsonResponse(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            author_name = serializer.validated_data.get("author")
            if author_name:
                author, created = Author.objects.get_or_create(name=author_name)
                serializer.validated_data["author"] = author

            serializer.save()
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
        queryset = Author.objects.all()
        name = request.GET.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if not queryset.exists():
            return JsonResponse(
                {"msg": "no authors found by filters"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AuthorSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthorView(APIView):
    def get(self, request, id):
        try:
            author = Author.objects.get(id=id)
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        except Author.DoesNotExist:
            return JsonResponse(
                {"error": "author not found"}, status=status.HTTP_404_NOT_FOUND
            )
