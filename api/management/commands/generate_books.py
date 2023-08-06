import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from faker import Faker

from api.models import Book, Author


def get_random_genre():
    genre_list = [
        "Fiction",
        "Mystery",
        "Science Fiction",
        "Fantasy",
        "Romance",
        "Thriller",
        "Historical Fiction",
        "Non-fiction",
        "Biography",
        "Self-Help",
    ]
    return random.choice(genre_list)


def generate_random_date():
    start_date = datetime(1900, 1, 1)
    end_date = datetime(2022, 12, 31)
    days_difference = (end_date - start_date).days
    random_days = random.randint(0, days_difference)
    random_date = start_date + timedelta(days=random_days)
    return random_date.date()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("books_count", nargs="?", type=int, default=10)

    def handle(self, *args, books_count, **options):
        faker = Faker()

        books = []
        for _ in range(books_count):
            author = Author(name=f"{faker.first_name()} {faker.last_name()}")
            author.save()
            book = Book(
                title=faker.sentence().replace(".", ""),
                author_id=author.id,
                genre=get_random_genre(),
                price=faker.random_int(min=10000, max=50000),
                quantity=faker.random_int(min=10, max=100),
                publication_date=generate_random_date(),
            )
            books.append(book)
        Book.objects.bulk_create(books)

        self.stdout.write(
            self.style.SUCCESS("Successfully created %s books" % books_count)
        )
