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
    is_favorite = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'media'], name='unique_user_media')
        ]

    def __str__(self):
        return f"{self.user.username} — {self.media.media_title}"

class LibraryFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_user_folder_name')
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username} — {self.name}"


class FolderItem(models.Model):
    folder = models.ForeignKey(LibraryFolder, on_delete=models.CASCADE, related_name='items')
    library_log = models.ForeignKey(UserLibraryLog, on_delete=models.CASCADE, related_name='folder_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['folder', 'library_log'], name='unique_folder_item')
        ]
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.folder.name} — {self.library_log.media.media_title}"