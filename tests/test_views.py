from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            password="other test password",
            role="volunteer",
        )

    def test_view_redirect_coordinator(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:coordinator-index"))

    def test_view_redirect_volunteer(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:volunteer-index"))

    def test_view_redirect_login(self):
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class CoordinatorIndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            password="other test password",
            role="volunteer",
        )
    def test_view_logged_context_coordinator(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:coordinator-index"))
        self.assertEqual(response.status_code, 200)

        self.assertIn("num_volunteers", response.context)
        self.assertIn("num_tasks", response.context)
        self.assertIn("num_categories", response.context)
        self.assertIn("num_reports", response.context)
        self.assertIn("status_counts", response.context)

    def test_view_if_not_coordinator_permission_denied(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.get(reverse("tasks:coordinator-index"))
        self.assertEqual(response.status_code, 403)


class VolunteerIndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            password="test password",
            role="volunteer",
        )

    def test_view_logged_context_volunteer(self):
        self.client.login(username="volunteer", password="test password")
        response = self.client.get(reverse("tasks:volunteer-index"))
        self.assertEqual(response.status_code, 200)

        self.assertIn("user", response.context)
        self.assertIn("num_tasks", response.context)
        self.assertIn("num_categories", response.context)