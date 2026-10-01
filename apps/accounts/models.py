from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = None
    last_name = None
    date_joined = None

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username