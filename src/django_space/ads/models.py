from django.db import models


class Ads(models.Model):
    """модель объявления"""

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = models.CharField(max_length=1000)


class Image(models.Model):
    """модель изображения, связь один ко многим с объявлением"""

    ads = models.ForeignKey(Ads, on_delete=models.CASCADE)
    path = models.CharField(max_length=256)
