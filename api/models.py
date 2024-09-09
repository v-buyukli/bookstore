from datetime import date

import requests
from django.conf import settings
from django.db import models


class Token(models.Model):
    sub = models.CharField(max_length=255)
    token = models.CharField(max_length=512)
    created = models.DateTimeField(auto_now_add=True, blank=True)


class Author(models.Model):
    name = models.CharField(max_length=255)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.CharField(max_length=255)
    price = models.PositiveIntegerField(default=1)
    quantity = models.IntegerField(default=1)
    publication_date = models.DateField(default=date.today)


class Order(models.Model):
    books = models.ManyToManyField(Book, through="OrderItem")
    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    invoice_id = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, null=True)


class OrderItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class MonoSettings(models.Model):
    public_key = models.CharField(max_length=1000)

    @classmethod
    def get_token(cls):
        try:
            return cls.objects.last().public_key
        except AttributeError:
            key = requests.get(
                "https://api.monobank.ua/api/merchant/pubkey",
                headers={"X-Token": settings.MONOBANK_API_KEY},
            ).json()["key"]
            cls.objects.create(public_key=key)
            return key
