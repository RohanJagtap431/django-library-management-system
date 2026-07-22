from django.db import models
from members.models import Member


class EmailTemplate(models.Model):
    EMAIL_TYPES = [
        ("welcome", "Welcome Email"),
        ("book_issue", "Book Issue Email"),
        ("book_return", "Book Return Email"),
        ("overdue", "Overdue Reminder"),
    ]
    
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPES, unique=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.get_email_type_display()
    
    
class EmailHistory(models.Model):

    EMAIL_TYPES = [
        ("Compose", "Compose"),
        ("Welcome", "Welcome"),
        ("Book Issue", "Book Issue"),
        ("Book Return", "Book Return"),
        ("Overdue Reminder", "Overdue Reminder"),
    ]

    STATUS_CHOICES = [
        ("Sent", "Sent"),
        ("Failed", "Failed"),
    ]

    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return self.recipient
    
    
    