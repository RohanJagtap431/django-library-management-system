from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name="notification_list"),
    path('mark-all-as-read/', views.mark_all_as_read, name="mark_all_as_read"),
]
