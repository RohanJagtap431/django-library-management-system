from django.urls import path
from . import views

urlpatterns = [
    path("", views.reports_dashboard, name="reports_dashboard"),
    path("fine-report/", views.fine_report, name="fine_report"),
    path("fine-report/export/", views.export_fine_csv, name="export_fine_csv"),
    path("fine-report/pdf/", views.export_fine_pdf, name="export_fine_pdf"),
    path("book-report/", views.book_report, name="book_report"),
    path("book-report/export/", views.export_book_csv, name="export_book_csv"),
    path("book-report/pdf/", views.export_book_pdf, name="export_book_pdf"),
    path("member-report/", views.member_report, name="member_report"),
    path("member-report/export/", views.export_member_csv, name="export_member_csv"),
    path("member-report/pdf/", views.export_member_pdf, name="export_member_pdf"),
    path("issue-return-report/", views.issue_return_report, name="issue_return_report"),
    path("issue-return-report/export/", views.export_issue_return_csv, name="export_issue_return_csv"),
    path("issue-return-report/pdf/", views.export_issue_return_pdf, name="export_issue_return_pdf"),
]
