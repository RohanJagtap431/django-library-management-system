from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from books.models import Book
from django.db.models import Sum
from django.utils import timezone
from transactions.models import Transaction, STATUS_CHOICES
from django.core.paginator import Paginator
from django.db.models import Q
import csv
import os
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image,
)
from reportlab.pdfgen import canvas
from books.models import Book, CATEGORY_CHOICES
from members.models import Member, MEMBER_TYPE_CHOICES
from settings_app.models import IssueSettings



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
    search = request.GET.get("search", "")
    
    if search:
        transactions = transactions.filter(
            Q(issue_id__icontains=search) | Q(book__title__icontains=search) | Q(book__isbn__icontains=search) | Q(member__full_name__icontains=search) | Q(member__member_id__icontains=search)
        )

    total_fine = transactions.aggregate(
        total=Sum("fine")
    )["total"] or 0
    
    total_transactions = Transaction.objects.filter(
        status="returned",
        fine__gt=0
    ).count()
    
    
    members_with_fine = (
        Transaction.objects.filter(
            status="returned",
            fine__gt=0
        )
        .values("member")
        .distinct()
        .count()
    )
    
    for transaction in transactions:
        if transaction.return_date and transaction.return_date > transaction.due_date:
            transaction.late_days = (
                transaction.return_date - transaction.due_date
            ).days
        else:
            transaction.late_days = 0
    
    query_params = request.GET.copy()
    query_params.pop("page", None)
        
    paginator = Paginator(transactions, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start = max(current_page - 2, 1)
    end = min(current_page + 2, total_pages)

    page_range = range(start, end + 1)

    context = {
        'page_obj': page_obj,
        "page_range": page_range,
        "transactions": transactions,
        "total_fine": total_fine,
        "query_params": query_params.urlencode(),
        "total_transactions": total_transactions,
        "members_with_fine": members_with_fine,
    }

    return render(
        request,
        "reports/fine_report.html",
        context,
    )

@login_required(login_url="login")
def export_fine_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="fine_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Transaction ID",
        "Member Name",
        "Book Title",
        "Due Date",
        "Return Date",
        "Late Days",
        "Fine"
    ])

    fines = Transaction.objects.filter(fine__gt=0)
    
    for fine in fines:
        if fine.return_date and fine.return_date > fine.due_date:
            fine.late_days = (
                fine.return_date - fine.due_date
            ).days
        else:
            fine.late_days = 0

    for fine in fines:
        writer.writerow([
            fine.issue_id,
            fine.member.full_name,
            fine.book.title,
            fine.due_date.strftime("%d-%m-%Y"),
            fine.return_date.strftime("%d-%m-%Y") if fine.return_date else "-",
            fine.late_days,
            fine.fine,
        ])

    return response


def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()

    canvas.setFont("Helvetica", 9)

    canvas.drawRightString(
        810,
        20,
        f"Page {page_num}"
    )
    

@login_required(login_url="login")
def export_fine_pdf(request):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Fine_Report.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    heading_style.alignment = TA_CENTER

    normal_style = styles["Normal"]

    elements = []

    

    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "images",
        "logo.png"
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = "CENTER"
        elements.append(logo)

    

    elements.append(
        Paragraph(
            "<b>LIBRARY MANAGEMENT SYSTEM</b>",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "<b>Fine Report</b>",
            heading_style
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Generated On :</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
            normal_style
        )
    )

    elements.append(Spacer(1, 15))

    

    data = [[
        "Transaction ID",
        "Member",
        "Book",
        "Due Date",
        "Return Date",
        "Fine (Rs)"
    ]]

    transactions = Transaction.objects.filter(fine__gt=0)

    total_fine = 0

    for t in transactions:

        total_fine += t.fine

        data.append([
            str(t.issue_id),
            t.member.full_name,
            t.book.title,
            t.due_date.strftime("%d-%m-%Y"),
            t.return_date.strftime("%d-%m-%Y") if t.return_date else "-",
            f"{t.fine}"
        ])

    table = Table(
        data,
        colWidths=[
            1.2 * inch,
            2.7 * inch,
            3.8 * inch,
            1.2 * inch,
            1.2 * inch,
            0.9 * inch,
        ],
        repeatRows=1,
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 11),

        ("BOTTOMPADDING", (0,0), (-1,0), 10),

        ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),

        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

        ("FONTSIZE", (0,1), (-1,-1), 9),

        ("ROWBACKGROUNDS", (0,1), (-1,-1),
            [
                colors.white,
                colors.HexColor("#f5f5f5")
            ]
        ),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 20))

    

    elements.append(
        Paragraph(
            f"<b>Total Records :</b> {transactions.count()}",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            f"<b>Total Fine :</b> Rs. {total_fine}",
            normal_style
        )
    )

    elements.append(Spacer(1, 20))

    

    elements.append(
        Paragraph(
            "<font color='grey'>Generated by Library Management System</font>",
            normal_style
        )
    )

    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return response

@login_required(login_url="login")
def book_report(request):
    books = Book.objects.all().order_by("-created_at")
    total_book = Book.objects.count()
    total_books = Book.objects.aggregate(
        total=Sum("total_copies")
    )["total"] or 0
    
    available_books = Book.objects.aggregate(
        total=Sum("available_copies")
    )["total"] or 0
    search = request.GET.get("search", "")
    category = request.GET.get("category")
    status = request.GET.get("status")
    if search:
        books = books.filter(
            Q(title__icontains=search) | Q(author__icontains=search) |  Q(isbn__icontains=search) |  Q(category__icontains=search) |  Q(publisher__icontains=search) |  Q(publication_year__icontains=search) | Q(shelf_location__icontains=search)
        )
    
    if category:
        books = books.filter(category = category)
        
    if status:
        if status == "available":
            books = books.filter(available_copies__gt=0)
        elif status == "out_of_stock":
            books = books.filter(available_copies=0)
    
    query_params = request.GET.copy()
    query_params.pop("page", None)
        
    paginator = Paginator(books, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start = max(current_page - 2, 1)
    end = min(current_page + 2, total_pages)

    page_range = range(start, end + 1)
    
    return render(request, 'reports/book_report.html', {
        'page_obj': page_obj,
        "page_range": page_range,
        'categories': CATEGORY_CHOICES,
        'search': search,
        'category': category,
        'status': status,
        "query_params": query_params.urlencode(),
        "total_book": total_book,
        "total_books": total_books,
        "available_books": available_books,
    })
    
    
@login_required(login_url="login")
def export_book_csv(request):

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="book_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Book ID",
        "Title",
        "Author",
        "Category",
        "ISBN",
        "Publisher",
        "Publication Year",
        "Total Copies",
        "Available Copies",
        "Shelf Location",
        "Status",
    ])

    books = Book.objects.all()

    for book in books:

        status = (
            "Available"
            if book.available_copies > 0
            else "Unavailable"
        )

        writer.writerow([
            book.id,
            book.title,
            book.author,
            book.category,
            book.isbn,
            book.publisher,
            book.publication_year,
            book.total_copies,
            book.available_copies,
            book.shelf_location,
            status,
        ])

    return response

@login_required(login_url="login")
def export_book_pdf(request):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Book_Report.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    heading_style.alignment = TA_CENTER

    normal_style = styles["BodyText"]
    normal_style.fontSize = 8
    normal_style.leading = 10

    elements = []

    

    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "images",
        "logo.png"
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = "CENTER"
        elements.append(logo)

    

    elements.append(
        Paragraph(
            "<b>LIBRARY MANAGEMENT SYSTEM</b>",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "<b>Book Report</b>",
            heading_style
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Generated On :</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    books = Book.objects.all()

    data = [[
        "ISBN",
        "Title",
        "Author",
        "Category",
        "Year",
        "Total",
        "Available",
        "Status"
    ]]

    total_copies = 0
    available_copies = 0

    for book in books:

        total_copies += book.total_copies
        available_copies += book.available_copies

        status = (
            "Available"
            if book.available_copies > 0
            else "Unavailable"
        )

        data.append([
            str(book.isbn),
            Paragraph(book.title, normal_style),
            Paragraph(book.author, normal_style),
            Paragraph(book.category, normal_style),
            str(book.publication_year),
            str(book.total_copies),
            str(book.available_copies),
            status,
        ])
        
        table = Table(
        data,
        colWidths=[
            1.0 * inch,   
            2.8 * inch,   
            2.0 * inch,   
            1.3 * inch,   
            0.8 * inch,   
            0.8 * inch,   
            1.0 * inch,   
            1.1 * inch,   
        ],
        repeatRows=1,
    )

    table.setStyle(TableStyle([

        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

        # Body
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),

        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),

        ("ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [
                colors.white,
                colors.HexColor("#f5f5f5")
            ]
        ),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 18))

    
    elements.append(
        Paragraph(
            f"<b>Total Book Titles :</b> {books.count()}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Total Copies :</b> {total_copies}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Available Copies :</b> {available_copies}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    

    elements.append(
        Paragraph(
            "<font color='grey'>Generated by Library Management System</font>",
            styles["Normal"]
        )
    )

    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return response


@login_required(login_url="login")
def member_report(request):
    members = Member.objects.all().order_by("member_id")
    total_members = Member.objects.all().count()
    active_members = Member.objects.filter(status="active").count()
    inactive_members = Member.objects.filter(status="inactive").count()
    search = request.GET.get("search", "")
    category = request.GET.get("category")
    status = request.GET.get("status")
    if search:
        members = members.filter(
            Q(full_name__icontains=search) | Q(email__icontains=search) |  Q(phone__icontains=search) |  Q(member_id__icontains=search) |  Q(gender__icontains=search) |  Q(address__icontains=search) | Q(city__icontains=search) | Q(state__icontains=search) | Q(pincode__icontains=search)
        )
    
    if category:
        members = members.filter(member_type = category)
        
    if status:
        members = members.filter(status=status)
    
    query_params = request.GET.copy()
    query_params.pop("page", None)
        
    paginator = Paginator(members, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start = max(current_page - 2, 1)
    end = min(current_page + 2, total_pages)

    page_range = range(start, end + 1)
    
    return render(request, 'reports/member_report.html', {
        'page_obj': page_obj,
        "page_range": page_range,
        'categories': MEMBER_TYPE_CHOICES,
        'search': search,
        'category': category,
        'status': status,
        "query_params": query_params.urlencode(),
        "total_members": total_members,
        "active_members": active_members,
        "inactive_members": inactive_members,
    })

@login_required(login_url="login")
def export_member_csv(request):

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="member_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Member ID",
        "Full Name",
        "Email",
        "Phone",
        "Gender",
        "Member Type",
        "Status",
        "Date of Birth",
        "City",
        "State",
        "Pincode",
        "Join Date",
    ])

    members = Member.objects.all()

    for member in members:

        writer.writerow([
            member.member_id,
            member.full_name,
            member.email,
            member.phone,
            member.gender,
            member.member_type,
            member.status.title(),
            member.date_of_birth.strftime("%d-%m-%Y") if member.date_of_birth else "-",
            member.city,
            member.state,
            member.pincode,
            member.join_date.strftime("%d-%m-%Y"),
        ])

    return response

@login_required(login_url="login")
def export_member_pdf(request):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Member_Report.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    heading_style.alignment = TA_CENTER

    normal_style = styles["BodyText"]
    normal_style.fontSize = 8
    normal_style.leading = 10

    elements = []

    

    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "images",
        "logo.png"
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = "CENTER"
        elements.append(logo)

    

    elements.append(
        Paragraph(
            "<b>LIBRARY MANAGEMENT SYSTEM</b>",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "<b>Member Report</b>",
            heading_style
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Generated On :</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    members = Member.objects.all()

    data = [[
        "Member ID",
        "Full Name",
        "Email",
        "Phone",
        "Gender",
        "Type",
        "Status",
        "Join Date"
    ]]

    active_members = 0
    inactive_members = 0

    for member in members:

        if member.status.lower() == "active":
            active_members += 1
        else:
            inactive_members += 1

        data.append([
            member.member_id,
            Paragraph(member.full_name, normal_style),
            Paragraph(member.email, normal_style),
            member.phone,
            member.gender,
            member.member_type,
            member.status.title(),
            member.join_date.strftime("%d-%m-%Y"),
        ])

    table = Table(
        data,
        colWidths=[
            1.2 * inch,
            2.0 * inch,
            2.5 * inch,
            1.2 * inch,
            0.9 * inch,
            1.0 * inch,
            1.0 * inch,
            1.2 * inch,
        ],
        repeatRows=1,
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),

        ("BOTTOMPADDING", (0,0), (-1,0), 8),

        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,1), (-1,-1), 8),

        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),

        ("ROWBACKGROUNDS",
            (0,1),
            (-1,-1),
            [
                colors.white,
                colors.HexColor("#f5f5f5")
            ]
        ),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 18))

    

    elements.append(
        Paragraph(
            f"<b>Total Members :</b> {members.count()}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Active Members :</b> {active_members}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Inactive Members :</b> {inactive_members}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    

    elements.append(
        Paragraph(
            "<font color='grey'>Generated by Library Management System</font>",
            styles["Normal"]
        )
    )

    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return response

@login_required(login_url="login")
def issue_return_report(request):
    transactions = Transaction.objects.all().order_by("created_at")
    total_issued = Transaction.objects.filter(status="issued").count()
    total_returned = Transaction.objects.filter(status="returned").count()
    today = timezone.localdate()
    overdue_books = Transaction.objects.filter(
        due_date__lt=today,
        status="issued"
    ).count()
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
        
    paginator = Paginator(transactions, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start = max(current_page - 2, 1)
    end = min(current_page + 2, total_pages)

    page_range = range(start, end + 1)
    
    return render(request, 'reports/issue_return_report.html', {
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
        "total_issued": total_issued,
        "total_returned": total_returned,
        "overdue_books": overdue_books,
    })
    

@login_required(login_url="login")
def export_issue_return_csv(request):

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="issue_return_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Transaction ID",
        "Book Title",
        "Member Name",
        "Issue Date",
        "Due Date",
        "Return Date",
        "Status",
        "Fine (Rs.)",
    ])

    transactions = Transaction.objects.all()

    for transaction in transactions:

        writer.writerow([
            transaction.issue_id,
            transaction.book.title,
            transaction.member.full_name,
            transaction.issue_date.strftime("%d-%m-%Y"),
            transaction.due_date.strftime("%d-%m-%Y"),
            transaction.return_date.strftime("%d-%m-%Y") if transaction.return_date else "-",
            transaction.status.title(),
            transaction.fine,
        ])

    return response


@login_required(login_url="login")
def export_issue_return_pdf(request):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Issue_Return_Report.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    heading_style.alignment = TA_CENTER

    normal_style = styles["BodyText"]
    normal_style.fontSize = 8
    normal_style.leading = 10

    elements = []

    

    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "images",
        "logo.png"
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=70, height=70)
        logo.hAlign = "CENTER"
        elements.append(logo)

    

    elements.append(
        Paragraph(
            "<b>LIBRARY MANAGEMENT SYSTEM</b>",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "<b>Issue & Return Report</b>",
            heading_style
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Generated On :</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    transactions = Transaction.objects.all()

    data = [[
        "Transaction ID",
        "Book",
        "Member",
        "Issue Date",
        "Due Date",
        "Return Date",
        "Status",
        "Fine (Rs.)"
    ]]

    issued_count = 0
    returned_count = 0
    total_fine = 0

    for transaction in transactions:

        if transaction.status.lower() == "issued":
            issued_count += 1
        elif transaction.status.lower() == "returned":
            returned_count += 1

        total_fine += transaction.fine

        data.append([
            transaction.issue_id,
            Paragraph(transaction.book.title, normal_style),
            Paragraph(transaction.member.full_name, normal_style),
            transaction.issue_date.strftime("%d-%m-%Y"),
            transaction.due_date.strftime("%d-%m-%Y"),
            transaction.return_date.strftime("%d-%m-%Y") if transaction.return_date else "-",
            transaction.status.title(),
            f"Rs. {transaction.fine}",
        ])

    table = Table(
        data,
        colWidths=[
            1.2 * inch,
            2.8 * inch,
            2.2 * inch,
            1.1 * inch,
            1.1 * inch,
            1.1 * inch,
            1.0 * inch,
            0.9 * inch,
        ],
        repeatRows=1,
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),

        ("BOTTOMPADDING", (0,0), (-1,0), 8),

        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,1), (-1,-1), 8),

        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),

        ("ROWBACKGROUNDS",
            (0,1),
            (-1,-1),
            [
                colors.white,
                colors.HexColor("#f5f5f5")
            ]
        ),

    ]))

    elements.append(table)

    elements.append(Spacer(1, 18))

    

    elements.append(
        Paragraph(
            f"<b>Total Transactions :</b> {transactions.count()}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Issued Books :</b> {issued_count}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Returned Books :</b> {returned_count}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>Total Fine Collected :</b> Rs. {total_fine}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    

    elements.append(
        Paragraph(
            "<font color='grey'>Generated by Library Management System</font>",
            styles["Normal"]
        )
    )

    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return response




