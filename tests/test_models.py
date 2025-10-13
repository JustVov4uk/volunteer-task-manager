from datetime import datetime, timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from tasks.models import Category, Tag, Task


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
            email="test@gmail.com",
            role="coordinator",
            phone_number="Test Phone Number",
            city="Test City",
        )

        self.assertEqual(customuser.username, "Test User")
        self.assertEqual(customuser.first_name, "Test First")
        self.assertEqual(customuser.last_name, "Test Last")
        self.assertEqual(customuser.email, "test@gmail.com")
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


class TagModelTest(TestCase):
    def test_tag_is_valid_data(self):
        tag = Tag.objects.create(
            name="Test Tag",
        )

        self.assertEqual(tag.name, "Test Tag")

    def test_tag_with_unique_name(self):
        Tag.objects.create(
            name="Test Tag",
        )
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Test Tag")

    def test_tag_format_str(self):
        tag = Tag.objects.create(
            name="Test Tag",
        )

        self.assertEqual(
            str(tag),
            f"{tag.name}"
        )


class TaskModelTest(TestCase):
    def test_task_with_minimal_fields(self):
        task = Task.objects.create(
            title="Test Task",
        )

        self.assertEqual(task.title, "Test Task")

    def test_task_with_full_fields(self):
        category = Category.objects.create(name="Help", description="Test Help")
        user1 = get_user_model().objects.create_user(username="creator")
        user2 = get_user_model().objects.create_user(username="performer")
        tag1 = Tag.objects.create(name="urgent")
        tag2 = Tag.objects.create(name="important")

        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            created_by=user1,
            assigned_to=user2,
            status="active",
            deadline="2025-12-31T23:59:00Z",
            category=category,
    )
        task.tags.add(tag1, tag2)

        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.created_by, user1)
        self.assertEqual(task.assigned_to, user2)
        self.assertEqual(task.status, "active")
        self.assertEqual(task.deadline, "2025-12-31T23:59:00Z")
        self.assertEqual(task.category, category)
        self.assertEqual(task.tags.count(), 2)

    def test_task_default_value_is_active(self):
        task = Task.objects.create(
            title="Test Task",
        )

        self.assertEqual(task.status, "active")

    def test_task_format_str(self):
        task = Task.objects.create(
            title="Test Task",
        )

        self.assertEqual(
            str(task),
            f"{task.title}"
        )

    def test_task_ordering_by_deadline(self):
        Task.objects.create(
            title="1Test Task",
            deadline="2025-12-31T23:59:00Z",
        )
        Task.objects.create(
            title="2Test Task",
            deadline="2025-12-20T23:59:00Z",
        )
        Task.objects.create(
            title="3Test Task",
            deadline="2025-12-10T23:59:00Z",
        )

        tasks = Task.objects.all()
        deadlines = [task.deadline for task in tasks]
        self.assertEqual(deadlines, [
            datetime(2025, 12, 10, 23, 59, tzinfo=timezone.utc),
            datetime(2025, 12, 20, 23, 59, tzinfo=timezone.utc),
            datetime(2025, 12, 31, 23, 59, tzinfo=timezone.utc),
        ])

    def test_task_foreign_key_set_null_on_delete(self):
        user1 = get_user_model().objects.create_user(username="creator")
        user2 = get_user_model().objects.create_user(username="performer")
        category = Category.objects.create(name="Test Category")

        task = Task.objects.create(
            title="Test Task",
            created_by=user1,
            assigned_to=user2,
            category=category,
        )

        self.assertEqual(task.created_by, user1)
        self.assertEqual(task.assigned_to, user2)
        self.assertEqual(task.category, category)

        user1.delete()
        user2.delete()
        category.delete()

        task.refresh_from_db()

        self.assertIsNone(task.created_by)
        self.assertIsNone(task.assigned_to)
        self.assertIsNone(task.category)

    def test_task_add_a_few_tags(self):
        tag1 = Tag.objects.create(name="Urgent")
        tag2 = Tag.objects.create(name="Important")

        task = Task.objects.create(title="Test Task")
        task.tags.add(tag1, tag2)

        self.assertEqual(task.tags.count(), 2)
        self.assertIn(tag1, task.tags.all())
        self.assertIn(tag2, task.tags.all())

    def test_task_status_invalid_value_raises_error(self):
        task = Task.objects.create(
            title="Test Task",
            status="unknown",
        )
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_task_status_with_valid_values(self):
        category = Category.objects.create(name="Test Category", description="Test Help")
        for status in ["active", "in_progress", "completed", "suspended"]:
            Task(title=f"Test Task {status}", status=status, category=category).full_clean()

    def test_task_description_may_be_empty(self):
        task = Task.objects.create(
            title="Test Task",
        )

        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "")