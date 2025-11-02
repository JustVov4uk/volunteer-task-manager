from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import Category, Task, Tag, Report


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


class TaskListViewTest(TestCase):
    def setUp(self):
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
            password="other test password2",
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
        self.tag1 = Tag.objects.create(
            name="urgent",
        )
        self.tag2 = Tag.objects.create(
            name="medicine",
        )
        self.task1 = Task.objects.create(
            title="test task1",
            category=self.category1,
            status="active",
            assigned_to=self.volunteer1,
        )
        self.task1.tags.add(self.tag1)

        self.task2 = Task.objects.create(
            title="test task2",
            category=self.category2,
            status="in_progress",
            assigned_to=self.volunteer2,
        )
        self.task2.tags.add(self.tag2)

    def test_view_coordinator_see_all_tasks(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:task-list"))

        self.assertEqual(response.status_code, 200)
        tasks = response.context["task_list"]
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task2, tasks)
        self.assertEqual(len(tasks), 2)

    def test_view_volunteer_see_only_yourself_tasks(self):
        self.client.login(username="volunteer1", password="other test password")
        response = self.client.get(reverse("tasks:task-list"))

        self.assertEqual(response.status_code, 200)
        tasks = response.context["task_list"]
        self.assertIn(self.task1, tasks)
        self.assertEqual(len(tasks), 1)

    def test_view_filtering_by_title(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:task-list")
                                   + "?title=test task1",
                                   )
        tasks = response.context["task_list"]
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.task1, tasks)
        self.assertNotIn(self.task2, tasks)

    def test_view_filtering_by_status(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:task-list")
                                   + "?status=in_progress",
                                   )
        tasks = response.context["task_list"]
        self.assertIn(self.task2, tasks)
        self.assertNotIn(self.task1, tasks)

    def test_view_filtering_by_category(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:task-list")
                                   + f"?category={self.category1.id}",
                                   )
        tasks = response.context["task_list"]
        self.assertIn(self.task1, tasks)
        self.assertNotIn(self.task2, tasks)

    def test_view_filtering_by_tag(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:task-list"), {"tags": [self.tag1.id]})
        tasks = response.context["task_list"]
        self.assertIn(self.task1, tasks)
        self.assertNotIn(self.task2, tasks)

    def test_view_filtering_by_assigned_to(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:task-list"), {"volunteer": self.volunteer1.id })
        tasks = response.context["task_list"]
        self.assertIn(self.task1, tasks)
        self.assertNotIn(self.task2, tasks)

    def test_view_pagination(self):
        self.client.login(username="coordinator", password="test password")
        for task in range(15):
            Task.objects.create(
                title=f"test task{task}"
            )
        response = self.client.get(reverse("tasks:task-list"))
        self.assertEqual(len(response.context["task_list"]), 5)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:task-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class TaskDetailViewTest(TestCase):
    def setUp(self):
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
            password="other test password2",
            role="volunteer",
        )
        self.task1 = Task.objects.create(
            title="test task1",
            assigned_to=self.volunteer1,
        )
        self.task2 = Task.objects.create(
            title="test task2",
            assigned_to=self.volunteer2,
        )

    def test_view_coordinator_see_all_tasks(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:task-detail", args=[self.task1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["task"], self.task1)

        response = self.client.get(reverse("tasks:task-detail", args=[self.task2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["task"], self.task2)

    def test_view_volunteer_see_only_yourself_tasks(self):
        self.client.login(username="volunteer1", password="other test password")
        response = self.client.get(reverse("tasks:task-detail", args=[self.task1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["task"], self.task1)

        response = self.client.get(reverse("tasks:task-detail", args=[self.task2.id]))
        self.assertEqual(response.status_code, 404)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:task-detail", args=[self.task1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class TaskCreateViewTest(TestCase):
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
        )

    def test_view_create_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:task-create"), {
            "title": "test task",
            "description": "test task",
            "created_by": self.coordinator.id,
            "assigned_to": self.volunteer.id,
            "status": "active",
            "category": self.category.id,
        })
        self.assertRedirects(response, reverse("tasks:task-list"))
        self.assertTrue(Task.objects.filter(title="test task", assigned_to=self.volunteer).exists())

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.post(reverse("tasks:task-create"))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:task-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class TaskUpdateViewTest(TestCase):
    def setUp(self):
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
            password="other test password2",
            role="volunteer",
        )
        self.category = Category.objects.create(
            name="test category",
        )
        self.task = Task.objects.create(
            title="test task",
            assigned_to=self.volunteer1,
            status="active",
        )

    def test_view_update_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:task-update", args=[self.task.id]), {
            "title": "test task",
            "description": "test task",
            "created_by": self.coordinator.id,
            "assigned_to": self.volunteer1.id,
            "status": "in_progress",
            "category": self.category.id,
        })

        self.assertRedirects(response, reverse("tasks:task-list"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "in_progress")

    @patch("tasks.views.notify_task_assigned")
    def test_view_check_notify_task_if_change_assigned_to(self, mock_notify):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:task-update", args=[self.task.id]), {
            "title": "test task",
            "description": "test task",
            "created_by": self.coordinator.id,
            "assigned_to": self.volunteer2.id,
            "status": "in_progress",
            "category": self.category.id,
        })

        self.assertRedirects(response, reverse("tasks:task-list"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.assigned_to, self.volunteer2)
        mock_notify.assert_called_once_with(self.task)

    def test_view_redirect_if_not_coordinator(self):
        self.client.login(username="volunteer", password="test password")
        response = self.client.post(reverse("tasks:task-update", args=[self.task.id]))
        self.assertEqual(response.status_code, 302)


class TaskDeleteViewTest(TestCase):
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
        self.task = Task.objects.create(
            title="test task",
            assigned_to=self.volunteer,
            status="in_progress",
        )

    def test_view_delete_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:task-delete", args=[self.task.id]))
        self.assertRedirects(response, reverse("tasks:task-list"))
        self.assertFalse(Task.objects.filter(title="test task").exists())

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.post(reverse("tasks:task-delete", args=[self.task.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:task-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class TagListViewTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.tag1 = Tag.objects.create(
            name="test tag1",
        )
        self.tag2 = Tag.objects.create(
            name="test tag2",
        )

    def test_view_status_code_200_and_context(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:tag-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("tag_list", response.context)
        self.assertIn("search_form", response.context)

    def test_view_filtering_by_name(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:tag-list") + "?name=test tag1")
        tags = response.context["tag_list"]
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].name, "test tag1")

    def test_view_pagination(self):
        self.client.login(username="coordinator", password="test password")
        for i in range(15):
            Tag.objects.create(
                name=f"tag{i}",
            )
        response = self.client.get(reverse("tasks:tag-list"))
        self.assertEqual(len(response.context["tag_list"]), 5)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:tag-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class TagDetailViewTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.tag = Tag.objects.create(
            name="test tag",
        )
    def test_view_status_code_200(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:tag-detail", args=[self.tag.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:tag-detail", args=[self.tag.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class TagCreateViewTest(TestCase):
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

    def test_view_create_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:tag-create"), data={
            "name": "test tag",
        })
        self.assertRedirects(response, reverse("tasks:tag-list"))
        self.assertEqual(Tag.objects.count(), 1)
        self.assertTrue(Tag.objects.filter(name="test tag").exists())

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.post(reverse("tasks:tag-create"))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:tag-create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class TagUpdateViewTest(TestCase):
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
        self.tag = Tag.objects.create(
            name="test tag",
        )

    def test_view_update_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:tag-update", args=[self.tag.id]), {
            "name": "medicine",
        })
        self.assertRedirects(response, reverse("tasks:tag-list"))
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, "medicine")

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.post(reverse("tasks:tag-update", args=[self.tag.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.post(reverse("tasks:tag-update", args=[self.tag.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class TagDeleteViewTest(TestCase):
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
        self.tag = Tag.objects.create(
            name="test tag",
        )

    def test_view_delete_success(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:tag-delete", args=[self.tag.id]))
        self.assertRedirects(response, reverse("tasks:tag-list"))
        self.assertFalse(Tag.objects.filter(name="test tag").exists())

    def test_view_permission_denied_if_not_coordinator(self):
        self.client.login(username="volunteer", password="other test password")
        response = self.client.post(reverse("tasks:tag-delete", args=[self.tag.id]))
        self.assertEqual(response.status_code, 403)

    def test_view_redirect_for_anonymous(self):
        response = self.client.post(reverse("tasks:tag-delete", args=[self.tag.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class ReportListViewTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.volunteer1 = get_user_model().objects.create_user(
            username="volunteer1",
            password="other test password1",
            role="volunteer",
        )
        self.volunteer2 = get_user_model().objects.create_user(
            username="volunteer2",
            password="other test password2",
            role="volunteer",
        )
        self.task1 = Task.objects.create(
            title="test task",
        )
        self.task2 = Task.objects.create(
            title="another task",
        )
        self.report1 = Report.objects.create(
            comment="test report",
            author=self.volunteer1,
            task=self.task1,
            verified_by=self.coordinator,
        )
        self.report2 = Report.objects.create(
            comment="another report",
            author=self.volunteer2,
            task=self.task2,
            verified_by=self.coordinator
        )

    def test_view_coordinator_see_all_reports(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.get(reverse("tasks:report-list"))
        self.assertEqual(response.status_code, 200)
        reports = response.context["report_list"]
        self.assertIn(self.report1, reports)
        self.assertIn(self.report2, reports)
        self.assertEqual(len(reports), 2)

    def test_view_volunteer_see_only_yourself_reports(self):
        self.client.login(username="volunteer1", password="other test password1")
        response = self.client.get(reverse("tasks:report-list"))
        self.assertEqual(response.status_code, 200)
        reports = response.context["report_list"]
        self.assertIn(self.report1, reports)
        self.assertNotIn(self.report2, reports)
        self.assertEqual(len(reports), 1)

    def test_view_filtering_by_author(self):
        self.client.login(username="volunteer1", password="other test password1")
        response = self.client.get(reverse("tasks:report-list")
                                   + "?author=volunteer1"
                                   )
        reports = response.context["report_list"]
        self.assertIn(self.report1, reports)
        self.assertNotIn(self.report2, reports)

    def test_view_filtering_by_author_filter(self):
        self.client.login(username="volunteer1", password="other test password1")
        response = self.client.get(reverse("tasks:report-list"), {"author_filter": self.volunteer1.id})
        reports = response.context["report_list"]
        self.assertIn(self.report1, reports)
        self.assertNotIn(self.report2, reports)

    def test_view_pagination(self):
        self.client.login(username="coordinator", password="test password")
        for report in range(15):
            Report.objects.create(
                comment=f"test report{report}",
                task=self.task1,
            )
        response = self.client.get(reverse("tasks:report-list"))
        self.assertEqual(len(response.context["report_list"]), 5)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:report-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class ReportDetailViewTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.volunteer1 = get_user_model().objects.create_user(
            username="volunteer1",
            password="other test password1",
            role="volunteer",
        )
        self.volunteer2 = get_user_model().objects.create_user(
            username="volunteer2",
            password="other test password2",
            role="volunteer",
        )
        self.task1 = Task.objects.create(
            title="test task",
        )
        self.task2 = Task.objects.create(
            title="another task",
        )
        self.report1 = Report.objects.create(
            comment="test report",
            author=self.volunteer1,
            task=self.task1,
            verified_by=self.coordinator,
        )
        self.report2 = Report.objects.create(
            comment="another report",
            author=self.volunteer2,
            task=self.task2,
            verified_by=self.coordinator
        )

    def test_view_coordinator_see_all_reports(self):
        self.client.login(username="coordinator", password="test password")

        response = self.client.get(reverse("tasks:report-detail", args=[self.task1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["report"], self.report1)

        response = self.client.get(reverse("tasks:report-detail", args=[self.task2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["report"], self.report2)

    def test_view_volunteer_see_only_yourself_reports(self):
        self.client.login(username="volunteer1", password="other test password1")
        response = self.client.get(reverse("tasks:report-detail", args=[self.task1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["report"], self.report1)

        response = self.client.get(reverse("tasks:report-detail", args=[self.task2.id]))
        self.assertEqual(response.status_code, 404)

    def test_view_redirect_for_anonymous(self):
        response = self.client.get(reverse("tasks:report-detail", args=[self.task1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


class ReportCreateViewTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            password="test password",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            password="test password",
            role="volunteer",
        )
        self.task = Task.objects.create(
            title="test task",
        )

    def test_view_create_success(self):
        self.client.login(username="volunteer", password="test password")
        response = self.client.post(reverse("tasks:report-create"), {
            "comment": "test report",
            "author": self.volunteer.id,
            "task": self.task.id,
        })

        self.assertRedirects(response, reverse("tasks:report-list"))
        self.assertTrue(Report.objects.filter(task=self.task.id).exists())

    def test_view_permission_denied_if_not_volunteer(self):
        self.client.login(username="coordinator", password="test password")
        response = self.client.post(reverse("tasks:report-create"))
        self.assertEqual(response.status_code, 403)
