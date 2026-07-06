from django.urls import path
from . import views

urlpatterns = [
    path('', views.members_list, name="members_list"),
    path('view/<int:member_id>/', views.member_detail, name="member_detail"),
    path('edit/<int:member_id>/', views.member_edit, name="member_edit"),
]
