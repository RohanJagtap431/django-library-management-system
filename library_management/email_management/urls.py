from django.urls import path
from . import views

urlpatterns = [
    path("", views.email_dashboard, name="email_dashboard"),
    path("compose-email/", views.compose_email, name="compose_email"),
    path("history/", views.email_history, name="email_history"),
    path("clear-all-history/", views.clear_all_history,name="clear_all_history"),
    path("delete-email-history/<int:id>/", views.delete_email_history, name="delete_email_history"),
    path("view/<int:id>/", views.view_email_history, name="view_email_history"),
    path("templates/", views.email_templates, name="email_templates"),
    path("edit/<int:id>/", views.edit_email_template, name="edit_email_template"),
    path("preview/<str:email_type>/", views.preview_email, name="preview_email"),
]
