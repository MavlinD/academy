from django.contrib import admin
from django.urls import path
from logrich.logger_ import log  # noqa

urlpatterns = [
    path("admin/", admin.site.urls),
]
