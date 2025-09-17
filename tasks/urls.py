from django.urls import path
from tasks.views import index, CategoryListView

urlpatterns = [
    path("", index, name="index"),
    path("category/", CategoryListView.as_view(), name="category-list"),
]

app_name = "tasks"
