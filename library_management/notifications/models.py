from django.db import models

NOTIFICATION_TYPE_CHOICES = [
    ("book_issued", "Book Issued"),
    ("book_returned", "Book Returned"),
    ("overdue", "Overdue"),
    ("low_stock", "Low Stock"),
    ("due_today", "Due Today"),
    ("fine", "Fine"),
    ("new_member", "New Member"),
    ("new_book", "New Book"),
    ("general", "General"),
]


class Notification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title