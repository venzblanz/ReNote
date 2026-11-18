import json
from django.db import models
from django.contrib.postgres.fields import ArrayField


class CompatibleArrayField(ArrayField):
    def db_type(self, connection):
        if connection.vendor == 'sqlite':
            return 'text'
        return super().db_type(connection)

    def get_placeholder(self, value, compiler, connection):
        if connection.vendor == 'sqlite':
            return '%s'
        return super().get_placeholder(value, compiler, connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        if connection.vendor == 'sqlite':
            if isinstance(value, (list, tuple)):
                return json.dumps(list(value))
            elif value is None:
                return json.dumps([])
            return value
        return super().get_db_prep_value(value, connection, prepared=prepared)

    def from_db_value(self, value, expression, connection):
        if connection.vendor == 'sqlite':
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except Exception:
                    return []
            return value or []
        return value

    def to_python(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                pass
        return super().to_python(value)


class Media(models.Model):
    external_id = models.CharField(max_length=50)
    media_type = models.CharField(max_length=15)
    media_title = models.CharField(max_length=255)
    media_description = models.TextField()
    media_image = models.TextField()
    media_release_date = models.DateField(null=True, blank=True)
    media_rate = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    genre = CompatibleArrayField(models.CharField(max_length=50), blank=True, default=list)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['external_id', 'media_type'], name='unique_media_source')
        ]

    def __str__(self):
        return self.media_title