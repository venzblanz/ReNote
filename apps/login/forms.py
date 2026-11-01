import logging
from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

logger = logging.getLogger(__name__)


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form with styled email input matching ReNote's auth design.
    """
    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "id": "id_email",
                "name": "email",
                "placeholder": "you@example.com",
                "autocomplete": "email",
                "required": True,
                "autofocus": True,
            }
        ),
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a password reset email with robust error logging so network/provider
        timeouts don't crash the web worker with an unhandled 500 server error.
        """
        try:
            super().send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                to_email,
                html_email_template_name=html_email_template_name,
            )
        except Exception as exc:
            logger.error(
                "Failed to send password reset email to %s: %s",
                to_email,
                exc,
                exc_info=True,
            )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom set password form with styled password fields for the reset confirmation step.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "new_password1" in self.fields:
            self.fields["new_password1"].widget.attrs.update({
                "id": "id_new_password1",
                "placeholder": "••••••••",
                "autocomplete": "new-password",
                "required": True,
            })
        if "new_password2" in self.fields:
            self.fields["new_password2"].widget.attrs.update({
                "id": "id_new_password2",
                "placeholder": "••••••••",
                "autocomplete": "new-password",
                "required": True,
            })
