# Generated by Django 4.1 on 2023-08-07 22:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0012_alter_user_role"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user", old_name="modified_at", new_name="updated_at",
        ),
        migrations.RenameField(
            model_name="userprofile", old_name="modified_at", new_name="updated_at",
        ),
    ]