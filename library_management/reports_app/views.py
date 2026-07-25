from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from books.models import Book
from django.db.models import Sum
from django.utils import timezone
from transactions.models import Transaction
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

    # ------------------ Logo ------------------

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

    # ------------------ Heading ------------------

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

    # ------------------ Table ------------------

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

    # ------------------ Summary ------------------

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

    # ------------------ Footer ------------------

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