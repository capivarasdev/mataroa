# Generated by Django 5.0.7 on 2024-07-25 17:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0106_alter_user_custom_domain"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="monero_address",
        ),
    ]
