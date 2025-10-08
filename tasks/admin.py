from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from tasks.models import Category, CustomUser, Tag, Task, Report


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("role", "phone_number", "city", "avatar_thumb")
    list_filter = ("role", "city", "is_active")
    search_fields = ("username", "city")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("role", "phone_number", "city", "profile_image")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("role", "phone_number", "city")}),
    )
    def avatar_thumb(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width:32px;height:32px;object-fit:cover;'
                               'border-radius:50%;">', obj.profile_image.url)
        return ""
    avatar_thumb.short_description = "Avatar"


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
    list_display = ["author", "comment", "created_at", "task", "verified_by", "verified_at"]
    list_filter = ("author", "task", "created_at")
    search_fields = ("author",)
