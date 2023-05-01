# Generated by Django 4.2 on 2023-04-29 17:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ads",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("price", models.DecimalField(decimal_places=2, max_digits=9)),
                ("description", models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name="Images",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("path", models.CharField(max_length=256)),
                ("ads", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ads.ads")),
            ],
        ),
    ]