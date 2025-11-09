from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, DeleteView, UpdateView

from tasks.forms import TaskSearchForm, TaskForm
from tasks.mixins import CoordinatorRequiredMixin
from tasks.models import Task
from tasks.notifications import notify_task_assigned


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 5

    def get_context_data(
        self, *, object_list=..., **kwargs
    ):
        context = super(TaskListView, self).get_context_data(**kwargs)
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


class TaskUpdateView(LoginRequiredMixin, CoordinatorRequiredMixin, UpdateView):
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
