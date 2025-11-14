import time
from datetime import datetime, timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from tasks.models import Category, Tag, Task, Report


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


class ReportModelTests(TestCase):
    def test_report_is_valid_with_all_fields(self):
        author = get_user_model().objects.create_user(username="volunteer")
        task = Task.objects.create(
            title="Test Task",
        )
        verified_by = get_user_model().objects.create_user(username="coordinator")

        report = Report.objects.create(
            comment="Test Comment",
            author=author,
            created_at="2025-12-10T10:00:00Z",
            updated_at="2025-12-11T10:00:00Z",
            task=task,
            verified_by=verified_by,
            verified_at=datetime(2025, 12, 15, 10, 0, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(report.comment, "Test Comment")
        self.assertEqual(report.author, author)
        self.assertIsNotNone(report.created_at)
        self.assertIsNotNone(report.updated_at)
        self.assertEqual(report.task, task)
        self.assertEqual(report.verified_by, verified_by)
        self.assertEqual(report.verified_at,
                         datetime(2025, 12, 15, 10, 0, 0, tzinfo=timezone.utc))

    def test_report_created_at_and_updated_at_behaviour(self):
        author = get_user_model().objects.create_user(username="volunteer")
        task = Task.objects.create(
            title="Test Task",
        )
        verified_by = get_user_model().objects.create_user(username="coordinator")

        report = Report.objects.create(
            comment="Test Comment",
            author=author,
            task=task,
            verified_by=verified_by,
        )

        created_first = report.created_at
        updated_first = report.updated_at

        self.assertIsNotNone(created_first)
        self.assertIsNotNone(updated_first)

        time.sleep(1)
        report.comment = "Update Comment"
        report.save()
        report.refresh_from_db()

        self.assertEqual(report.created_at, created_first)
        self.assertGreater(report.updated_at, updated_first)

    def test_report_relation_author_verified_by_task(self):
        author = get_user_model().objects.create_user(username="volunteer")
        task = Task.objects.create(
            title="Test Task",
        )
        verified_by = get_user_model().objects.create_user(username="coordinator")

        report = Report.objects.create(
            comment="Test Comment",
            author=author,
            task=task,
            verified_by=verified_by,
        )

        self.assertEqual(report.author, author)
        self.assertEqual(report.task, task)
        self.assertEqual(report.verified_by, verified_by)

        self.assertIn(report, author.reports_authored.all())
        self.assertIn(report, task.reports_task.all())
        self.assertIn(report, verified_by.reports_verified_by.all())

    def test_report_on_delete_behaviour(self):
        author = get_user_model().objects.create_user(username="volunteer")
        task = Task.objects.create(title="Test Task")
        verified_by = get_user_model().objects.create_user(username="coordinator")

        report = Report.objects.create(
            comment="Test Comment",
            author=author,
            task=task,
            verified_by=verified_by,
        )

        self.assertEqual(report.author, author)
        self.assertEqual(report.task, task)
        self.assertEqual(report.verified_by, verified_by)

        author.delete()
        report.refresh_from_db()
        self.assertIsNone(report.author)

        verified_by.delete()
        report.refresh_from_db()
        self.assertIsNone(report.verified_by)

        task.delete()
        self.assertFalse(Report.objects.filter(id=report.pk).exists())

    def test_report_ordering(self):
        task = Task.objects.create(title="Test Task")

        Report.objects.create(
            comment="1Test Comment",
            task=task,
        )
        time.sleep(1)
        Report.objects.create(
            comment="2Test Comment",
            task=task,
        )
        time.sleep(1)
        Report.objects.create(
            comment="3Test Comment",
            task=task,
        )
        reports = Report.objects.all()
        comments = [report.comment for report in reports]
        self.assertEqual(comments,
                         ["3Test Comment",
                          "2Test Comment",
                          "1Test Comment"])

    def test_report_if_task_exist_format_str(self):
        task = Task.objects.create(title="Test Task")
        report = Report.objects.create(
            comment="Test Comment",
            task=task,
        )

        self.assertEqual(
            str(report),
            f"Report for {report.task.title}"
        )

    def test_report_verified_at_is_none(self):
        task = Task.objects.create(title="Test Task")
        report = Report.objects.create(
            comment="Test Comment",
            task=task,
        )

        self.assertEqual(report.comment, "Test Comment")
        self.assertEqual(report.verified_at, None)
