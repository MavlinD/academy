# Generated by Django 4.2 on 2023-05-01 04:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ads", "0002_rename_images_image"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ads",
            old_name="description",
            new_name="desc",
        ),
    ]
