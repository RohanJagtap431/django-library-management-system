from django.db import models
from members.models import MEMBER_TYPE_CHOICES



class IssueSettings(models.Model):
    member_type = models.CharField(max_length=10, choices=MEMBER_TYPE_CHOICES, unique=True)
    max_books = models.PositiveIntegerField(default=3)
    loan_period = models.PositiveIntegerField(default=7)
    fine_per_day = models.PositiveIntegerField(default=5)
    
    def __str__(self):
        return self.member_type
    
class BookSettings(models.Model):
    low_stock_alert_limit = models.PositiveIntegerField(default=5)
    
    def __str__(self):
        return "Book Settings"
    
class NotificationSettings(models.Model):
    low_stock_alert = models.BooleanField(default=True)
    book_issue_alert = models.BooleanField(default=True)
    book_return_alert = models.BooleanField(default=True)
    overdue_alert = models.BooleanField(default=True)
    fine_alert = models.BooleanField(default=True)
    new_member_alert = models.BooleanField(default=True)
    notification_sound = models.BooleanField(default=True)
    show_badge_count = models.BooleanField(default=True)
    show_deskgtop_notification = models.BooleanField(default=True)
    new_book_alert = models.BooleanField(default=True)
    
    notification_tone = models.CharField(max_length=100, default="default")
    
    def __str__(self):
        return "Notification Settings"
    
    
    