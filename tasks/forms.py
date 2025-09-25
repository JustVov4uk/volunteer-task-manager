from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from tasks.models import Category, CustomUser, Task, Tag, Report


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class CustomUserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "role", "first_name", "last_name", "email", "phone_number", "city")


class CustomUserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "role", "first_name", "last_name", "email", "phone_number", "city")


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = CustomUser.objects.filter(role="volunteer")
        self.fields["created_by"].queryset = CustomUser.objects.filter(role="coordinator")


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["verified_by"].queryset = CustomUser.objects.filter(role="coordinator")
        self.fields["author"].queryset = CustomUser.objects.filter(role="volunteer")