from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from books.models import Book
from django.db.models import Sum
from django.utils import timezone
from transactions.models import Transaction

@login_required(login_url="login")
def reports_dashboard(request):
    today = timezone.localdate()
    
    total_books = Book.objects.aggregate(
        total=Sum("total_copies")
    )["total"] or 0
    
    available_books = Book.objects.aggregate(
        total=Sum("available_copies")
    )["total"] or 0
    
    total_issued = Transaction.objects.filter(status="issued").count()
    
    total_returned = Transaction.objects.filter(status="returned").count()
    
    overdue_books = Transaction.objects.filter(
        due_date__lt=today,
        status="issued"
    ).count()
    
    total_fine = Transaction.objects.aggregate(
        total = Sum("fine")
    )["total"] or 0
    
    
    context = {
        "total_books": total_books,
        "available_books": available_books,
        "total_issued": total_issued,
        "total_returned": total_returned,
        "overdue_books": overdue_books,
        "total_fine": total_fine,
    }
    return render(request, "reports/reports_dashboard.html", context)


@login_required(login_url="login")
def fine_report(request):

    transactions = Transaction.objects.filter(fine__gt=0)

    total_fine = transactions.aggregate(
        total=Sum("fine")
    )["total"] or 0

    context = {
        "transactions": transactions,
        "total_fine": total_fine,
    }

    return render(
        request,
        "reports/fine_report.html",
        context,
    )
