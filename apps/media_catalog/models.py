from django.db import models
from django.contrib.postgres.fields import ArrayField


class Media(models.Model):
    external_id = models.CharField(max_length=50)
    media_type = models.CharField(max_length=15)
    media_title = models.CharField(max_length=255)
    media_description = models.TextField()
    media_image = models.TextField()
    media_release_date = models.DateField(null=True, blank=True)
    media_rate = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    genre = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['external_id', 'media_type'], name='unique_media_source')
        ]

    def __str__(self):
        return self.media_title