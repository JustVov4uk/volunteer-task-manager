from django.urls import path

from tasks import views
from tasks.views import index, CategoryListView

urlpatterns = [
    path("", index, name="index"),
    path("category/", CategoryListView.as_view(), name="category-list"),
    path("coordinator/", views.coordinator_index, name="coordinator-index"),
    path("volunteer/", views.volunteer_index, name="volunteer-index"),
]

app_name = "tasks"
