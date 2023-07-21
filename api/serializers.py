from rest_framework import serializers

from .models import Author, Book, Order


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name")


class BookSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.name")

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "genre",
            "author",
            "price",
            "quantity",
            "publication_date",
        )


class OrderContentSerializer(serializers.Serializer):
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    quantity = serializers.IntegerField()


class OrderSerializer(serializers.Serializer):
    order = OrderContentSerializer(many=True, allow_empty=False)


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["total_price", "created_at", "invoice_id", "id", "books", "status"]


class MonoCallbackSerializer(serializers.Serializer):
    invoiceId = serializers.CharField()
    status = serializers.CharField()
    amount = serializers.IntegerField()
    ccy = serializers.IntegerField()
    reference = serializers.CharField()
