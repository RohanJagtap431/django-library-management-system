from django.db import models


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
    
    
    def __str__(self):
        return self.get_email_type_display()