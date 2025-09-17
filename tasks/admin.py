from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from tasks.models import (Category,
                          CustomUser,
                          Tag, Task,
                          Report)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (UserAdmin.list_display +
                    ("role", "phone_number",
                     "city"))
    list_filter = ("role", "city", "is_active")
    search_fields = ("username", "city")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("role", "phone_number", "city")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("role", "phone_number", "city")}),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "description",
        "created_by",
        "assigned_to",
        "status",
        "deadline",
        "category",
    ]
    list_filter = ("status", "deadline", "category")
    search_fields = ("title", "description")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "comment",
        "task",
        "verified_by",
        "verified_at"
    ]
    list_filter = ("author", "task")
    search_fields = ("author",)
