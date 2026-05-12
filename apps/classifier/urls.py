from django.urls import path

from . import views


app_name = "classifier"

urlpatterns = [
    path("", views.classify_view, name="classify"),
    path("result/", views.result_view, name="result"),
]
