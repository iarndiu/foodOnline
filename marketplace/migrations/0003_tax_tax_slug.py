# Generated by Django 4.1 on 2023-08-16 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0002_tax"),
    ]

    operations = [
        migrations.AddField(
            model_name="tax",
            name="tax_slug",
            field=models.SlugField(blank=True, max_length=100),
        ),
    ]
