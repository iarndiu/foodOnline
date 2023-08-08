# Generated by Django 4.1 on 2023-08-08 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0013_rename_modified_at_user_updated_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.PositiveSmallIntegerField(
                blank=True, choices=[(2, "Customer"), (1, "Vendor")], null=True
            ),
        ),
    ]
