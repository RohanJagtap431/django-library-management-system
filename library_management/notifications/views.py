from django.shortcuts import render, redirect
from .models import Notification
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def notification_list(request):
    notifications = Notification.objects.all().order_by("-created_at")
    
    
    paginator = Paginator(notifications, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj,
    })

@login_required(login_url="login")  
def mark_all_as_read(request):
    if request.method == "POST":
        unread_notifications = Notification.objects.filter(is_read=False)
        unread_notifications.update(is_read=True)
        return redirect('notification_list')

@login_required(login_url="login")
def delete_all_notifications(request):
    if request.method == "POST":
        Notification.objects.all().delete()
        
        messages.success(
            request, "All notifications deleted successfully."
        )
        return redirect('notification_list')
    return render(request, 'notifications/delete_notifications.html')    