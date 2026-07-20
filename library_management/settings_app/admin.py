from django.contrib import admin
from .models import IssueSettings
from .models import BookSettings
from .models import NotificationSettings, EmailSettings


admin.site.register(IssueSettings)
admin.site.register(BookSettings)
admin.site.register(NotificationSettings)
admin.site.register(EmailSettings)
