# Generated by Django 4.2 on 2023-05-02 12:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ads", "0004_rename_ads_image_ads_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="image",
            name="is_main",
            field=models.BooleanField(default=False),
        ),
    ]
