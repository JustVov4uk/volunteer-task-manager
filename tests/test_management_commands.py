from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from tasks.models import Category, Report, Tag, Task


class SeedDemoCommandTest(TestCase):
    def test_seed_demo_creates_recruiter_ready_data(self):
        output = StringIO()

        call_command("seed_demo", stdout=output)

        self.assertTrue(
            get_user_model().objects.filter(
                username="administrator1",
                role="coordinator",
            ).exists()
        )
        self.assertTrue(
            get_user_model().objects.filter(
                username="vol_tanya",
                role="volunteer",
            ).exists()
        )
        self.assertGreaterEqual(Category.objects.count(), 4)
        self.assertGreaterEqual(Tag.objects.count(), 8)
        self.assertGreaterEqual(Task.objects.count(), 6)
        self.assertGreaterEqual(Report.objects.count(), 2)
        self.assertIn("Demo data is ready.", output.getvalue())

    def test_seed_demo_is_idempotent(self):
        call_command("seed_demo", stdout=StringIO())

        counts_after_first_run = {
            "users": get_user_model().objects.count(),
            "categories": Category.objects.count(),
            "tags": Tag.objects.count(),
            "tasks": Task.objects.count(),
            "reports": Report.objects.count(),
        }

        call_command("seed_demo", stdout=StringIO())

        self.assertEqual(
            counts_after_first_run["users"],
            get_user_model().objects.count(),
        )
        self.assertEqual(
            counts_after_first_run["categories"],
            Category.objects.count(),
        )
        self.assertEqual(
            counts_after_first_run["tags"],
            Tag.objects.count(),
        )
        self.assertEqual(
            counts_after_first_run["tasks"],
            Task.objects.count(),
        )
        self.assertEqual(
            counts_after_first_run["reports"],
            Report.objects.count(),
        )
