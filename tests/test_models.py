from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
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
        customuser = get_user_model().objects.create_user(
            username="Test User",
            first_name="Test First",
            last_name="Test Last",
            password="Test Password",
            email="Test Email",
            role="coordinator",
            phone_number="Test Phone Number",
            city="Test City",
        )

        self.assertEqual(customuser.username, "Test User")
        self.assertEqual(customuser.first_name, "Test First")
        self.assertEqual(customuser.last_name, "Test Last")
        self.assertEqual(customuser.email, "Test Email")
        self.assertEqual(customuser.role, "coordinator")
        self.assertEqual(customuser.phone_number, "Test Phone Number")
        self.assertEqual(customuser.city, "Test City")
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_customuser_volunteer_is_default(self):
        customuser = get_user_model().objects.create_user(
            username="Test User",
        )

        self.assertEqual(customuser.role, "volunteer")

    def test_customuser_phone_number_is_unique(self):
        get_user_model().objects.create_user(
            username="Test User",
            phone_number="Test Phone Number",
        )
        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(username="Test User", phone_number="Test Phone Number")

    def test_customuser_format_str(self):
        customuser = get_user_model().objects.create_user(
            username="Test User",
        )

        self.assertEqual(
            str(customuser),
            f"{customuser.username}"
        )

    def test_customuser_ordering(self):
        get_user_model().objects.create_user(
            username="1Test User",
        )
        get_user_model().objects.create_user(
            username="2Test User",
        )
        get_user_model().objects.create_user(
            username="3Test User",
        )

        customusers = get_user_model().objects.all()
        usernames = [customuser.username for customuser in customusers]
        self.assertEqual(usernames, [
            "1Test User",
            "2Test User",
            "3Test User",
        ])

    def test_customuser_when_image_is_exist(self):
        image = SimpleUploadedFile("test.jpg", b"file_content", "image/jpeg")
        customuser = get_user_model().objects.create_user(
            username="Test User",
            profile_image=image,
        )

        self.assertTrue(customuser.avatar_url)
        self.assertEqual(customuser.avatar_url.endswith(".jpg"), True)
        self.assertIn("/media/", customuser.avatar_url)

    def test_customuser_when_image_is_not_exist(self):
        customuser = get_user_model().objects.create_user(
            username="Test User",
        )
        self.assertEqual(customuser.avatar_url, "")

    def test_customuser_city_is_empty(self):
        customuser = get_user_model().objects.create_user(
            username="Test User",
            city="",
        )

        self.assertEqual(customuser.username, "Test User")
        self.assertEqual(customuser.city, "")

    def test_customuser_role_accepts_only_defined_choices(self):
        customuser1 = get_user_model().objects.create_user(
            username="Test_User1",
            role="coordinator",
        )
        customuser1.full_clean()

        customuser2 = get_user_model().objects.create_user(
            username="Test_User2",
            role="volunteer",
        )
        customuser2.full_clean()

    def test_customuser_role_invalid_value_raises_error(self):
        customuser3 = get_user_model().objects.create_user(
            username="Test User3",
            role="admin",
        )
        with self.assertRaises(ValidationError):
            customuser3.full_clean()
