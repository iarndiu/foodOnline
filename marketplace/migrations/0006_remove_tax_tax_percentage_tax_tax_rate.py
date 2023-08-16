# Generated by Django 4.1 on 2023-08-16 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0005_remove_tax_tax_slug"),
    ]

    operations = [
        migrations.RemoveField(model_name="tax", name="tax_percentage",),
        migrations.AddField(
            model_name="tax",
            name="tax_rate",
            field=models.DecimalField(
                decimal_places=2,
                default=7.25,
                max_digits=4,
                verbose_name="Tax Rate (%)",
            ),
            preserve_default=False,
        ),
    ]
