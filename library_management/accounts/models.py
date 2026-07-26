from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        default="profile_images/default-user.png",
        blank=True
    )

    def __str__(self):
        return self.user.username