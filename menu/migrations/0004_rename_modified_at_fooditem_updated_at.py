# Generated by Django 4.1 on 2023-08-03 23:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0003_rename_modified_at_category_updated_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="fooditem", old_name="modified_at", new_name="updated_at",
        ),
    ]
