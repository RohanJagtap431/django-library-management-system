from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('dashboard/', views.dashboard, name="dashboard"),
    path("search/", views.global_search, name="global_search"),
]
