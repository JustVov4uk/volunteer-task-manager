from django.db.models import Count
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from tasks.forms import (CategoryForm, CustomUserCreateForm,
                         CustomUserUpdateForm, TaskForm,
                         TagForm, CustomUserSearchForm,
                         CategorySearchForm, TaskSearchForm,
                         TagSearchForm, ReportSearchForm,
                         VolunteerReportForm, CoordinatorReportForm)
from tasks.mixins import CoordinatorRequiredMixin
from tasks.models import CustomUser, Task, Category, Tag, Report
from tasks.notifications import notify_task_assigned, notify_report_verified


@login_required
def index(request: HttpRequest) -> HttpResponse:
    if request.user.role =="coordinator":
        return redirect("tasks:coordinator-index")
    return redirect("tasks:volunteer-index")

@login_required
def coordinator_index(request: HttpRequest) -> HttpResponse:
    if request.user.role !="coordinator":
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


class VolunteerListView(LoginRequiredMixin, generic.ListView):
    model = CustomUser
    template_name = "tasks/volunteer_list.html"
    context_object_name = "volunteer_list"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(VolunteerListView, self).get_context_data(**kwargs)
        username = self.request.GET.get("username")
        context["search_form"] = CustomUserSearchForm(
            initial={"username": username}
        )
        return context

    def get_queryset(self):
        queryset = CustomUser.objects.filter(role="volunteer")
        form = CustomUserSearchForm(self.request.GET)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            if username:
                queryset = queryset.filter(username__icontains=username)
        return queryset


class VolunteerDetailView(LoginRequiredMixin, generic.DetailView):
    model = CustomUser
    template_name = "tasks/volunteer_detail.html"
    context_object_name = "volunteer"

    def get_queryset(self):
        return (
            CustomUser.objects
            .filter(role="volunteer")
            .prefetch_related("assigned_tasks", "reports_authored")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volunteer = self.get_object()

        tasks = volunteer.assigned_tasks.all()
        context["tasks_count"] = tasks.count()
        context["reports_count"] = volunteer.reports_authored.count()
        context["tasks_completed"] = tasks.filter(status="completed").count()
        context["tasks_in_progress"] = tasks.filter(status="in_progress").count()

        return context


class VolunteerCreateView(LoginRequiredMixin, CoordinatorRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreateForm
    template_name = "tasks/volunteer_form.html"
    success_url = reverse_lazy("tasks:volunteer-list")


class VolunteerUpdateView(LoginRequiredMixin, CoordinatorRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = "tasks/volunteer_form.html"
    success_url = reverse_lazy("tasks:volunteer-list")


class VolunteerDeleteView(LoginRequiredMixin, CoordinatorRequiredMixin, DeleteView):
    model = CustomUser
    success_url = reverse_lazy("tasks:volunteer-list")
    template_name = "tasks/volunteer_confirm_delete.html"
    context_object_name = "volunteer"


class CategoryListView(LoginRequiredMixin, generic.ListView):
    model = Category
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name")
        context["search_form"] = CategorySearchForm(
            initial={"name": name}
        )
        return context

    def get_queryset(self):
        queryset = Category.objects.all()
        form = CategorySearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            if name:
                queryset = queryset.filter(name__icontains=name)
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    model = Category


class CategoryCreateView(LoginRequiredMixin, CoordinatorRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("tasks:category-list")


class CategoryUpdateView(LoginRequiredMixin, CoordinatorRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("tasks:category-list")


class CategoryDeleteView(LoginRequiredMixin, CoordinatorRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("tasks:category-list")

class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 5

    def get_context_data(
        self, *, object_list = ..., **kwargs
    ):
        context = super(TaskListView, self).get_context_data(**kwargs)
        title = self.request.GET.get("title")
        context["search_form"] = TaskSearchForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = (
            Task.objects
            .select_related("category", "created_by", "assigned_to")
            .prefetch_related("tags")
        )
        if self.request.user.role == "volunteer":
            queryset = queryset.filter(assigned_to=self.request.user)

        form = TaskSearchForm(self.request.GET)
        if form.is_valid():
            title = form.cleaned_data.get("title")
            status = form.cleaned_data.get("status")
            category = form.cleaned_data.get("category")
            tag = form.cleaned_data.get("tags")
            volunteer = form.cleaned_data.get("volunteer")
            if title:
                queryset = queryset.filter(title__icontains=title)
            if status:
                queryset = queryset.filter(status=status)
            if category:
                queryset = queryset.filter(category=category)
            if tag:
                queryset = queryset.filter(tags=tag)
            if volunteer:
                queryset = queryset.filter(assigned_to=volunteer)
        return queryset


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task

    def get_queryset(self):
        queryset = (
            Task.objects
            .select_related("category", "created_by", "assigned_to")
            .prefetch_related("tags")
        )
        if self.request.user.role == "volunteer":
            queryset = queryset.filter(assigned_to=self.request.user)
        return queryset


class TaskCreateView(LoginRequiredMixin, CoordinatorRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        notify_task_assigned(self.object)
        return response


class TaskUpdateView(LoginRequiredMixin,CoordinatorRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks:task-list")

    def form_valid(self, form):
        assigned_changed = "assigned_to" in form.changed_data
        response = super().form_valid(form)
        if assigned_changed:
            notify_task_assigned(self.object)
        return response


class TaskDeleteView(LoginRequiredMixin, CoordinatorRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy("tasks:task-list")

class TagListView(LoginRequiredMixin, generic.ListView):
    model = Tag
    paginate_by = 5

    def get_context_data(
        self, *, object_list = ..., **kwargs
    ):
        context = super(TagListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name")
        context["search_form"] = TagSearchForm(
            initial={"name": name}
        )
        return context

    def get_queryset(self):
        queryset = Tag.objects.all()
        form = TagSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            if name:
                queryset = queryset.filter(name__icontains=name)
        return queryset


class TagDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tag


class TagCreateView(LoginRequiredMixin, CoordinatorRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy("tasks:tag-list")


class TagUpdateView(LoginRequiredMixin, CoordinatorRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy("tasks:tag-list")


class TagDeleteView(LoginRequiredMixin, CoordinatorRequiredMixin, DeleteView):
    model = Tag
    success_url = reverse_lazy("tasks:tag-list")


class ReportListView(LoginRequiredMixin, generic.ListView):
    model = Report
    paginate_by = 5

    def get_context_data(
        self, *, object_list = ..., **kwargs
    ):
        context = super(ReportListView, self).get_context_data(**kwargs)
        author = self.request.GET.get("author")
        context["search_form"] = ReportSearchForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = (
            Report.objects
            .select_related("author", "task", "verified_by")
        )
        if self.request.user.role == "volunteer":
            queryset = queryset.filter(author=self.request.user)

        form = ReportSearchForm(self.request.GET)
        if form.is_valid():
            author_text = form.cleaned_data.get("author")
            author_filter = form.cleaned_data.get("author_filter")
            created_filter = form.cleaned_data.get("created_filter")
            if author_text:
                queryset = queryset.filter(author__username__icontains=author_text)
            if author_filter:
                queryset = queryset.filter(author=author_filter)
            if created_filter:
                queryset = queryset.filter(created_at__date=created_filter)
        return queryset


class ReportDetailView(LoginRequiredMixin, generic.DetailView):
    model = Report

    def get_queryset(self):
        queryset = (
            Report.objects
            .select_related("author", "task", "verified_by")
        )
        if self.request.user.role == "volunteer":
            queryset = queryset.filter(author=self.request.user)
        return queryset


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = VolunteerReportForm
    success_url = reverse_lazy("tasks:report-list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "volunteer":
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ReportUpdateView(LoginRequiredMixin, CoordinatorRequiredMixin, UpdateView):
    model = Report
    form_class = CoordinatorReportForm
    success_url = reverse_lazy("tasks:report-list")

    def form_valid(self, form):
        form.instance.verified_by = self.request.user
        form.instance.verified_at = timezone.now()
        response = super().form_valid(form)
        notify_report_verified(self.object)
        return response


class ReportDeleteView(LoginRequiredMixin, CoordinatorRequiredMixin, DeleteView):
    model = Report
    success_url = reverse_lazy("tasks:report-list")
