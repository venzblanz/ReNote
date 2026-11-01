from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = "login"

urlpatterns = [
    path("", auth_views.LoginView.as_view(template_name="login/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Password Reset Flow
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="login/password_reset_form.html",
            email_template_name="login/password_reset_email.txt",
            html_email_template_name="login/password_reset_email.html",
            subject_template_name="login/password_reset_subject.txt",
            form_class=CustomPasswordResetForm,
            success_url=reverse_lazy("login:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="login/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="login/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
            success_url=reverse_lazy("login:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="login/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
