from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name="transaction_list"),
    path('issue-book/', views.issue_book, name="issue_book"),
    path("search-member/", views.search_member, name="search_member"),
    path("search-book/", views.search_book, name="search_book"),
]
