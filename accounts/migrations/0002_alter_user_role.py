# Generated by Django 4.1 on 2023-07-23 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.PositiveSmallIntegerField(
                blank=True, choices=[(2, "Customer"), (1, "Restaurant")], null=True
            ),
        ),
    ]
