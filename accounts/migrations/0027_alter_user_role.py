# Generated by Django 4.1 on 2023-08-18 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0026_alter_user_role"),
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