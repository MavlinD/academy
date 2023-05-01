from django.contrib import admin

from src.django_space.ads.models import Ads, Image


@admin.register(Ads)
class AdsAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "desc")
    list_filter = ("name",)
    search_fields = ("name", "desc")
    ordering = ["name", "price"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("ads", "path")
    list_filter = ("ads",)
    search_fields = ("ads", "path")
    ordering = ["ads", "path"]
