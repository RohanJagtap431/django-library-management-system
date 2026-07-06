from django.shortcuts import render, get_object_or_404, redirect
from .models import Member
from django.core.paginator import Paginator
from .models import Member, MEMBER_TYPE_CHOICES, GENDER_CHOICES, STATUS_CHOICES, STATE_CHOICES
from django.db.models import Q
from datetime import datetime, date
from django.contrib import messages


def members_list(request):
    members = Member.objects.all()
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
    
        
    paginator = Paginator(members, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'members/member_list.html', {
        'page_obj': page_obj,
        'categories': MEMBER_TYPE_CHOICES,
        'search': search,
        'category': category,
        'status': status
    })


def member_detail(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    today = date.today()

    age = (
        today.year
        - member.date_of_birth.year
        - (
            (today.month, today.day)
            < (member.date_of_birth.month, member.date_of_birth.day)
        )
    )
    return render(request, 'members/member_details.html', {
        "member": member,
        "age": age,
    })
    

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
                return render(request, "members/add_member.html", {
                    "errors": errors,
                    "member_choices": MEMBER_TYPE_CHOICES,
                    "status_choices": STATUS_CHOICES,
                    "gender_choices": GENDER_CHOICES,
                    "state_choices": STATE_CHOICES,
                })
            
        Member.objects.create(
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
        
        messages.success(request, "Member added successfully.")
        return redirect("members_list")

    return render(request, "members/add_member.html", {
        "member_choices": MEMBER_TYPE_CHOICES,
        "status_choices": STATUS_CHOICES,
        "gender_choices": GENDER_CHOICES,
        "state_choices": STATE_CHOICES,
    })


