from django.db import models
from apps.accounts.models import User


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.user.username}"