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
from settings_app.models import IssueSettings
from notifications.models import Notification
from settings_app.models import BookSettings, NotificationSettings
from django.contrib.auth.decorators import login_required
from settings_app.models import EmailSettings
from email_management.models import EmailTemplate
from django.core.mail import send_mail
from django.conf import settings
from email_management.models import EmailHistory


@login_required(login_url="login")
def transaction_list(request):
    
    transactions = Transaction.objects.all().order_by("-created_at")
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
        
    today = timezone.localdate()

    if status:
        if status == "issued":
            transactions = transactions.filter(
                status="issued"
            )

        elif status == "returned":
            transactions = transactions.filter(
                status="returned"
            )

        elif status == "overdue":
            transactions = transactions.filter(
                status="issued",
                due_date__lt=today
            )
            
    if member:
        transactions = transactions.filter(member_id=member)
        
    if book:
        transactions = transactions.filter(book_id=book)
        
    
    today = timezone.localdate()

    for transaction in transactions:
        
        issue_settings = IssueSettings.objects.get(
            member_type=transaction.member.member_type
        )
        
        
        if transaction.status == "issued":
            if today > transaction.due_date:
                transaction.current_fine = (today - transaction.due_date).days * issue_settings.fine_per_day
            else:
                transaction.current_fine = 0
        else:
            transaction.current_fine = transaction.fine

    query_params = request.GET.copy()
    query_params.pop("page", None)
        
    paginator = Paginator(transactions, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start = max(current_page - 2, 1)
    end = min(current_page + 2, total_pages)

    page_range = range(start, end + 1)
    
    return render(request, 'transactions/transaction_list.html', {
        'page_obj': page_obj,
        "page_range": page_range,
        'search': search,
        "status": status,
        "all_status": STATUS_CHOICES,
        "all_members": all_members,
        "member": member,
        "all_books": all_books,
        "book": book,
        "today": timezone.localdate(),
        "query_params": query_params.urlencode(),
    })

@login_required(login_url="login")
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
            
        if member_error:
            messages.error(request, member_error)
            
        if book_error:
            messages.error(request, book_error)
            
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
        
        issue_settings = IssueSettings.objects.get(
            member_type=member.member_type
        )
        
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
            
        if issued_books >= issue_settings.max_books:
            member_error = (
                f"This member has reached the maximum issue limit "
                f"({issue_settings.max_books} books)."
            )
            
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
        
        
        loan_period = issue_settings.loan_period

        due_date = date.today() + timedelta(days=loan_period)

        transaction = Transaction.objects.create(
            member=member,
            book=book,
            due_date=due_date,
        )

        book.available_copies -= 1
        book.save()
        
        
        email_settings = EmailSettings.objects.first()

        if email_settings and email_settings.book_issue_email:

            issue_template = EmailTemplate.objects.get(
                email_type="book_issue"
            )

            subject = issue_template.subject

            message = issue_template.message
            message = message.replace("{{ full_name }}", member.full_name if member else "")
            message = message.replace("{{ member_email }}", member.email if member else "")
            message = message.replace("{{ join_date }}", member.join_date.strftime("%d-%m-%Y") if member and member.join_date else "")

            message = message.replace("{{ title }}", book.title if book else "")

            message = message.replace("{{ issue_date }}", transaction.issue_date.strftime("%d-%m-%Y") if transaction and transaction.issue_date else "")
            message = message.replace("{{ due_date }}", transaction.due_date.strftime("%d-%m-%Y") if transaction and transaction.due_date else "")
            message = message.replace("{{ return_date }}", transaction.return_date.strftime("%d-%m-%Y") if transaction and transaction.return_date else "")
            
            overdue_days = max(0, (date.today() - transaction.due_date).days)
            
            message = message.replace(
                "{{ overdue_days }}",
                str(overdue_days)
            )
            
            message = message.replace(
                "{{ fine }}",
                str(transaction.fine if transaction.fine else 0)
            )


            try:
                send_mail(
                    subject=subject,
                    message="",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[member.email],
                    html_message=message,
                    fail_silently=False,
                )
                
                EmailHistory.objects.create(
                    member=member,
                    recipient=member.email,
                    subject=subject,
                    message=message,
                    email_type="Book Issue",
                    status="Sent",
                )
                
            except Exception as e:
                
                EmailHistory.objects.create(
                    member=member,
                    recipient=member.email,
                    subject=subject,
                    message=message,
                    email_type="Book Issue",
                    status="Failed",
                )
                
                messages.warning(
                    request,
                    f"Book issued successfully, but email could not be sent: {e}"
                )
        
        notification_settings = NotificationSettings.objects.first()
        
        message=f'"{book.title}" has been issued to "{member.full_name}" successfully.'
        
        if notification_settings.book_issue_alert:
            Notification.objects.create(
                title="Book Issued",
                message=message,
                notification_type="book_issued",
            )
        
        book_settings = BookSettings.objects.first()
        
        if notification_settings.low_stock_alert:
            if book.available_copies == 0:
                message=f'The book "{book.title}" is currently out of stock.'
                
                Notification.objects.create(
                    title="Low Stock Alert",
                    message=message,
                    notification_type="low_stock",
                )
                
            elif book.available_copies <= book_settings.low_stock_alert_limit:
                message=f'"{book.title}" has only "{book.available_copies}" copies remaining in the library.'
                
                Notification.objects.create(
                    title="Low Stock Alert",
                    message=message,
                    notification_type="low_stock",
                )

        messages.success(request, "Book issued successfully.")

        return redirect("issue_book")
    
    context = {
        "members": members,
        "books": books,
        "member_error": member_error,
        "book_error": book_error,
    }

    return render(request, "transactions/issue_book.html", context)

@login_required(login_url="login")
def return_book(request, issue_id):
    transaction = get_object_or_404(
        Transaction,
        issue_id=issue_id
    )
    
    member = transaction.member
    book = transaction.book
    
    
    issue_settings = IssueSettings.objects.get(
        member_type=transaction.member.member_type
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
            fine =late_days * issue_settings.fine_per_day
        else:
            fine = 0
        
        transaction.fine = fine
        
        notification_settings = NotificationSettings.objects.first()
        
        if notification_settings.fine_alert:
            if fine > 0:
                message=f'A fine of ₹{fine} has been applied to {transaction.member.full_name} for the overdue book {transaction.book.title}.'
            
                Notification.objects.create(
                    title="Fine Applied",
                    message=message,
                    notification_type="fine",
                )
        
        transaction.book.available_copies += 1
        
        transaction.book.save()
        transaction.save()
        
        email_settings = EmailSettings.objects.first()

        if email_settings and email_settings.book_return_email:

            issue_template = EmailTemplate.objects.get(
                email_type="book_return"
            )

            subject = issue_template.subject

            message = issue_template.message
            
            message = message.replace("{{ full_name }}", member.full_name if member else "")
            message = message.replace("{{ member_email }}", member.email if member else "")
            message = message.replace("{{ join_date }}", member.join_date.strftime("%d-%m-%Y") if member and member.join_date else "")

            message = message.replace("{{ title }}", book.title if book else "")

            message = message.replace("{{ issue_date }}", transaction.issue_date.strftime("%d-%m-%Y") if transaction and transaction.issue_date else "")
            message = message.replace("{{ due_date }}", transaction.due_date.strftime("%d-%m-%Y") if transaction and transaction.due_date else "")
            message = message.replace("{{ return_date }}", transaction.return_date.strftime("%d-%m-%Y") if transaction and transaction.return_date else "")

            
            overdue_days = max(0, (date.today() - transaction.due_date).days)
                        
            message = message.replace(
                "{{ overdue_days }}",
                str(overdue_days)
            )
            
            message = message.replace(
                "{{ fine }}",
                str(transaction.fine if transaction.fine else 0)
            )

            try:
                send_mail(
                    subject=subject,
                    message="",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[member.email],
                    html_message=message,
                    fail_silently=False,
                )
                
                EmailHistory.objects.create(
                    member=member,
                    recipient=member.email,
                    subject=subject,
                    message=message,
                    email_type="Book Return",
                    status="Sent",
                )
                
            except Exception as e:
                
                EmailHistory.objects.create(
                    member=member,
                    recipient=member.email,
                    subject=subject,
                    message=message,
                    email_type="Book Return",
                    status="Failed",
                )
                
                messages.warning(
                    request,
                    f"Book returned successfully, but email could not be sent: {e}"
                )
        
        message=f'{transaction.member.full_name} has successfully returned {transaction.book.title}.'
        
        notification_settings = NotificationSettings.objects.first()
        
        if notification_settings.book_return_alert:
            Notification.objects.create(
                title="Book Returned",
                message=message,
                notification_type="book_returned",
            )

        messages.success(request, "Book returned successfully.")
        
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
        fine =late_days * issue_settings.fine_per_day
    else:
        fine = 0
    
    context= {
        "transaction": transaction,
        "status": status,
        "return_date": return_date,
        "late_days": late_days,
        "fine": fine,
        "FINE_PER_DAY": issue_settings.fine_per_day,
    }
    
    return render(request, "transactions/return_book.html", context)

@login_required(login_url="login")
def search_member(request):
    query = request.GET.get("q", "").strip()
    
    if not query:
        return JsonResponse({"members": []})
    
    members = Member.objects.filter(
        Q(member_id__icontains=query) | Q(full_name__icontains=query)
    )[:10]
    
    member_data = []

    for member in members:
        
        issue_settings = IssueSettings.objects.get(
            member_type=member.member_type
        )
        
        member_data.append({
            "member_id": member.member_id,
            "full_name": member.full_name,
            "phone": member.phone,
            "member_type": member.member_type,
            "status": member.status,
            "id": member.id,
            "max_books": issue_settings.max_books,
            "loan_period": issue_settings.loan_period,
            "fine_per_day": issue_settings.fine_per_day,
        })
        
    return JsonResponse({
        "members": member_data
    })

@login_required(login_url="login")   
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
    
@login_required(login_url="login")
def transaction_details(request, issue_id):
    transaction = get_object_or_404(Transaction, issue_id=issue_id)
    
    issue_settings = IssueSettings.objects.get(
        member_type=transaction.member.member_type
    )
    
    
    if transaction.status == "issued":
        if transaction.due_date < timezone.localdate():
            status = "Overdue"
        else:
            status = "Issued"

    elif transaction.status == "returned":
        status = "Returned"
        
    else:
        status = "Unknown"
        
    return_date = timezone.localdate()
    
    if transaction.status == "issued":
        if timezone.localdate() > transaction.due_date:
            late_days = (return_date - transaction.due_date).days
        else:
            late_days = 0
    
    elif transaction.status == "returned":
        if transaction.return_date > transaction.due_date:
            late_days = (transaction.return_date - transaction.due_date).days
        else:
            late_days = 0
            
        

    if transaction.status == "issued":
        if late_days > 0:
            fine =late_days * issue_settings.fine_per_day
        else:
            fine = 0
            
    elif transaction.status == "returned":
        fine = transaction.fine
        
    
    
    
        
    context = {
        "transaction":transaction,
        "status": status,
        "return_date": return_date,
        "late_days": late_days,
        "fine": fine,
        
    }
        
        
    
    return render(request, "transactions/transaction_details.html", context)

def send_overdue_email(transaction):
    email_settings = EmailSettings.objects.first()
    
    if not email_settings or not email_settings.overdue_reminder:
        return
    
    overdue_template = EmailTemplate.objects.get(
        email_type="overdue"
    )
    
    
    
    subject = overdue_template.subject
    message = overdue_template.message
    
    
    member = transaction.member
    book = transaction.book

    message = message.replace("{{ full_name }}", member.full_name if member else "")
    message = message.replace("{{ member_email }}", member.email if member else "")
    message = message.replace("{{ join_date }}", member.join_date.strftime("%d-%m-%Y") if member and member.join_date else "")

    message = message.replace("{{ title }}", book.title if book else "")

    message = message.replace("{{ issue_date }}", transaction.issue_date.strftime("%d-%m-%Y") if transaction and transaction.issue_date else "")
    message = message.replace("{{ due_date }}", transaction.due_date.strftime("%d-%m-%Y") if transaction and transaction.due_date else "")
    message = message.replace("{{ return_date }}", transaction.return_date.strftime("%d-%m-%Y") if transaction and transaction.return_date else "")

    overdue_days = max(0, (date.today() - transaction.due_date).days)
    
    issue_settings = IssueSettings.objects.get(
        member_type=transaction.member.member_type
    )
    
    current_fine = overdue_days * issue_settings.fine_per_day
        

    message = message.replace(
        "{{ overdue_days }}",
        str(overdue_days)
    )
    
    message = message.replace(
        "{{ fine }}",
        str(current_fine)
    )
    
    try:
        send_mail(
            subject=subject,
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[member.email],
            html_message=message,
            fail_silently=False,
        )

        EmailHistory.objects.create(
            member=member,
            recipient=member.email,
            subject=subject,
            message=message,
            email_type="Overdue Reminder",
            status="Sent",
        )

    except Exception as e:

        EmailHistory.objects.create(
            member=member,
            recipient=member.email,
            subject=subject,
            message=message,
            email_type="Overdue Reminder",
            status="Failed",
        )

        raise

    transaction.last_reminder_sent = date.today()
    transaction.save()


    
    