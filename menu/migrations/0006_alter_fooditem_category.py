# Generated by Django 4.1 on 2023-08-07 22:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0005_alter_fooditem_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fooditem",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fooditems",
                to="menu.category",
            ),
        ),
    ]
