from django.urls import path

from tasks import views
from tasks.views import (index,
                         CategoryListView,
                         CategoryDetailView,
                         TaskListView, TaskDetailView,
                         TagListView, TagDetailView, ReportListView, ReportDetailView)

urlpatterns = [
    path("", index, name="index"),
    path("category/", CategoryListView.as_view(), name="category-list"),
    path("category/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
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
