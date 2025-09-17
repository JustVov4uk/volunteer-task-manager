from django.urls import path
from tasks.views import (test_view)


urlpatterns = [
    path("", test_view, name="index" ),
]

app_name = "tasks"