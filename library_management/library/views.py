from django.shortcuts import render, redirect
from books.models import Book
from members.models import Member
from django.db.models import Count
from django.utils import timezone
from transactions.models import Transaction
from settings_app.models import IssueSettings
from notifications.models import Notification
from django.contrib.auth.decorators import login_required



@login_required(login_url="login")
def dashboard(request):
    today = timezone.localdate()
    total_books = Book.objects.count()
    total_member = Member.objects.count()
    recent_transactions = Transaction.objects.order_by("-created_at")[:4]
    total_issued = Transaction.objects.filter(status="issued").count()
    
    
    
    
    today = timezone.localdate()

    pending_fines = 0

    for transaction in Transaction.objects.filter(status="issued"):
        
        issue_settings = IssueSettings.objects.get(
            member_type=transaction.member.member_type
        )
        
        if today > transaction.due_date:
            pending_fines += (today - transaction.due_date).days * issue_settings.fine_per_day
    
    

    category_data = (
        Book.objects
        .values("category")
        .annotate(total=Count("id"))
    )

    labels = []
    counts = []

    for item in category_data:
        labels.append(item["category"])
        counts.append(item["total"])
        
       
    

    context = {
        "total_books": total_books,
        "total_member": total_member,
        "labels": labels,
        "counts": counts,
        "today": today,
        "recent_transactions": recent_transactions,
        "total_issued": total_issued,
        "pending_fines": pending_fines,
    }

    return render(request, "dashboard/dashboard.html", context)



def global_search(request):
    q = request.GET.get("q", "").strip().lower()

    if q == "dashboard":
        return redirect("dashboard")

    elif q in ["books", "book", "book page", "book list"]:
        return redirect("/books/")

    elif q == "add book" or q == "book add" or q == "books add" or q == "add books":
        return redirect("book_add")
    
    elif q in ["member", "members", "member list"]:
        return redirect("/members/")
    
    elif q in ["add member", "add members"]:
        return redirect("member_add")
    
    elif q in ["transactions", "transaction", "transaction list", "transaction list"]:
        return redirect("/transactions/")
    
    elif q in ["issue book", "issues book", "issue books", "issues books"]:
        return redirect("issue_book")
    
    else:
        return redirect("dashboard")