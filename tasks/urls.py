from django.urls import path

from tasks import views
from tasks.views import (index,
                         CategoryListView,
                         CategoryDetailView,
                         TaskListView, TaskDetailView)

urlpatterns = [
    path("", index, name="index"),
    path("category/", CategoryListView.as_view(), name="category-list"),
    path("category/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("coordinator/", views.coordinator_index, name="coordinator-index"),
    path("volunteer/", views.volunteer_index, name="volunteer-index"),
]

app_name = "tasks"
