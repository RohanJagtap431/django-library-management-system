from django.core.management.base import BaseCommand
from transactions.scheduler import check_overdue_books


class Command(BaseCommand):
    help = "Send overdue reminder emails"

    def handle(self, *args, **kwargs):
        check_overdue_books()
        self.stdout.write(
            self.style.SUCCESS("Overdue reminder emails sent successfully.")
        )