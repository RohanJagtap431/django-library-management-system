from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction, STATUS_CHOICES
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from members.models import Member
from books.models import Book
from django.http import JsonResponse
from django.contrib import messages
from datetime import date, timedelta

FINE_PER_DAY = 10

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
                due_date__lt = timezone.localdate(),
            )
            
    if member:
        transactions = transactions.filter(member_id=member)
        
    if book:
        transactions = transactions.filter(book_id=book)
        
    
    today = timezone.localdate()

    for transaction in transactions:
        if transaction.status == "issued":
            if today > transaction.due_date:
                transaction.current_fine = (today - transaction.due_date).days * FINE_PER_DAY
            else:
                transaction.current_fine = 0
        else:
            transaction.current_fine = transaction.fine

    
        
    paginator = Paginator(transactions, 8)
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
        "today": timezone.localdate(),
    })

def issue_book(request):
    member_error = None
    book_error = None
    
        
    members = Member.objects.filter(status="active")
    books = Book.objects.filter(available_copies__gt=0)
    
    if request.method == 'POST':
        member_id = request.POST.get("member")
        book_id = request.POST.get("book")
        
        if not member_id:
            member_error = "Please select a member."

        if not book_id:
            book_error = "Please select a book."
            
        if member_error or book_error:
            context = {
                "members": members,
                "books": books,
                "member_error": member_error,
                "book_error": book_error,
            }
            return render(request, "transactions/issue_book.html", context)    
        
        
        member = Member.objects.get(id=member_id)
        book = Book.objects.get(id=book_id)
        
        issued_books = Transaction.objects.filter(
            member=member,
            status="issued"
        ).count()
        
        same_book = Transaction.objects.filter(
            member=member,
            book=book,
            status="issued"
        ).exists()

        

        if member.status != "active":
            member_error = "Selected member is inactive."

        if book.available_copies <= 0:
            book_error = "Selected book is currently unavailable."
            
        if issued_books >= 3:
            member_error = "This member has reached the maximum issue limit (3 books)."
            
        if same_book:
            book_error ="This book is already issued to this member."
        
        if member_error or book_error:
            context = {
                "members": members,
                "books": books,
                "member_error": member_error,
                "book_error": book_error,
                
            }
            return render(request, "transactions/issue_book.html", context)
        
        
        loan_period = 7

        due_date = date.today() + timedelta(days=loan_period)

        Transaction.objects.create(
            member=member,
            book=book,
            due_date=due_date,
        )

        book.available_copies -= 1
        book.save()

        messages.success(request, "Book issued successfully.")

        return redirect("issue_book")
    
    context = {
        "members": members,
        "books": books,
        "member_error": member_error,
        "book_error": book_error,
    }

    return render(request, "transactions/issue_book.html", context)


def return_book(request, issue_id):
    transaction = get_object_or_404(
        Transaction,
        issue_id=issue_id
    )
    
    if request.method == "POST":
        if transaction.status == "returned":
            return redirect("transaction_list")
        
        transaction.return_date = timezone.localdate()
        
        transaction.status = "returned"
        
        return_date = timezone.localdate()
        
        if return_date > transaction.due_date:
            late_days = (return_date - transaction.due_date).days
        else:
            late_days = 0
            
        if late_days > 0:
            fine =late_days * FINE_PER_DAY
        else:
            fine = 0
        
        transaction.fine = fine
        
        transaction.book.available_copies += 1
        
        transaction.book.save()
        transaction.save()
        
        
        
        return redirect("transaction_list")
        
        
            
            
    
    if transaction.due_date < timezone.localdate():
        status = "Overdue"
    else:
        status = "Issued"
        
    return_date = timezone.localdate()
    
    if return_date > transaction.due_date:
        late_days = (return_date - transaction.due_date).days
    else:
        late_days = 0
        
    if late_days > 0:
        fine =late_days * FINE_PER_DAY
    else:
        fine = 0
    
    context= {
        "transaction": transaction,
        "status": status,
        "return_date": return_date,
        "late_days": late_days,
        "fine": fine,
        "FINE_PER_DAY": FINE_PER_DAY,
    }
    
    return render(request, "transactions/return_book.html", context)


def search_member(request):
    query = request.GET.get("q", "").strip()
    
    if not query:
        return JsonResponse({"members": []})
    
    members = Member.objects.filter(
        Q(member_id__icontains=query) | Q(full_name__icontains=query)
    )[:10]
    
    member_data = []

    for member in members:
        member_data.append({
            "member_id": member.member_id,
            "full_name": member.full_name,
            "phone": member.phone,
            "member_type": member.member_type,
            "status": member.status,
            "id": member.id,
        })
        
    return JsonResponse({
        "members": member_data
    })
    
def search_book(request):
    query = request.GET.get("q", "").strip()
    
    if not query:
        return JsonResponse({"books": []})
    
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(isbn__icontains=query)
    )[:10]
    
    book_data = []
    
    for book in books:
        book_data.append({
            "isbn": book.isbn,
            "title": book.title,
            "category": book.category,
            "author": book.author,
            "available_copies": book.available_copies,
            "id": book.id,
        })
        
    return JsonResponse({
        "books": book_data
    })