from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from tasks.models import Category


class CategoryModelTest(TestCase):
    def test_category_is_valid_data(self):
        category = Category.objects.create(
            name="Test Category",
            description="Test description",
        )

        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.description, "Test description")
        self.assertEqual(Category.objects.count(), 1)

    def test_category_format_str(self):
        category = Category.objects.create(
            name="Test Category",
            description="Test description",
        )

        self.assertEqual(
            str(category),
            f"{category.name}"
        )

    def test_category_max_length(self):
        category = Category(
            name="a" * 101,
            description="b" * 501,
        )
        with self.assertRaises(ValidationError):
            category.full_clean()


class CustomUserModelTest(TestCase):
    def test_user_is_valid_data(self):