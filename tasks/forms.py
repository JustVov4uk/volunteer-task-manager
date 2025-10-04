from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils import timezone

from tasks.models import Category, CustomUser, Task, Tag, Report


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class CategorySearchForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by name",
            }
        )
    )


class CustomUserCreateForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "role", "first_name", "last_name", "email", "phone_number", "city", "profile_image")


class CustomUserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "role", "first_name", "last_name", "email", "phone_number", "city", "profile_image")


class CustomUserSearchForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by username",
            }
        )
    )

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"
        widgets = {
            "deadline": forms.DateTimeInput(attrs={
                "type": "datetime-local",
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = CustomUser.objects.filter(role="volunteer")
        self.fields["created_by"].queryset = CustomUser.objects.filter(role="coordinator")


class TaskSearchForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by title",
            }
        )
    )
    status = forms.ChoiceField(
        choices=[("", "All"), ("active", "Active"),
                 ("in_progress", "In Progress"),
                 ("completed", "Completed"),
                 ("suspended", "Suspended")],
        required=False,
        label="Status",
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All categories",
        label="Category",
    )
    tags = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="All tags",
        label="Tags",
    )


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"


class TagSearchForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by name",
            }
        )
    )


class VolunteerReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("comment", "task")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["task"].queryset = Task.objects.filter(assigned_to=user)



class CoordinatorReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("verified_by", "verified_at")
        widgets = {
            "verified_at": forms.DateTimeInput(attrs={
                "type": "datetime-local",
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["verified_by"].queryset = CustomUser.objects.filter(role="coordinator")


class ReportSearchForm(forms.Form):
    author = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search by author",
            }
        )
    )
    author_filter = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role="volunteer"),
        required=False,
        empty_label="All authors",
        label="Author",
    )
    created_filter = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role="volunteer"),
        required=False,
        empty_label="All authors",
        label="Created",
    )
