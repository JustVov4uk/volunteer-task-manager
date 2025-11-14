from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

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

    status_counts = (Task.objects.values("status")
                     .annotate(count=Count("status"))
                     .order_by()
                )

    context = {
        "num_volunteers": num_volunteers,
        "num_tasks": num_tasks,
        "num_categories": num_categories,
        "num_reports": num_reports,
        "status_counts": list(status_counts),
    }
    return render(request, "tasks/index_coordinator.html", context=context)


@login_required
def volunteer_index(request: HttpRequest) -> HttpResponse:
    user = request.user
    num_tasks = Task.objects.count()
    num_categories = Category.objects.count()

    context = {
        "user": user,
        "num_tasks": num_tasks,
        "num_categories": num_categories,
    }

    return render(request, "tasks/index_volunteer.html", context=context)
