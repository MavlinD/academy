# Generated by Django 4.2 on 2023-05-02 05:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ads", "0003_rename_description_ads_desc"),
    ]

    operations = [
        migrations.RenameField(
            model_name="image",
            old_name="ads",
            new_name="ads_id",
        ),
    ]
