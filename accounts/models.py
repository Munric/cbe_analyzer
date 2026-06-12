from django.contrib.auth.models import AbstractUser
from django.db import models
from schools.models import School


class User(AbstractUser):

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("teacher", "Teacher"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="teacher"
    )

    def __str__(self):
        return self.username