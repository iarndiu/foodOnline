# Generated by Django 4.1 on 2023-08-01 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_rename_is_superuser_user_is_superadmin_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="userprofile", name="address_line_1",),
        migrations.RemoveField(model_name="userprofile", name="address_line_2",),
        migrations.AddField(
            model_name="userprofile",
            name="address",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]