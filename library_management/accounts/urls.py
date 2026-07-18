from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),
    path("change-password/", views.change_password, name="change_password"),
    path('profile/', views.profile, name="profile"),
    path('edit-profile/', views.edit_profile, name="edit_profile"),
]
