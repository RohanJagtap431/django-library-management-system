from django.shortcuts import render, get_object_or_404, redirect
from .models import Member
from django.core.paginator import Paginator
from .models import Member, MEMBER_TYPE_CHOICES, GENDER_CHOICES, STATUS_CHOICES, STATE_CHOICES
from django.db.models import Q
from datetime import datetime, date
from django.contrib import messages
from transactions.models import Transaction
from django.utils import timezone
from notifications.models import Notification
from settings_app.models import NotificationSettings
from django.contrib.auth.decorators import login_required
from settings_app.models import EmailSettings
from email_management.models import EmailTemplate
from django.core.mail import send_mail
from django.conf import settings
from email_management.models import EmailHistory

FINE_PER_DAY = 10
@login_required(login_url="login")
def members_list(request):
    members = Member.objects.all().order_by("-join_date")
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
        
    paginator = Paginator(members, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    current_page = page_obj.number
    total_pages = paginator.num_pages

    start = max(current_page - 2, 1)
    end = min(current_page + 2, total_pages)

    page_range = range(start, end + 1)
    
    return render(request, 'members/member_list.html', {
        'page_obj': page_obj,
         "page_range": page_range,
        'categories': MEMBER_TYPE_CHOICES,
        'search': search,
        'category': category,
        'status': status,
        "query_params": query_params.urlencode(),
    })

@login_required(login_url="login")
def member_detail(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    total_issued = Transaction.objects.filter(
        member_id=member_id
        ).count()
    
    total_books_returned = Transaction.objects.filter(
        member_id=member_id,
        status="returned"
    ).count()
    
    

    today = timezone.localdate()

    overdue_count = Transaction.objects.filter(
        member_id=member_id,
        status="issued",
        due_date__lt=today
    ).count()
    
    today = date.today()

    age = (
        today.year
        - member.date_of_birth.year
        - (
            (today.month, today.day)
            < (member.date_of_birth.month, member.date_of_birth.day)
        )
    )
    
    
    today = timezone.localdate()

    pending_fine = 0
    collected_fine = 0

    transactions = Transaction.objects.filter(member=member)

    for transaction in transactions:
        if transaction.status == "issued":
            if today > transaction.due_date:
                pending_fine += (today - transaction.due_date).days * FINE_PER_DAY
        else:
            collected_fine += transaction.fine

    total_fine = pending_fine + collected_fine
            
    
    
    
    return render(request, 'members/member_details.html', {
        "member": member,
        "age": age,
        "total_issued": total_issued,
        "total_books_returned": total_books_returned,
        "overdue_count": overdue_count,
        "pending_fines": pending_fine,
        "total_fine": total_fine,
    })
    
@login_required(login_url="login")
def member_edit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        date_of_birth = request.POST.get("date_of_birth")
        dob = None
        gender = request.POST.get("gender")
        member_type = request.POST.get("member_type")
        status = request.POST.get("status")
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state")
        pincode = request.POST.get("pincode", "").strip()
        
        errors = {}
        
        if not full_name:
            errors["full_name"] = "Full Name is required."
            
        if not email:
            errors["email"] = "Email is required."
            
        if not phone:
            errors["phone"] = "Phone Number is required."
            
        if not address:
            errors["address"] = "Address is required."
            
        if not gender:
            errors["gender"] = "Gender is required."
            
        if not member_type:
            errors["member_type"] = "Member Type is required."
            
        if not status:
            errors["status"] = "Status is required."
            
        if not city:
            errors["city"] = "City is required."
            
        if not state:
            errors["state"] = "State is required."
            
        if not pincode:
            errors["pincode"] = "Pincode is required."
            
        if errors:
            for error in errors.values():
                messages.error(request, error)
                
            return render(request, "members/edit_member.html", {
                "member": member,
                "errors": errors,
                "member_choices": MEMBER_TYPE_CHOICES,
                "status_choices": STATUS_CHOICES,
                "gender_choices": GENDER_CHOICES,
                "state_choices": STATE_CHOICES,
            })
        
        
        
        if Member.objects.exclude(id=member.id).filter(email=email).exists():
            errors["email"] = "Email already exists."
            
        
        if date_of_birth:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            
            if dob > date.today():
                errors["date_of_birth"] = "Birth Date cannot be in the future."
                
        
        if not phone.isdigit() or len(phone) != 10:
            errors["phone"] = "Please enter a valid 10-digit phone number."
           
            
        if not pincode.isdigit() or len(pincode) != 6:
            errors["pincode"] = "Please enter a valid 6-digit Pincode."
        
        if errors:
            for error in errors.values():
                messages.error(request, error)
                
            return render(request, "members/edit_member.html", {
                "member": member,
                "errors": errors,
                "member_choices": MEMBER_TYPE_CHOICES,
                "status_choices": STATUS_CHOICES,
                "gender_choices": GENDER_CHOICES,
                "state_choices": STATE_CHOICES,
            })
            
        if status == "inactive":
            has_issued_books = Transaction.objects.filter(
                member=member,
                status="issued"
            ).exists()

            if has_issued_books:
                messages.error(
                    request,
                    "This member has issued books. Please return all issued books before marking the member as inactive."
                )

                return render(request, "members/edit_member.html", {
                    "member": member,
                    "errors": errors,
                    "member_choices": MEMBER_TYPE_CHOICES,
                    "status_choices": STATUS_CHOICES,
                    "gender_choices": GENDER_CHOICES,
                    "state_choices": STATE_CHOICES,
                })
            
        
            
        member.full_name = full_name
        member.email = email
        member.phone = phone
        member.address = address
        member.date_of_birth = dob if date_of_birth else None
        member.gender =gender
        member.member_type = member_type
        member.status = status
        member.city = city
        member.state = state
        member.pincode = pincode
        
        profile_photo = request.FILES.get("profile_photo")
        if profile_photo:
            if member.profile_photo:
                member.profile_photo.delete(save=False)
            member.profile_photo = profile_photo
            
        member.save()
        messages.success(request, "Member updated successfully.")
        return redirect("members_list")
    return render(request, "members/edit_member.html", {
        "member": member,
        "member_choices": MEMBER_TYPE_CHOICES,
        "status_choices": STATUS_CHOICES,
        "gender_choices": GENDER_CHOICES,
        "state_choices": STATE_CHOICES,
    })


@login_required(login_url="login")
def member_add(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        date_of_birth = request.POST.get("date_of_birth")
        dob = None
        gender = request.POST.get("gender")
        member_type = request.POST.get("member_type")
        status = request.POST.get("status")
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state")
        pincode = request.POST.get("pincode", "").strip()
        profile_photo = request.FILES.get("profile_photo")
        
        errors = {}
        
        if not full_name:
            errors["full_name"] = "Full Name is required."
            
        if not email:
            errors["email"] = "Email is required."
            
        if not phone:
            errors["phone"] = "Phone Number is required."
            
        if not address:
            errors["address"] = "Address is required."
            
        if not gender:
            errors["gender"] = "Gender is required."
            
        if not member_type:
            errors["member_type"] = "Member Type is required."
            
        if not status:
            errors["status"] = "Status is required."
            
        if not city:
            errors["city"] = "City is required."
            
        if not state:
            errors["state"] = "State is required."
            
        if not pincode:
            errors["pincode"] = "Pincode is required."
            
        if errors:
            for error in errors.values():
                messages.error(request, error)
                
            return render(request, "members/add_member.html", {
                "errors": errors,
                "member_choices": MEMBER_TYPE_CHOICES,
                "status_choices": STATUS_CHOICES,
                "gender_choices": GENDER_CHOICES,
                "state_choices": STATE_CHOICES,
            })
        
    
        
        if Member.objects.filter(email=email).exists():
            errors["email"] = "Email already exists."
            
        
        if date_of_birth:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
            
            if dob > date.today():
                errors["date_of_birth"] = "Birth Date cannot be in the future."
            
                
        if not phone.isdigit() or len(phone) != 10:
            errors["phone"] = "Please enter a valid 10-digit phone number."
            
            
        if not pincode.isdigit() or len(pincode) != 6:
            errors["pincode"] = "Please enter a valid 6-digit Pincode."
            
        if errors:
            for error in errors.values():
                messages.error(request, error)
                
            return render(request, "members/add_member.html", {
                "errors": errors,
                "member_choices": MEMBER_TYPE_CHOICES,
                "status_choices": STATUS_CHOICES,
                "gender_choices": GENDER_CHOICES,
                "state_choices": STATE_CHOICES,
            })
            
        member = Member.objects.create(
            full_name = full_name,
            email =  email,
            phone = phone,
            address =address,
            date_of_birth = dob if date_of_birth else None,
            gender = gender,
            member_type = member_type,
            status = status,
            city = city,
            state = state,
            pincode =pincode,
            profile_photo = profile_photo
        )
        
        email_settings = EmailSettings.objects.first()

        if email_settings and email_settings.welcome_email:

            welcome_template = EmailTemplate.objects.get(
                email_type="welcome"
            )

            subject = welcome_template.subject
            
   
            
            message = welcome_template.message
            message = message.replace("{{ full_name }}", member.full_name if member else "")
            message = message.replace("{{ member_email }}", member.email if member else "")
            message = message.replace("{{ join_date }}", member.join_date.strftime("%d-%m-%Y") if member and member.join_date else "")



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
                    email_type="Welcome",
                    status="Sent",
                )

            except Exception as e:

                EmailHistory.objects.create(
                    member=member,
                    recipient=member.email,
                    subject=subject,
                    message=message,
                    email_type="Welcome",
                    status="Failed",
                )

                messages.warning(
                    request,
                    f"Member added successfully, but email could not be sent: {e}"
                )
            
            
        message=f'"{full_name}" has been successfully registered as a new library member.'
        
        
        notification_settings = NotificationSettings.objects.first()
        
        if notification_settings.new_member_alert:
            Notification.objects.create(
                title="New Member Registered",
                message=message,
                notification_type="new_member",
            )
        
        messages.success(request, "Member added successfully.")
        return redirect("members_list")

    return render(request, "members/add_member.html", {
        "member_choices": MEMBER_TYPE_CHOICES,
        "status_choices": STATUS_CHOICES,
        "gender_choices": GENDER_CHOICES,
        "state_choices": STATE_CHOICES,
    })


