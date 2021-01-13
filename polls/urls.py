from django.urls import path

from . import views

urlpatterns = [
    path("active", views.active, name="active"),
]
