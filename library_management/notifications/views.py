from django.shortcuts import render, redirect
from .models import Notification
from django.core.paginator import Paginator


def notification_list(request):
    notifications = Notification.objects.all().order_by("-created_at")
    
    
    paginator = Paginator(notifications, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj,
    })
    
def mark_all_as_read(request):
    if request.method == "POST":
        unread_notifications = Notification.objects.filter(is_read=False)
        unread_notifications.update(is_read=True)
        return redirect('notification_list')
    