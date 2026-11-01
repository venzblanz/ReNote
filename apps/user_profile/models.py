from django.db import models
from apps.accounts.models import User

DEFAULT_AVATAR = '202156.png'

AVAILABLE_AVATARS = [
    '202156.png',
    '365483.png',
    '367476.jpeg',
    '371396.png',
    '375205.png',
    '375210.png',
    '375214.png',
    '375218.png',
    '375364.png',
    '377617.png',
    '378290.jpg',
    '378408.jpg',
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_name = models.CharField(max_length=30, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.CharField(max_length=100, default=DEFAULT_AVATAR, blank=True)
    data_privacy_consent = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return self.user.username
