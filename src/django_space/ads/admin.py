from django.contrib import admin
from django.contrib.admin import AdminSite

from src.django_space.ads.models import Ads, Image

# class AdminSite(AdminSite):
#     site_header = 'Monty Python administration'


@admin.register(Ads)
class AdsAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "description")
    list_filter = ("name",)
    search_fields = ("name", "description")
    ordering = ["name", "price"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("ads", "path")
    list_filter = ("ads",)
    search_fields = ("ads", "path")
    ordering = ["ads", "path"]
    # raw_id_fields = ('parent',)
