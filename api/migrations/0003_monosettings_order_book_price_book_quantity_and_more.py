import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_token"),
    ]

    operations = [
        migrations.CreateModel(
            name="MonoSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("public_key", models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_price", models.PositiveIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("invoice_id", models.CharField(max_length=255, null=True)),
                ("status", models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name="book",
            name="price",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="book",
            name="quantity",
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.book"
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.order"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="books",
            field=models.ManyToManyField(through="api.OrderItem", to="api.book"),
        ),
    ]
