from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from tasks.forms import CustomUserSearchForm, CustomUserCreateForm, CustomUserUpdateForm
from tasks.mixins import CoordinatorRequiredMixin
from tasks.models import CustomUser


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
        context["tasks_in_progress"] = tasks.filter(
            status="in_progress").count()

        return context


class VolunteerCreateView(LoginRequiredMixin,
                          CoordinatorRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreateForm
    template_name = "tasks/volunteer_form.html"
    success_url = reverse_lazy("tasks:volunteer-list")


class VolunteerUpdateView(LoginRequiredMixin,
                          CoordinatorRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = "tasks/volunteer_form.html"
    success_url = reverse_lazy("tasks:volunteer-list")


class VolunteerDeleteView(LoginRequiredMixin,
                          CoordinatorRequiredMixin, DeleteView):
    model = CustomUser
    success_url = reverse_lazy("tasks:volunteer-list")
    template_name = "tasks/volunteer_confirm_delete.html"
    context_object_name = "volunteer"
