import json
from datetime import date
from urllib.parse import quote_plus, urlencode

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Author, Book, Token, Order, MonoSettings
from .mono import create_order, verify_signature
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    OrderSerializer,
    OrderModelSerializer,
    MonoCallbackSerializer,
)
from .services import get_access_token


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
    if s:
        if s["userinfo"]["sub"] not in Token.objects.values_list("sub", flat=True):
            Token.objects.create(sub=s["userinfo"]["sub"], token=get_access_token())

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


@api_view(["GET"])
def token(request):
    s = request.session.get("user")
    if s:
        t = Token.objects.filter(sub=s["userinfo"]["sub"]).values().first()
        return JsonResponse({"access_token": t["token"]}, status=status.HTTP_200_OK)
    else:
        return JsonResponse(
            {"msg": "need registration"}, status=status.HTTP_401_UNAUTHORIZED
        )


class BooksView(APIView):
    pagination_class = LimitOffsetPagination

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        params = {"title", "author", "genre", "limit", "offset"}
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

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = BookSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

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
            price=serializer.validated_data["price"],
            quantity=serializer.validated_data["quantity"],
            publication_date=serializer.validated_data.get(
                "publication_date", date.today()
            ),
        )
        cache.clear()
        return JsonResponse(
            {"id": book.id, "msg": "book added successfully"},
            status=status.HTTP_201_CREATED,
        )


class BookView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request, id):
        try:
            book = Book.objects.get(id=id)
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response(
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

            params = {
                "title",
                "author",
                "genre",
                "price",
                "quantity",
                "publication_date",
            }
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
            if "price" in request_body:
                book.price = request_body["price"]
            if "quantity" in request_body:
                book.quantity = request_body["quantity"]
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
    pagination_class = LimitOffsetPagination

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        params = {"name", "limit", "offset"}
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

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = AuthorSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


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


class OrdersViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderModelSerializer
    pagination_class = LimitOffsetPagination


class OrderView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        order = OrderSerializer(data=request.data)
        order.is_valid(raise_exception=True)
        webhook_url = request.build_absolute_uri(reverse("mono_callback"))
        order_data = create_order(order.validated_data["order"], webhook_url)
        return Response(order_data)


class OrderCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        public_key = MonoSettings.get_token()

        if not verify_signature(
            public_key, request.headers.get("X-Sign"), request.body
        ):
            return Response(
                {"status": "signature mismatch"}, status=status.HTTP_400_BAD_REQUEST
            )

        callback = MonoCallbackSerializer(data=request.data)
        callback.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(id=callback.validated_data["reference"])
        except Order.DoesNotExist:
            return Response(
                {"status": "order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if order.invoice_id != callback.validated_data["invoiceId"]:
            return Response(
                {"status": "invoiceId mismatch"}, status=status.HTTP_400_BAD_REQUEST
            )

        order.status = callback.validated_data["status"]
        order.save()
        return Response({"status": "ok"})
