from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ("koordinator", "Koordinator"),
        ("volunteer", "Volunteer"),
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=100)
    city = models.CharField(max_length=100)


