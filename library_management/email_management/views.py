from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from members.models import Member
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from datetime import date
from .models import EmailHistory, EmailTemplate
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import EmailTemplateForm
EMAIL_TYPES = EmailHistory.EMAIL_TYPES

@login_required(login_url="login")
def email_dashboard(request):
    recent_emails = EmailHistory.objects.order_by("-sent_at")[:4]
    total_emails = EmailHistory.objects.filter(status="Sent").count()
    failed_emails = EmailHistory.objects.filter(status="Failed").count()

    today = timezone.localdate()

    start = timezone.make_aware(
        datetime.combine(today, datetime.min.time())
    )
    end = start + timedelta(days=1)

    emails_today = EmailHistory.objects.filter(
        status="Sent",
        sent_at__gte=start,
        sent_at__lt=end,
    ).count()
        
    context = {
        "recent_emails": recent_emails,
        "total_emails": total_emails,
        "emails_today": emails_today,
        "failed_emails": failed_emails,
    }
    
    return render(request, "email_management/email_dashboard.html", context)


@login_required(login_url="login")
def compose_email(request):

    members = Member.objects.filter(status="Active")

    if request.method == "POST":

        recipient_type = request.POST.get("recipient_type")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if recipient_type == "member":

            member_id = request.POST.get("member")

            if not member_id:
                messages.error(request, "Please select a member.")
                return redirect("compose_email")

            member = Member.objects.get(member_id=member_id)

            placeholders = {
                "{{ full_name }}": member.full_name if member else "",
                "{{ member_id }}": str(member.member_id),
                "{{ member_email }}": member.email if member else "",
                "{{ join_date }}": member.join_date.strftime("%d-%m-%Y") if member and member.join_date else "",
                "{{ phone }}": member.phone,
                "{{ status }}": member.status,
                "{{ today }}": date.today().strftime("%d-%m-%Y"),
            }

            email_message = message

            for key, value in placeholders.items():
                email_message = email_message.replace(key, value)

            email = EmailMultiAlternatives(
                subject=subject,
                body=email_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[member.email],
            )

            email.attach_alternative(email_message, "text/html")

            try:
                email.send()

                EmailHistory.objects.create(
                    member=member,
                    recipient=member.email,
                    subject=subject,
                    message=email_message,
                    email_type="Compose",
                    status="Sent",
                )

                messages.success(request, "Email sent successfully.")

            except Exception:
                EmailHistory.objects.create(
                    member=member,
                    recipient=member.email,
                    subject=subject,
                    message=email_message,
                    email_type="Compose",
                    status="Failed",
                )

                messages.error(request, "Failed to send email.")

            return redirect("compose_email")


        elif recipient_type == "all":

            members = Member.objects.filter(status="Active")

            for member in members:

                placeholders = {
                    "{{ full_name }}": member.full_name,
                    "{{ member_id }}": str(member.member_id),
                    "{{ member_email }}": member.email,
                    "{{ phone }}": member.phone,
                    "{{ status }}": member.status,
                    "{{ today }}": date.today().strftime("%d-%m-%Y"),
                    "{{ join_date }}": member.join_date.strftime("%d-%m-%Y") if member and member.join_date else "",
                    
                }

                email_message = message

                for key, value in placeholders.items():
                    email_message = email_message.replace(key, value)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=email_message,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[member.email],
                )

                email.attach_alternative(email_message, "text/html")

                try:
                    email.send()

                    EmailHistory.objects.create(
                        member=member,
                        recipient=member.email,
                        subject=subject,
                        message=email_message,
                        email_type="Compose",
                        status="Sent",
                    )

                except Exception:

                    EmailHistory.objects.create(
                        member=member,
                        recipient=member.email,
                        subject=subject,
                        message=email_message,
                        email_type="Compose",
                        status="Failed",
                    )

            messages.success(
                request,
                "Email sent successfully to all active members."
            )

            return redirect("compose_email")
    
    context = {
        "members": members,
    }

    return render(
        request,
        "email_management/compose_email.html",
        context,
    )
  
@login_required(login_url="login")  
def clear_all_history(request):
    if request.method == "POST":
        EmailHistory.objects.all().delete()
        
        messages.success(
            request, "Clear all email history successfully."
        )
        return redirect('email_history')
    return render(request, 'email_management/clear_all_email_history.html')    


@login_required(login_url="login")
def delete_email_history(request, id):

    email = get_object_or_404(EmailHistory, id=id)

    if request.method == "POST":
        email.delete()
        messages.success(request, "Email history deleted successfully.")
        return redirect("email_history")

    context = {
        "email": email,
    }

    return render(
        request,
        "email_management/delete_email_history.html",
        context,
    )

@login_required(login_url="login")
def email_history(request):

    emails = EmailHistory.objects.select_related("member").order_by("-sent_at")

    
    search = request.GET.get("search", "").strip()

    if search:
        emails = emails.filter(
            Q(recipient__icontains=search) |
            Q(subject__icontains=search) |
            Q(member__full_name__icontains=search) |  
            Q(status__icontains=search) |
            Q(email_type__icontains=search)
        )

   
    selected_email_type = request.GET.get("email_type", "")

    if selected_email_type:
        emails = emails.filter(email_type=selected_email_type)

   
    selected_status = request.GET.get("status", "")

    if selected_status:
        emails = emails.filter(status=selected_status)
        
    today = request.GET.get("today")

    if today:
        current_date = timezone.localdate()

        start = timezone.make_aware(
            datetime.combine(current_date, datetime.min.time())
        )

        end = start + timedelta(days=1)

        emails = emails.filter(
            status="Sent",
            sent_at__gte=start,
            sent_at__lt=end,
        )

   
    paginator = Paginator(emails, 7)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start = max(current_page - 2, 1)
    end = min(current_page + 2, total_pages)

    page_range = range(start, end + 1)

    
    query_params = request.GET.copy()
    query_params.pop("page", None)

    context = {
        "page_obj": page_obj,
         "page_range": page_range,
        "email_type_choices": EMAIL_TYPES,
        "selected_email_type": selected_email_type,

        "selected_status": selected_status,

        "search": search,

        "query_params": query_params.urlencode(),
    }

    return render(
        request,
        "email_management/email_history.html",
        context,
    )
    

@login_required(login_url="login")
def view_email_history(request, id):

    email = get_object_or_404(
        EmailHistory.objects.select_related("member"),
        id=id
    )

    context = {
        "email": email,
    }

    return render(
        request,
        "email_management/view_email_history.html",
        context,
    )
    
@login_required(login_url="login")
def email_templates(request):
    templates = EmailTemplate.objects.all().order_by("id")
    
    
    context = {
        "templates": templates,
    }
    
    return render(request, "email_management/email_templates.html", context)

@login_required(login_url="login")
def preview_email(request, email_type):

    template = get_object_or_404(
        EmailTemplate,
        email_type=email_type
    )

    subject = template.subject
    message = template.message

    placeholders = {
        "{{ full_name }}": "Rohan Jagtap",
        "{{ member_email }}": "rohanjagtap@example.com",
        "{{ join_date }}": "22-07-2026",
        "{{ title }}": "Python Programming",
        "{{ issue_date }}": "20-07-2026",
        "{{ due_date }}": "27-07-2026",
        "{{ return_date }}": "25-07-2026",
        "{{ overdue_days }}": "3",
        "{{ fine }}": "30",
    }

    for key, value in placeholders.items():
        subject = subject.replace(key, value)
        message = message.replace(key, value)

    return render(
        request,
        "email_management/preview_email.html",
        {
            "template": template,
            "subject": subject,
            "message": message,
        }
    )

@login_required(login_url="login")
def edit_email_template(request, id):

    template = get_object_or_404(
        EmailTemplate,
        id=id
    )

    if request.method == "POST":
        form = EmailTemplateForm(
            request.POST,
            instance=template
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Email template updated successfully."
            )

            return redirect("email_templates")

    else:
        form = EmailTemplateForm(instance=template)

    context = {
        "form": form,
        "template": template,
    }

    return render(
        request,
        "email_management/edit_email_template.html",
        context,
    )