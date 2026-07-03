from django.urls import path
from . import views


urlpatterns = [
    path('', views.books_list, name="books_list"),
    path('view/<int:book_id>/', views.book_detail, name="book_detail"),
    path('edit/<int:book_id>/', views.book_edit, name="book_edit"),
    path('delete/<int:book_id>/', views.book_delete, name="book_delete"),
    path('books/add/', views.book_add, name='book_add'),
]
