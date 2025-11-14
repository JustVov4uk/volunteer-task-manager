from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from tasks.forms import ReportSearchForm, VolunteerReportForm, CoordinatorReportForm
from tasks.mixins import CoordinatorRequiredMixin
from tasks.models import Report
from tasks.notifications import notify_report_verified


class ReportListView(LoginRequiredMixin, generic.ListView):
    model = Report
    paginate_by = 5

    def get_context_data(
        self, *, object_list=..., **kwargs
    ):
        context = super(ReportListView, self).get_context_data(**kwargs)
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
                queryset = queryset.filter(
                    author__username__icontains=author_text)
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


class ReportUpdateView(LoginRequiredMixin,
                       CoordinatorRequiredMixin, UpdateView):
    model = Report
    form_class = CoordinatorReportForm
    success_url = reverse_lazy("tasks:report-list")

    def form_valid(self, form):
        form.instance.verified_by = self.request.user
        form.instance.verified_at = timezone.now()
        response = super().form_valid(form)
        notify_report_verified(self.object)
        return response


class ReportDeleteView(LoginRequiredMixin,
                       CoordinatorRequiredMixin, DeleteView):
    model = Report
    success_url = reverse_lazy("tasks:report-list")
