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