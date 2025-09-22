from django.urls import path

from tasks import views
from tasks.forms import CustomUserCreateForm
from tasks.views import (index,
                         CategoryListView,
                         CategoryDetailView,
                         TaskListView, TaskDetailView,
                         TagListView, TagDetailView,
                         ReportListView, ReportDetailView,
                         VolunteerListView,VolunteerDetailView,
                         CategoryCreateView,CategoryUpdateView,
                         CategoryDeleteView, VolunteerCreateView)

urlpatterns = [
    path("", index, name="index"),
    path("volunteers/", VolunteerListView.as_view(), name="volunteer-list"),
    path("volunteers/<int:pk>/", VolunteerDetailView.as_view(), name="volunteer-detail"),
    path("volunteers/create/", VolunteerCreateView.as_view(), name="volunteer-create"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("categories/create/", CategoryCreateView.as_view(), name="category-create"),
    path("categories/update/<int:pk>/", CategoryUpdateView.as_view(), name="category-update"),
    path("categories/delete/<int:pk>/", CategoryDeleteView.as_view(), name="category-delete"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tags/", TagListView.as_view(), name="tag-list"),
    path("tags/<int:pk>/", TagDetailView.as_view(), name="tag-detail"),
    path("reports/", ReportListView.as_view(), name="report-list"),
    path("reports/<int:pk>/", ReportDetailView.as_view(), name="report-detail"),
    path("coordinator/", views.coordinator_index, name="coordinator-index"),
    path("volunteer/", views.volunteer_index, name="volunteer-index"),
]

app_name = "tasks"
