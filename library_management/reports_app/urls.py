from django.urls import path
from . import views

urlpatterns = [
    path("", views.reports_dashboard, name="reports_dashboard"),
    path("fine-report/", views.fine_report, name="fine_report"),
    path("fine-report/export/", views.export_fine_csv, name="export_fine_csv"),
    path("pdf/", views.export_fine_pdf, name="export_fine_pdf"),
]
