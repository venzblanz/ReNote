from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    path("", views.library_view, name="list"),
    path("add/", views.add_title_view, name="add"),
    path("save/", views.save_title_view, name="save"),
]