from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from tasks.models import CustomUser, Task, Category


def index(request: HttpRequest) -> HttpResponse:
    num_volunteers = CustomUser.objects.count()
    num_tasks = Task.objects.count()
    num_categories = Category.objects.count()
    context = {
        "num_volunteers": num_volunteers,
        "num_tasks": num_tasks,
        "num_categories": num_categories,
    }
    return render(request, "tasks/index.html", context=context)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    model = Category
