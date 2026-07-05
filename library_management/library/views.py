from django.shortcuts import render, redirect
from books.models import Book
from members.models import Member
from django.db.models import Count
from django.utils import timezone


def login_page(request):
    return render(request, 'auth/login.html')

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def dashboard(request):
    today = timezone.localtime()
    total_books = Book.objects.count()
    total_member = Member.objects.count()

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
    
    else:
        return redirect("dashboard")