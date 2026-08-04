from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path(
        'admin/',
        admin.site.urls),
    path(
        "",
        include("tracker.urls",
                namespace="tracker")),
    path(
        "accounts/",
        include("django.contrib.auth.urls"))
] + debug_toolbar_urls()
