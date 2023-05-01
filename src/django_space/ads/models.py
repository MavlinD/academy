from django.db import models

from src.django_space.ads.config import config


class Ads(models.Model):
    """модель объявления"""

    name = models.CharField(max_length=config.AD_NAME_MAX_LENGTH)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    desc = models.CharField(max_length=config.AD_DESC_MAX_LENGTH)


class Image(models.Model):
    """модель изображения, связь один ко многим с объявлением"""

    ads = models.ForeignKey(Ads, on_delete=models.CASCADE)
    path = models.CharField(max_length=256)
