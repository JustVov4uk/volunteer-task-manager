from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from tasks.models import Category


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


class VolunteerListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
        )
        self.volunteer1 = get_user_model().objects.create_user(
            username="volunteer1",
            password="test password",
            role="volunteer",
        )
        self.volunteer2 = get_user_model().objects.create_user(
            username="volunteer2",
            password="test password",
            role="volunteer",
        )

    def test_view_login_volunteer_code_200(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:volunteer-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("volunteer_list", response.context)

    def test_view_pagination(self):
        self.client.login(username="coordinator", password="test password")
        for i in range(10):
            get_user_model().objects.create_user(
                username=f"page_volunteer_{i}",
                password="test password",
                role="volunteer",
            )
        response = self.client.get(reverse("tasks:volunteer-list"))
        self.assertEqual(len(response.context["volunteer_list"]), 5)

    def test_view_filtering(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:volunteer-list") + "?username=volunteer1")
        self.assertEqual(response.status_code, 200)
        volunteers = response.context["volunteer_list"]
        self.assertEqual(len(volunteers), 1)
        self.assertEqual(volunteers[0].username, "volunteer1")

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:volunteer-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class VolunteerDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.volunteer1 = get_user_model().objects.create_user(
            username="volunteer1",
            password="other test password",
            role="volunteer",
        )
        self.volunteer2 = get_user_model().objects.create_user(
            username="volunteer2",
            password="other test password",
            role="volunteer",
        )

    def test_view_logged_user_status_200_and_context(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:volunteer-detail", args=[self.volunteer1.id]))
        self.assertEqual(response.status_code, 200)

        self.assertIn("tasks_count", response.context)
        self.assertIn("reports_count", response.context)
        self.assertIn("tasks_completed", response.context)
        self.assertIn("tasks_in_progress", response.context)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:volunteer-detail", args=[self.volunteer1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_view_filtering_only_volunteers(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:volunteer-list"))

        for user in response.context["volunteer_list"]:
            self.assertEqual(user.role, "volunteer")


class VolunteerCreateViewTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
    def test_view_create_success(self):
        self.client.login(username="coordinator", password="test password")
        volunteer = {
            "username": "volunteer",
            "password1": "Complex1234!",
            "password2": "Complex1234!",
            "first_name": "test name",
            "last_name": "test last name",
            "role": "volunteer",
        }
        response = self.client.post(reverse("tasks:volunteer-create"), data=volunteer)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            get_user_model().objects.filter(
                username="volunteer",
                first_name="test name",
                last_name="test last name",
                role="volunteer",
            ).exists())

    def test_view_redirect_if_not_coordinator(self):
        self.client.login(username="volunteer", password="Complex1234!")
        response = self.client.get(reverse("tasks:volunteer-create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:volunteer-create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class VolunteerUpdateViewTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            password="other test password",
            role="volunteer",
            city="test city",
        )

    def test_view_update_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse(
            "tasks:volunteer-update", args=[self.volunteer.id]), {
            "username": "volunteer",
            "role": "volunteer",
            "city": "London",
        })
        self.assertRedirects(response, reverse("tasks:volunteer-list"))
        self.volunteer.refresh_from_db()
        self.assertEqual(self.volunteer.city, "London")

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.get(reverse("tasks:volunteer-update", args=[self.volunteer.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:volunteer-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class VolunteerDeleteViewTest(TestCase):
    def setUp(self):
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

    def test_view_delete_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:volunteer-delete", args=[self.volunteer.id]))
        self.assertRedirects(response, reverse("tasks:volunteer-list"))
        self.assertFalse(get_user_model().objects.filter(username="volunteer").exists())

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.get(reverse("tasks:volunteer-delete", args=[self.volunteer.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:volunteer-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class CategoryListViewTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.category1 = Category.objects.create(
            name="test category1",
            description="test description",
        )
        self.category2 = Category.objects.create(
            name="test category2",
            description="test description",
        )

    def test_view_logged_used_200_and_context(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("category_list", response.context)
        self.assertIn("search_form", response.context)

    def test_view_filtering_for_name(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:category-list") + "?name=test category1")
        categories = response.context["category_list"]
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "test category1")

    def test_view_pagination(self):
        self.client.login(username="coordinator", password="test password")
        for category in range(15):
            Category.objects.create(
                name=f"test category{category}",
                description="test description",
            )
        response = self.client.get(reverse("tasks:category-list"))
        self.assertEqual(len(response.context["category_list"]), 5)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:category-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class CategoryDetailViewTest(TestCase):
    def setUp(self):
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
        self.category1 = Category.objects.create(
            name="test category1",
            description="test description",
        )
        self.category2 = Category.objects.create(
            name="test category2",
            description="test description",
        )

    def test_view_logged_user_200(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:category-detail", args=[self.category1.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:category-detail", args=[self.category1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class CategoryCreateViewTest(TestCase):
    def setUp(self):
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

    def test_view_create_category_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:category-create"),
                                    {
                                        "name": "test category",
                                        "description": "test description",
                                    })
        self.assertRedirects(response, reverse("tasks:category-list"))
        self.assertTrue(Category.objects.filter(name="test category").exists())

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.post(reverse("tasks:category-create"))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:category-create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class CategoryUpdateViewTest(TestCase):
    def setUp(self):
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
        self.category = Category.objects.create(
            name="test category",
            description="test description",
        )

    def test_view_update_category_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:category-update", args=[self.category.id]), {
            "name": "Products",
            "description": "test description",
        })
        self.assertRedirects(response, reverse("tasks:category-list"))
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Products")

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.post(reverse("tasks:category-update", args=[self.category.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.post(reverse("tasks:category-update", args=[self.category.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class CategoryDeleteViewTest(TestCase):
    def setUp(self):
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
        self.category = Category.objects.create(
            name="test category",
            description="test description",
        )

    def test_view_delete_category_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:category-delete", args=[self.category.id]))
        self.assertRedirects(response, reverse("tasks:category-list"))
        self.assertFalse(Category.objects.filter(name="test category").exists())

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.post(reverse("tasks:category-delete", args=[self.category.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.post(reverse("tasks:category-delete", args=[self.category.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)
