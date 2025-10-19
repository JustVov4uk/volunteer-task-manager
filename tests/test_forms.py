from django.test import TestCase

from tasks.forms import CategoryForm, CategorySearchForm


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
