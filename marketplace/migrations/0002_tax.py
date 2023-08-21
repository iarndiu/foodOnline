# Generated by Django 4.1 on 2023-08-15 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tax",
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
                ("tax_type", models.CharField(blank=True, max_length=25)),
                (
                    "tax_percentage",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=4,
                        verbose_name="Tax Percentage (%)",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"verbose_name_plural": "tax", },
        ),
    ]