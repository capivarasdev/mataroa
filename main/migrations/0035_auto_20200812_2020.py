# Generated by Django 3.0.8 on 2020-08-12 20:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0034_analytic"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="analytic",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddField(
            model_name="user",
            name="comments_on",
            field=models.BooleanField(
                default=False, help_text="Enable/disable comments for your blog"
            ),
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("body", models.TextField()),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.Post"
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
