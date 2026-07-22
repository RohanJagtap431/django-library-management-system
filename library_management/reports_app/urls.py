from django.urls import path
from . import views

urlpatterns = [
    path("", views.reports_dashboard, name="reports_dashboard"),
    path("fine-report/", views.fine_report, name="fine_report"),
]
