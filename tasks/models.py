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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="volunteer", db_index=True)
    phone_number = models.CharField(max_length=25, unique=False, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True)
    profile_image = models.ImageField(upload_to="images/", null=True, blank=True)

    @property
    def avatar_url(self):
        if self.profile_image:
            return self.profile_image.url
        return ""

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
    description = models.TextField(max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="created_tasks"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", db_index=True)
    deadline = models.DateTimeField(null=True, blank=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, db_index=True, related_name="tasks")
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")

    def __str__(self):
        return self.title


class Report(models.Model):
    comment = models.CharField(max_length=500)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reports_authored",
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reports",
        null=True,
        blank=True,
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.task:
            return f"Report for {self.task.title}"
        return "Report (no task)"
