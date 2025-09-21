from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic

from tasks.models import CustomUser, Task, Category, Tag, Report

@login_required
def index(request: HttpRequest) -> HttpResponse:
    if request.user.role =="coordinator":
        return redirect("tasks:coordinator-index")
    return redirect("tasks:volunteer-index")

@login_required
def coordinator_index(request: HttpRequest) -> HttpResponse:
    num_volunteers = CustomUser.objects.filter(role="volunteer").count()
    num_tasks = Task.objects.count()
    num_categories = Category.objects.count()
    num_tags = Tag.objects.count()
    num_reports = Report.objects.count()

    context = {
        "num_volunteers": num_volunteers,
        "num_tasks": num_tasks,
        "num_categories": num_categories,
        "num_tags": num_tags,
        "num_reports": num_reports,
    }
    return render(request, "tasks/index_coordinator.html", context=context)

@login_required
def volunteer_index(request: HttpRequest) -> HttpResponse:
    num_tasks = Task.objects.count()
    num_categories = Category.objects.count()

    context = {
        "num_tasks": num_tasks,
        "num_categories": num_categories,
    }

    return render(request, "tasks/index_volunteer.html", context=context)


class VolunteerListView(LoginRequiredMixin, generic.ListView):
    model = CustomUser
    template_name = "tasks/volunteer_list.html"
    context_object_name = "volunteer_list"

    def get_queryset(self):
        return CustomUser.objects.filter(role="volunteer")


class VolunteerDetailView(LoginRequiredMixin, generic.DetailView):
    model = CustomUser
    template_name = "tasks/volunteer_detail.html"
    context_object_name = "volunteer_detail"

    def get_queryset(self):
        return CustomUser.objects.filter(role="volunteer")

class CategoryListView(LoginRequiredMixin, generic.ListView):
    model = Category


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    model = Category


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task


class TagListView(LoginRequiredMixin, generic.ListView):
    model = Tag


class TagDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tag


class ReportListView(LoginRequiredMixin, generic.ListView):
    model = Report


class ReportDetailView(LoginRequiredMixin, generic.DetailView):
    model = Report
