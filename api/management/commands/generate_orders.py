import random
from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand
from faker import Faker

from api.models import Order


def generate_random_date():
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 7, 31)
    days_difference = (end_date - start_date).days
    random_days = random.randint(0, days_difference)
    random_date = start_date + timedelta(days=random_days)
    random_datetime = random_date.replace(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=random.randint(0, 999999),
        tzinfo=timezone.utc,
    )
    return random_datetime


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("orders_count", nargs="?", type=int, default=10)

    def handle(self, *args, orders_count, **options):
        faker = Faker()

        for _ in range(orders_count):
            order = Order(
                total_price=faker.random_int(min=10000, max=100000),
                invoice_id="23072226PYknLaw6C1tj",
                status="created",
            )
            order.save()
            order.created_at = generate_random_date()
            order.save()

        self.stdout.write(
            self.style.SUCCESS("Successfully created %s orders" % orders_count)
        )
