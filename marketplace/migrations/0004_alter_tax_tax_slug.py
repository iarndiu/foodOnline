# Generated by Django 4.1 on 2023-08-16 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0003_tax_tax_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tax",
            name="tax_slug",
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
