from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.forms import (CategoryForm,
                         CategorySearchForm,
                         CustomUserCreateForm, CustomUserUpdateForm, CustomUserSearchForm)


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