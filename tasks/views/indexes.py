from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from tasks.models import CustomUser, Task, Category, Report


@login_required
def index(request: HttpRequest) -> HttpResponse:
    if request.user.role == "coordinator":
        return redirect("tasks:coordinator-index")
    return redirect("tasks:volunteer-index")


@login_required
def coordinator_index(request: HttpRequest) -> HttpResponse:
    if request.user.role != "coordinator":
        raise PermissionDenied

    num_volunteers = CustomUser.objects.filter(role="volunteer").count()
    num_tasks = Task.objects.count()
    num_categories = Category.objects.count()
    num_reports = Report.objects.count()
    now = timezone.now()
    due_soon_until = now + timedelta(days=7)

    status_counts = (
        Task.objects
        .values("status")
        .annotate(count=Count("status"))
        .order_by()
    )
    active_tasks = Task.objects.exclude(status="completed")
    overdue_tasks = (
        active_tasks
        .filter(deadline__lt=now)
        .select_related("assigned_to", "category")
        .order_by("deadline")[:5]
    )
    due_soon_tasks = (
        active_tasks
        .filter(deadline__gte=now, deadline__lte=due_soon_until)
        .select_related("assigned_to", "category")
        .order_by("deadline")[:5]
    )
    unverified_reports = (
        Report.objects
        .filter(verified_at__isnull=True)
        .select_related("author", "task")
        .order_by("-created_at")[:5]
    )
    latest_tasks = (
        Task.objects
        .select_related("assigned_to", "category")
        .order_by("-id")[:5]
    )

    context = {
        "num_volunteers": num_volunteers,
        "num_tasks": num_tasks,
        "num_categories": num_categories,
        "num_reports": num_reports,
        "status_counts": list(status_counts),
        "overdue_tasks": overdue_tasks,
        "due_soon_tasks": due_soon_tasks,
        "unverified_reports": unverified_reports,
        "latest_tasks": latest_tasks,
        "overdue_count": active_tasks.filter(deadline__lt=now).count(),
        "due_soon_count": active_tasks.filter(
            deadline__gte=now,
            deadline__lte=due_soon_until,
        ).count(),
        "unverified_reports_count": Report.objects.filter(
            verified_at__isnull=True,
        ).count(),
    }
    return render(request, "tasks/index_coordinator.html", context=context)


@login_required
def volunteer_index(request: HttpRequest) -> HttpResponse:
    user = request.user
    my_tasks = (
        Task.objects
        .filter(assigned_to=user)
        .select_related("category", "created_by")
        .order_by("deadline")[:5]
    )
    my_reports = (
        Report.objects
        .filter(author=user)
        .select_related("task", "verified_by")
        .order_by("-created_at")[:5]
    )

    context = {
        "user": user,
        "my_tasks": my_tasks,
        "my_reports": my_reports,
        "assigned_tasks_count": Task.objects.filter(assigned_to=user).count(),
        "completed_tasks_count": Task.objects.filter(
            assigned_to=user,
            status="completed",
        ).count(),
        "reports_count": Report.objects.filter(author=user).count(),
    }

    return render(request, "tasks/index_volunteer.html", context=context)
