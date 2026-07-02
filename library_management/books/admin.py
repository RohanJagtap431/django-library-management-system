from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['isbn', 'title', 'author', 'category']
    search_fields = ['isbn', 'title', 'author']
    list_filter = ['category', 'publisher', 'publication_year']
    ordering = ['-created_at']
    list_per_page = 10



