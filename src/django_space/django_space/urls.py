from django.contrib import admin
from django.urls import include, path
from logrich.logger_ import log  # noqa

urlpatterns = [
    path("ads/", include("src.django_space.ads.urls")),
    path("admin/", admin.site.urls),
]
