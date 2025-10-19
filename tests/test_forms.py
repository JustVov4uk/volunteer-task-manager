from django.test import TestCase

from tasks.forms import CategoryForm


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