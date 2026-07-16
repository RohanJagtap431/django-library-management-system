from notifications.models import Notification
from settings_app.models import NotificationSettings

def notification_count(request):
    unread_count = Notification.objects.filter(is_read=False).count()
    notification_settings = NotificationSettings.objects.first()
    return {
        "unread_count": unread_count,
        "notification_settings": notification_settings,
    }
     