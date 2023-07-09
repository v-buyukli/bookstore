from datetime import date

from rest_framework import serializers


class AuthorSerializer(serializers.Serializer):
    author = serializers.CharField(max_length=255)


class BookSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    genre = serializers.CharField(max_length=255)
    publication_date = serializers.DateField(default=date.today)
