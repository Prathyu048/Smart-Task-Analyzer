from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Serve the frontend template at root
    path("", TemplateView.as_view(template_name="frontend.html"), name="home"),
    # Include the tasks app URLs (tasks/urls.py will import its own views)
    path("", include("tasks.urls")),
]
