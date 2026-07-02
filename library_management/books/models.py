from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

CATEGORY_CHOICES = [
    ("Programming", "Programming"),
    ("Science", "Science"),
    ("Computer Science", "Computer Science"),
    ("Mathematics", "Mathematics"),
    ("History", "History"),
    ("Novel", "Novel"),
    ("Biography", "Biography"),
    ("Self Help", "Self Help"),
    ("Others", "Others"),
]

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    isbn = models.CharField(max_length=50, unique=True)
    publisher = models.CharField(max_length=100, blank=True)
    publication_year = models.IntegerField()
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()
    shelf_location = models.CharField(max_length=100, blank=True)
    book_cover = models.ImageField(upload_to="book_covers/", blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.title
    
    def is_available(self):
        return self.available_copies > 0
    
    def clean(self):
        super().clean()
        if self.publication_year > date.today().year:
            raise ValidationError({
                "publication_year": "Publication year cannot be in the future."
            })
            
        if self.total_copies < 1:
            raise ValidationError({
                "total_copies": "Total copies must be at least 1."
            })
            
        if self.available_copies < 0:
            raise ValidationError({
                "available_copies": "Available copies cannot be negative."
            })
            
        if self.available_copies > self.total_copies:
            raise ValidationError({
                "available_copies": "Available copies cannot be greater than total copies."
            })