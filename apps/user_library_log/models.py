from django.db import models
from apps.accounts.models import User
from apps.media_catalog.models import Media


class UserLibraryLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    personal_rate = models.SmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20)
    rewatch_count = models.IntegerField(default=0)
    media_note = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'media'], name='unique_user_media')
        ]

    def __str__(self):
        return f"{self.user.username} — {self.media.media_title}"