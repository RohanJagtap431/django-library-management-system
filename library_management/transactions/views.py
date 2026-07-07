from django.shortcuts import render
from .models import Transaction, STATUS_CHOICES
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date
from members.models import Member
from books.models import Book


def transaction_list(request):
    transactions = Transaction.objects.all()
    all_members = Member.objects.all()
    all_books = Book.objects.all()
    search = request.GET.get("search", "")
    status = request.GET.get("status")
    member = request.GET.get("member")
    book = request.GET.get("book")
    
    
    if search:
        transactions = transactions.filter(
            Q(issue_id__icontains=search) | Q(book__title__icontains=search) | Q(book__isbn__icontains=search) | Q(member__full_name__icontains=search) | Q(member__member_id__icontains=search)
        )
        
    if status:
        if status == "issued":
            transactions = transactions.filter(status="issued")

        elif status == "returned":
            transactions = transactions.filter(status="returned")

        elif status == "overdue":
            transactions = transactions.filter(
                status="issued",
                due_date__lt=date.today(),
            )
            
    if member:
        transactions = transactions.filter(member_id=member)
        
    if book:
        transactions = transactions.filter(book_id=book)

    
        
    paginator = Paginator(transactions, 7)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'transactions/transaction_list.html', {
        'page_obj': page_obj,
        'search': search,
        "status": status,
        "all_status": STATUS_CHOICES,
        "all_members": all_members,
        "member": member,
        "all_books": all_books,
        "book": book,
    })

