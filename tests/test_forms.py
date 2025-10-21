from unicodedata import category

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.forms import (CategoryForm,
                         CategorySearchForm,
                         CustomUserCreateForm, CustomUserUpdateForm, CustomUserSearchForm, TaskForm, TaskSearchForm)
from tasks.models import Category, Tag


class CategoryFormTest(TestCase):
    def test_form_valid_with_all_fields(self):
        form_data = {
            "name": "test name",
            "description": "test description"
        }
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "test name")
        self.assertEqual(form.cleaned_data["description"], "test description")

    def test_form_invalid_without_name(self):
        form_data = {
            "description": "test description"
        }
        form = CategoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class CategorySearchFormTest(TestCase):
    def test_form_valid_with_name_field(self):
        form_data = {
            "name": "test name",
        }
        form = CategorySearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "test name")

    def test_form_valid_when_name_is_empty(self):
        form_data = {
            "name": "",
            "description": "test description"
        }
        form = CategorySearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "")

    def test_form_field_has_placeholder(self):
        placeholder = CategorySearchForm().fields["name"].widget.attrs["placeholder"]
        self.assertEqual(placeholder, "Search by name")


class CustomUserCreateFormTest(TestCase):
    def test_form_valid_with_correct_data(self):
        form_data = {
            "username": "user",
            "password1": "test password",
            "password2": "test password",
            "first_name": "test first",
            "last_name": "test last",
            "email": "test@email.com",
            "role": "volunteer",
            "phone_number": "123456789",
            "city": "test city",
        }
        form = CustomUserCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_if_username_is_empty(self):
        form_data = {
            "username": "",
        }
        form = CustomUserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_form_if_form_has_all_fields(self):
        fields = [
            "username", "role", "first_name", "last_name",
            "email", "phone_number", "city", "profile_image",
            "password1", "password2",
        ]
        form = CustomUserCreateForm()
        self.assertEqual(list(form.fields.keys()), fields)


class CustomUserUpdateFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="old_user",
            first_name="old",
            last_name="user",
            email="old@gmail.com",
            role="volunteer",
            phone_number="123456789",
            city="old city",
        )
    def test_form_update_exist_volunteer(self):
        form_data = {
            "username": "new_user",
            "first_name": "new",
            "last_name": "user",
            "email": "new@gmail.com",
            "role": "volunteer",
            "phone_number": "987654321",
            "city": "new city",
        }
        form = CustomUserUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.username, "new_user")
        self.assertEqual(updated_user.first_name, "new")
        self.assertEqual(updated_user.last_name, "user")
        self.assertEqual(updated_user.email, "new@gmail.com")
        self.assertEqual(updated_user.phone_number, "987654321")
        self.assertEqual(updated_user.city, "new city")

    def test_form_valid_when_update_a_few_fields(self):
        form_data = {
            "username": "old_user",
            "first_name": "old",
            "last_name": "user",
            "email": "old@gmail.com",
            "role": "volunteer",
            "phone_number": "987654321",
            "city": "new city",
        }
        form = CustomUserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())


class CustomUserSearchFormTest(TestCase):
    def test_form_valid_with_input_username(self):
        form_data = {
            "username": "test_user",
        }
        form = CustomUserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "test_user")

    def test_form_valid_when_input_username_is_empty(self):
        form_data = {
            "username": "",
        }
        form = CustomUserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "")

    def test_form_with_placeholder(self):
        placeholder = CustomUserSearchForm().fields["username"].widget.attrs["placeholder"]
        self.assertEqual(placeholder, "Search by username")


class TaskFormTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            role="volunteer",
        )
        self.category = Category.objects.create(
            name="Test Category",
        )
        self.tag = Tag.objects.create(
            name="Test Tag",
        )

    def test_form_valid_with_all_fields(self):
        form_data = {
            "title": "test title",
            "description": "test description",
            "created_by": self.coordinator.id,
            "assigned_to": self.volunteer.id,
            "status": "active",
            "deadline": "2019-07-30T12:00",
            "category": self.category.id,
            "tags": [self.tag.id]
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_deadline_widget_type_is_datetime_local(self):
        form = TaskForm()
        widget = form.fields["deadline"].widget
        self.assertEqual(getattr(widget, "input_type", None), "datetime-local")

    def test_form_querysets_filtered_in_init(self):
        form = TaskForm()
        assigned_queryset = form.fields["assigned_to"].queryset
        created_queryset = form.fields["created_by"].queryset

        self.assertIn(self.volunteer, assigned_queryset)
        self.assertNotIn(self.coordinator, assigned_queryset)

        self.assertIn(self.coordinator, created_queryset)
        self.assertNotIn(self.volunteer, created_queryset)


class TaskSearchFormTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            role="volunteer",
        )
        self.category = Category.objects.create(
            name="Test Category",
        )
        self.tag = Tag.objects.create(
            name="Test Tag",
        )
    def test_form_valid_for_all_filters(self):
        form_data = {
            "title": "test title",
            "status": "active",
            "category": self.category.id,
            "tags": self.tag.id,
            "volunteer": self.volunteer.id,
        }
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_valid_with_empty_filters(self):
        form_data = {
            "title": "",
            "status": "",
            "category": "",
            "tags": "",
            "volunteer": "",
        }
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_status_has_choices(self):
        form = TaskSearchForm()
        choices = [choice[0] for choice in form.fields["status"].choices if choice[0]]
        self.assertEqual(choices, ["active", "in_progress", "completed", "suspended"])

    def test_form_fields_category_tags_volunteer_with_empty_label(self):
        form = TaskSearchForm()
        self.assertEqual(form.fields["category"].empty_label, "All categories")
        self.assertEqual(form.fields["tags"].empty_label, "All tags")
        self.assertEqual(form.fields["volunteer"].empty_label, "All volunteers")

    def test_form_placeholder_in_title(self):
        form = TaskSearchForm()
        placeholder = form.fields["title"].widget.attrs["placeholder"]
        self.assertEqual(placeholder, "Search by title")
