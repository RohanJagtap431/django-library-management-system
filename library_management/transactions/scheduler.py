from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from .models import Transaction
from .views import send_overdue_email
from datetime import datetime, timedelta

def check_overdue_books():

    overdue_transactions = Transaction.objects.filter(
        status="issued",
        due_date__lt=date.today(),
    )

    for transaction in overdue_transactions:
        if transaction.last_reminder_sent == date.today():
            continue
        
        print(transaction.member.email)
        print("Sending mail...")
        send_overdue_email(transaction)
        

scheduler = BackgroundScheduler()


def start_scheduler():

    if not scheduler.running:

        scheduler.add_job(
            check_overdue_books,
            "cron",
            hour=9,
            minute=0,
            id="overdue_reminder_job",
            replace_existing=True,
        )

        scheduler.start()

        print("Overdue Scheduler Started")
        