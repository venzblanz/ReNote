from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

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
