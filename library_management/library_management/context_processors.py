from notifications.models import Notification

def notification_count(request):
    unread_count = Notification.objects.filter(is_read=False).count()
    return {
        "unread_count": unread_count,
    }
     