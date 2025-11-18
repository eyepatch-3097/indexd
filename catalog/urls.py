from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("add/", views.add_item, name="add_item"),
    path("lists/<slug:slug>/", views.list_detail, name="list_detail"),
    path("search_external/", views.external_search, name="external_search"),
    path("prefill_from_external/", views.prefill_from_external, name="prefill_from_external"),
]
