from django.urls import path
from . import views

app_name = "register"

urlpatterns = [
    path("", views.register_view, name="register"),
    path("terms/", views.terms_view, name="terms"),
    path("privacy/", views.privacy_view, name="privacy"),
]
