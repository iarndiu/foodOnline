# Generated by Django 4.1 on 2023-08-27 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendor", "0006_alter_openinghour_options_and_more"),
        ("order", "0003_alter_payment_payment_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="total_data",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="vendors",
            field=models.ManyToManyField(blank=True, to="vendor.vendor"),
        ),
    ]
