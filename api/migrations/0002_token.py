from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Token",
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
                ("sub", models.CharField(max_length=255)),
                ("token", models.CharField(max_length=512)),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]