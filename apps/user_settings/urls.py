from django.urls import path
from . import views

app_name = "user_settings"

urlpatterns = [
    path("", views.settings_view, name="settings"),
    path("deactivate/", views.deactivate_account_view, name="deactivate"),
    path("delete/", views.delete_account_view, name="delete"),
]
