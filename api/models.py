from datetime import date

from django.db import models


class Token(models.Model):
    sub = models.CharField()
    token = models.CharField()
    created = models.DateTimeField(auto_now_add=True, blank=True)


class Author(models.Model):
    name = models.CharField(max_length=255)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.CharField(max_length=255)
    publication_date = models.DateField(default=date.today)
