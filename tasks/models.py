from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("coordinator", "Coordinator"),
        ("volunteer", "Volunteer"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="volunteer")
    phone_number = models.CharField(max_length=15, unique=False, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("suspended", "Suspended"),
    )

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name="created_tasks")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.SET_NULL,
                                    related_name="assigned_tasks",
                                    null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default="active")
    deadline = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title


class Report(models.Model):
    comment = models.CharField(max_length=500)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL,
                               related_name="reports_authored")
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.SET_NULL,
                                    related_name="reports_verified",
                                    null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report for {self.task.title}"
