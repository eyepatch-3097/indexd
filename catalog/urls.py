from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("add/", views.add_item, name="add_item"),
    path("lists/<slug:slug>/", views.list_detail, name="list_detail"),
]
