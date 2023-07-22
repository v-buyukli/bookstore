import base64
import hashlib

import ecdsa
import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status

from api.models import Order, OrderItem, Book


def create_order(order_data, webhook_url):
    for order_item in order_data:
        book_id = order_item["book_id"].id
        quantity = order_item["quantity"]
        try:
            book = Book.objects.get(id=book_id)
            if quantity < 1:
                return JsonResponse(
                    {"error": "quantity must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if book.quantity < quantity:
                return JsonResponse(
                    {"error": f"available quantity = {book.quantity}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Book.DoesNotExist:
            return JsonResponse(
                {"error": "book not found"}, status=status.HTTP_404_NOT_FOUND
            )

    basketOrder = []
    order_items = []
    amount = 0
    order = Order.objects.create(total_price=0)

    for order_item in order_data:
        item_sum = order_item["book_id"].price * order_item["quantity"]
        basketOrder.append(
            {
                "name": order_item["book_id"].title,
                "qty": order_item["quantity"],
                "sum": item_sum,
                "unit": "шт.",
            }
        )
        item = OrderItem.objects.create(
            book=order_item["book_id"], order=order, quantity=order_item["quantity"]
        )
        order_items.append(item)
        amount += item_sum

    order.total_price = amount
    order.save()

    body = {
        "amount": amount,
        "merchantPaymInfo": {
            "reference": str(order.id),
            "basketOrder": basketOrder,
        },
        "webHookUrl": webhook_url,
    }

    r = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        headers={"X-Token": settings.MONOBANK_API_KEY},
        json=body,
    )
    r.raise_for_status()
    order.invoice_id = r.json()["invoiceId"]
    order.save()

    for order_item in order_data:
        book = Book.objects.get(id=order_item["book_id"].id)
        book.quantity -= order_item["quantity"]
        book.save()
    cache.clear()

    url = r.json()["pageUrl"]
    return {"url": url, "id": order.id}


def verify_signature(pub_key_base64, x_sign_base64, body_bytes):
    try:
        pub_key_bytes = base64.b64decode(pub_key_base64)
        signature_bytes = base64.b64decode(x_sign_base64)
        pub_key = ecdsa.VerifyingKey.from_pem(pub_key_bytes.decode())
        ok = pub_key.verify(
            signature_bytes,
            body_bytes,
            sigdecode=ecdsa.util.sigdecode_der,
            hashfunc=hashlib.sha256,
        )
    except Exception:
        return False

    if ok:
        return True
    else:
        return False
