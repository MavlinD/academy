from django.db import models

from src.django_space.ads.config import config


class Ads(models.Model):
    """модель объявления"""

    name = models.CharField(max_length=config.AD_NAME_MAX_LENGTH)
    price = models.DecimalField(max_digits=config.AD_MAX_PRICE_DIGITS, decimal_places=2)
    desc = models.CharField(max_length=config.AD_DESC_MAX_LENGTH)

    def __str__(self):
        return self.name


class Image(models.Model):
    """модель изображения, связь один ко многим с объявлением"""

    ads_id = models.ForeignKey(Ads, on_delete=models.CASCADE)
    path = models.CharField(max_length=256)
    is_main = models.BooleanField(default=False)
