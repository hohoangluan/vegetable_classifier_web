from django.urls import path

from . import views


app_name = "pages"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_landing_view, name="about"),
    path("pipeline/", views.pipeline_view, name="pipeline"),
    path("dataset/", views.dataset_view, name="dataset"),
]
