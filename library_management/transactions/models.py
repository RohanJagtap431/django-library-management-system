from django.db import models
from books.models import Book
from members.models import Member


STATUS_CHOICES = [
    ("issued", "Issued"),
    ("returned", "Returned"),
]


class Transaction(models.Model):
    issue_id = models.CharField(max_length=50, unique=True, editable=False)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="issued")
    fine = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reminder_sent = models.DateField(null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        if not self.issue_id:
            last_issue = Transaction.objects.order_by("-id").first()

            if last_issue:
                last_id = int(last_issue.issue_id[3:])
                self.issue_id = f"ISS{last_id + 1:04d}"
            else:
                self.issue_id = "ISS0001"

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.issue_id