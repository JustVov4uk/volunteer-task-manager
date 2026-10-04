from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Category, Report, Tag, Task


class Command(BaseCommand):
    help = "Create or update demo data for the public project demo."

    def handle(self, *args, **options):
        coordinator = self._user(
            username="administrator1",
            password="Me262VoV",
            role="coordinator",
            email="coordinator@example.com",
            first_name="Demo",
            last_name="Coordinator",
            is_staff=True,
            is_superuser=True,
        )
        tanya = self._user(
            username="vol_tanya",
            password="GoodPass123!",
            role="volunteer",
            email="vol_tanya@example.com",
            first_name="Tanya",
            last_name="Ivanova",
            city="Lviv",
        )
        mykola = self._user(
            username="vol_mykola",
            password="GoodPass123!",
            role="volunteer",
            email="vol_mykola@example.com",
            first_name="Mykola",
            last_name="Petrenko",
            city="Odesa",
        )
        iryna = self._user(
            username="vol_iryna",
            password="GoodPass123!",
            role="volunteer",
            email="vol_iryna@example.com",
            first_name="Iryna",
            last_name="Bondar",
            city="Zaporizhzhia",
        )

        categories = {
            "Humanitarian Aid": Category.objects.update_or_create(
                name="Humanitarian Aid",
                defaults={
                    "description": (
                        "Food, water, hygiene kits, and basic supplies "
                        "for civilians."
                    ),
                },
            )[0],
            "Medical Assistance": Category.objects.update_or_create(
                name="Medical Assistance",
                defaults={
                    "description": (
                        "Logistics for hospitals, clinics, and field "
                        "medical teams."
                    ),
                },
            )[0],
            "Evacuation Support": Category.objects.update_or_create(
                name="Evacuation Support",
                defaults={
                    "description": (
                        "Transport, registration, shelter, and route "
                        "coordination."
                    ),
                },
            )[0],
            "Reconstruction": Category.objects.update_or_create(
                name="Reconstruction",
                defaults={
                    "description": (
                        "Repair work for damaged homes and community "
                        "infrastructure."
                    ),
                },
            )[0],
        }

        tags = {
            name: Tag.objects.update_or_create(name=name)[0]
            for name in [
                "urgent",
                "logistics",
                "medical",
                "transport",
                "shelter",
                "food",
                "reconstruction",
                "coordination",
            ]
        }

        now = timezone.now()
        task_specs = [
            {
                "title": "Deliver food kits to displaced families",
                "description": (
                    "Prepare and deliver food packages to families "
                    "registered at the local aid center."
                ),
                "assigned_to": tanya,
                "status": "completed",
                "deadline": now - timedelta(days=5),
                "category": categories["Humanitarian Aid"],
                "tags": ["food", "logistics"],
            },
            {
                "title": "Transport medical kits to field clinic",
                "description": (
                    "Coordinate driver, route, and delivery confirmation "
                    "for urgent medical supplies."
                ),
                "assigned_to": mykola,
                "status": "in_progress",
                "deadline": now + timedelta(days=2),
                "category": categories["Medical Assistance"],
                "tags": ["urgent", "medical", "transport"],
            },
            {
                "title": "Register passengers for evacuation bus",
                "description": (
                    "Check passenger list, help with luggage, and "
                    "coordinate departure time."
                ),
                "assigned_to": tanya,
                "status": "active",
                "deadline": now + timedelta(days=6),
                "category": categories["Evacuation Support"],
                "tags": ["transport", "coordination"],
            },
            {
                "title": "Repair damaged community center windows",
                "description": (
                    "Collect materials and support the repair team before "
                    "the next weather change."
                ),
                "assigned_to": iryna,
                "status": "active",
                "deadline": now - timedelta(days=1),
                "category": categories["Reconstruction"],
                "tags": ["reconstruction", "urgent"],
            },
            {
                "title": "Prepare temporary shelter equipment",
                "description": (
                    "Sort blankets, heaters, and sleeping mats for the "
                    "railway station shelter point."
                ),
                "assigned_to": None,
                "status": "active",
                "deadline": now + timedelta(days=4),
                "category": categories["Evacuation Support"],
                "tags": ["shelter", "logistics"],
            },
            {
                "title": "Audit remaining warehouse supplies",
                "description": (
                    "Check stock levels and prepare a list of missing "
                    "items for the next purchase."
                ),
                "assigned_to": None,
                "status": "suspended",
                "deadline": None,
                "category": categories["Humanitarian Aid"],
                "tags": ["coordination", "logistics"],
            },
        ]

        tasks = {}
        for spec in task_specs:
            tag_names = spec.pop("tags")
            task, _ = Task.objects.update_or_create(
                title=spec["title"],
                defaults={
                    **spec,
                    "created_by": coordinator,
                },
            )
            task.tags.set([tags[name] for name in tag_names])
            tasks[task.title] = task

        self._report(
            task=tasks["Deliver food kits to displaced families"],
            author=tanya,
            verified_by=coordinator,
            verified_at=now - timedelta(days=3),
            comment=(
                "Food kits were delivered to the registered families. "
                "Two additional addresses were added for the next route."
            ),
        )
        self._report(
            task=tasks["Transport medical kits to field clinic"],
            author=mykola,
            verified_by=None,
            verified_at=None,
            comment=(
                "Driver and route are confirmed. The team is waiting for final "
                "pickup confirmation from the clinic coordinator."
            ),
        )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))

    def _user(self, username, password, **defaults):
        user_model = get_user_model()
        user, _ = user_model.objects.update_or_create(
            username=username,
            defaults=defaults,
        )
        user.set_password(password)
        user.save()
        return user

    def _report(self, task, author, comment, verified_by, verified_at):
        report, _ = Report.objects.update_or_create(
            task=task,
            author=author,
            defaults={
                "comment": comment,
                "verified_by": verified_by,
                "verified_at": verified_at,
            },
        )
        return report
