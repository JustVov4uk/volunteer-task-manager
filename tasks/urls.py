from django.urls import path
from tasks import views
from tasks.views import (index, CategoryListView,
                         CategoryDetailView,
                         TaskListView, TaskDetailView,
                         TagListView, TagDetailView,
                         ReportListView, ReportDetailView,
                         VolunteerListView, VolunteerDetailView,
                         CategoryCreateView, CategoryUpdateView,
                         CategoryDeleteView, VolunteerCreateView,
                         VolunteerUpdateView, VolunteerDeleteView,
                         TaskCreateView, TaskUpdateView, TaskDeleteView,
                         TagCreateView, TagUpdateView, TagDeleteView,
                         ReportCreateView, ReportUpdateView,
                         ReportDeleteView)


urlpatterns = [
    path("", index, name="index"),
    path("volunteers/", VolunteerListView.as_view(), name="volunteer-list"),
    path("volunteers/<int:pk>/", VolunteerDetailView.as_view(), name="volunteer-detail"),
    path("volunteers/create/", VolunteerCreateView.as_view(), name="volunteer-create"),
    path("volunteers/update/<int:pk>/", VolunteerUpdateView.as_view(), name="volunteer-update"),
    path("volunteers/delete/<int:pk>/", VolunteerDeleteView.as_view(), name="volunteer-delete"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("categories/create/", CategoryCreateView.as_view(), name="category-create"),
    path("categories/update/<int:pk>/", CategoryUpdateView.as_view(), name="category-update"),
    path("categories/delete/<int:pk>/", CategoryDeleteView.as_view(), name="category-delete"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/update/<int:pk>/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/delete/<int:pk>/", TaskDeleteView.as_view(), name="task-delete"),
    path("tags/", TagListView.as_view(), name="tag-list"),
    path("tags/<int:pk>/", TagDetailView.as_view(), name="tag-detail"),
    path("tags/create/", TagCreateView.as_view(), name="tag-create"),
    path("tags/update/<int:pk>/", TagUpdateView.as_view(), name="tag-update"),
    path("tags/delete/<int:pk>/", TagDeleteView.as_view(), name="tag-delete"),
    path("reports/", ReportListView.as_view(), name="report-list"),
    path("reports/<int:pk>/", ReportDetailView.as_view(), name="report-detail"),
    path("reports/create/", ReportCreateView.as_view(), name="report-create"),
    path("reports/update/<int:pk>/", ReportUpdateView.as_view(), name="report-update"),
    path("reports/delete/<int:pk>/", ReportDeleteView.as_view(), name="report-delete"),
    path("coordinator/", views.coordinator_index, name="coordinator-index"),
    path("volunteer/", views.volunteer_index, name="volunteer-index"),
]

app_name = "tasks"
