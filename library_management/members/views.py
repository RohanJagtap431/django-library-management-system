from django.shortcuts import render, get_object_or_404
from .models import Member
from django.core.paginator import Paginator
from .models import Member, MEMBER_TYPE_CHOICES
from django.db.models import Q
from datetime import date


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