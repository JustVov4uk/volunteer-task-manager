from django.contrib.auth import get_user_model
from django.test import TestCase
from tasks.forms import (CategoryForm,
                         CategorySearchForm,
                         CustomUserCreateForm,
                         CustomUserUpdateForm,
                         CustomUserSearchForm,
                         TaskForm, TaskSearchForm,
                         TagForm, TagSearchForm,
                         VolunteerReportForm, CoordinatorReportForm,
                         ReportSearchForm)
from tasks.models import Category, Tag, Task


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


class CustomUserCreateFormTest(TestCase):
    def test_form_valid_with_correct_data(self):
        form_data = {
            "username": "user",
            "password1": "test password",
            "password2": "test password",
            "first_name": "test first",
            "last_name": "test last",
            "email": "test@email.com",
            "role": "volunteer",
            "phone_number": "123456789",
            "city": "test city",
        }
        form = CustomUserCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_if_username_is_empty(self):
        form_data = {
            "username": "",
        }
        form = CustomUserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_form_if_form_has_all_fields(self):
        fields = [
            "username", "role", "first_name", "last_name",
            "email", "phone_number", "city", "profile_image",
            "password1", "password2",
        ]
        form = CustomUserCreateForm()
        self.assertEqual(list(form.fields.keys()), fields)


class CustomUserUpdateFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="old_user",
            first_name="old",
            last_name="user",
            email="old@gmail.com",
            role="volunteer",
            phone_number="123456789",
            city="old city",
        )
    def test_form_update_exist_volunteer(self):
        form_data = {
            "username": "new_user",
            "first_name": "new",
            "last_name": "user",
            "email": "new@gmail.com",
            "role": "volunteer",
            "phone_number": "987654321",
            "city": "new city",
        }
        form = CustomUserUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.username, "new_user")
        self.assertEqual(updated_user.first_name, "new")
        self.assertEqual(updated_user.last_name, "user")
        self.assertEqual(updated_user.email, "new@gmail.com")
        self.assertEqual(updated_user.phone_number, "987654321")
        self.assertEqual(updated_user.city, "new city")

    def test_form_valid_when_update_a_few_fields(self):
        form_data = {
            "username": "old_user",
            "first_name": "old",
            "last_name": "user",
            "email": "old@gmail.com",
            "role": "volunteer",
            "phone_number": "987654321",
            "city": "new city",
        }
        form = CustomUserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())


class CustomUserSearchFormTest(TestCase):
    def test_form_valid_with_input_username(self):
        form_data = {
            "username": "test_user",
        }
        form = CustomUserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "test_user")

    def test_form_valid_when_input_username_is_empty(self):
        form_data = {
            "username": "",
        }
        form = CustomUserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "")

    def test_form_with_placeholder(self):
        placeholder = CustomUserSearchForm().fields["username"].widget.attrs["placeholder"]
        self.assertEqual(placeholder, "Search by username")


class TaskFormTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            role="volunteer",
        )
        self.category = Category.objects.create(
            name="Test Category",
        )
        self.tag = Tag.objects.create(
            name="Test Tag",
        )

    def test_form_valid_with_all_fields(self):
        form_data = {
            "title": "test title",
            "description": "test description",
            "created_by": self.coordinator.id,
            "assigned_to": self.volunteer.id,
            "status": "active",
            "deadline": "2019-07-30T12:00",
            "category": self.category.id,
            "tags": [self.tag.id]
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_deadline_widget_type_is_datetime_local(self):
        form = TaskForm()
        widget = form.fields["deadline"].widget
        self.assertEqual(getattr(widget, "input_type", None), "datetime-local")

    def test_form_querysets_filtered_in_init(self):
        form = TaskForm()
        assigned_queryset = form.fields["assigned_to"].queryset
        created_queryset = form.fields["created_by"].queryset

        self.assertIn(self.volunteer, assigned_queryset)
        self.assertNotIn(self.coordinator, assigned_queryset)

        self.assertIn(self.coordinator, created_queryset)
        self.assertNotIn(self.volunteer, created_queryset)


class TaskSearchFormTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            role="volunteer",
        )
        self.category = Category.objects.create(
            name="Test Category",
        )
        self.tag = Tag.objects.create(
            name="Test Tag",
        )
    def test_form_valid_for_all_filters(self):
        form_data = {
            "title": "test title",
            "status": "active",
            "category": self.category.id,
            "tags": self.tag.id,
            "volunteer": self.volunteer.id,
        }
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_valid_with_empty_filters(self):
        form_data = {
            "title": "",
            "status": "",
            "category": "",
            "tags": "",
            "volunteer": "",
        }
        form = TaskSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_status_has_choices(self):
        form = TaskSearchForm()
        choices = [choice[0] for choice in form.fields["status"].choices if choice[0]]
        self.assertEqual(choices, ["active", "in_progress", "completed", "suspended"])

    def test_form_fields_category_tags_volunteer_with_empty_label(self):
        form = TaskSearchForm()
        self.assertEqual(form.fields["category"].empty_label, "All categories")
        self.assertEqual(form.fields["tags"].empty_label, "All tags")
        self.assertEqual(form.fields["volunteer"].empty_label, "All volunteers")

    def test_form_placeholder_in_title(self):
        form = TaskSearchForm()
        placeholder = form.fields["title"].widget.attrs["placeholder"]
        self.assertEqual(placeholder, "Search by title")


class TagFormTest(TestCase):
    def test_form_valid_with_field_name(self):
        form_data = {
            "name": "test name",
        }
        form = TagForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_if_name_is_empty(self):
        form_data = {
            "name": "",
        }
        form = TagForm(data=form_data)
        self.assertIn("name", form.errors)


class TagSearchFormTest(TestCase):
    def test_form_valid_with_name_filled(self):
        form_data = {
            "name": "test name",
        }
        form = TagSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "test name")

    def test_form_valid_if_name_field_is_empty(self):
        form_data = {
            "name": "",
        }
        form = TagSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "")

    def test_form_with_placeholder(self):
        form = TagSearchForm()
        placeholder = form.fields["name"].widget.attrs["placeholder"]
        self.assertEqual(placeholder, "Search by name")


class VolunteerReportFormTest(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username="author",
            role="volunteer",
        )
        self.other_author = get_user_model().objects.create_user(
            username="other_author",
            role="volunteer",
        )
        self.task = Task.objects.create(
            title="test title",
            assigned_to=self.author,
        )
        self.other_task = Task.objects.create(
            title="other test title",
            assigned_to=self.other_author,
        )

    def test_form_with_user_in_init(self):
        form = VolunteerReportForm(user=self.author)
        task_queryset = form.fields["task"].queryset

        self.assertIn(self.task, task_queryset)
        self.assertNotIn(self.other_task, task_queryset)
        self.assertEqual(task_queryset.count(), 1)

    def test_form_without_user_in_init(self):
        form = VolunteerReportForm()
        task_queryset = form.fields["task"].queryset
        self.assertEqual(task_queryset.count(), 2)
        self.assertIn(self.task, task_queryset)
        self.assertIn(self.other_task, task_queryset)

    def test_form_valid_with_comment_and_task(self):
        form_data = {
            "comment": "test comment",
            "task": self.task,
        }
        form = VolunteerReportForm(data=form_data)
        self.assertTrue(form.is_valid())


class CoordinatorReportFormTest(TestCase):
    def setUp(self):
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            role="coordinator",
        )
        self.other_coordinator = get_user_model().objects.create_user(
            username="other_coordinator",
            role="coordinator",
        )
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            role="volunteer",
        )

    def test_form_with_only_coordinator_in_init(self):
        form = CoordinatorReportForm()
        verified_queryset = form.fields["verified_by"].queryset

        self.assertIn(self.coordinator, verified_queryset)
        self.assertIn(self.other_coordinator, verified_queryset)
        self.assertNotIn(self.volunteer, verified_queryset)
        self.assertEqual(verified_queryset.count(), 2)

    def test_form_with_widget(self):
        form = CoordinatorReportForm()
        widget = form.fields["verified_at"].widget
        self.assertEqual(getattr(widget, "input_type", None), "datetime-local")


class ReportSearchFormTest(TestCase):
    def setUp(self):
        self.volunteer = get_user_model().objects.create_user(
            username="volunteer",
            role="volunteer",
        )
        self.other_volunteer = get_user_model().objects.create_user(
            username="other_volunteer",
            role="volunteer",
        )
        self.coordinator = get_user_model().objects.create_user(
            username="coordinator",
            role="coordinator",
        )
    def test_form_valid_with_input_data(self):
        form_data = {
            "author": "test author",
        }
        form = ReportSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["author"], "test author")

    def test_form_author_filter_equal_role_volunteer(self):
        form = ReportSearchForm()
        filter_queryset = form.fields["author_filter"].queryset

        self.assertIn(self.volunteer, filter_queryset)
        self.assertIn(self.other_volunteer, filter_queryset)
        self.assertNotIn(self.coordinator, filter_queryset)
        self.assertEqual(filter_queryset.count(), 2)

    def test_form_with_widget(self):
        form = ReportSearchForm()
        widget = form.fields["created_filter"].widget
        self.assertEqual(getattr(widget, "input_type", None), "date")

    def test_form_with_placeholder(self):
        form = ReportSearchForm()
        placeholder = form.fields["author"].widget.attrs["placeholder"]
        self.assertEqual(placeholder, "Search by author")
