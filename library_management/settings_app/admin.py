from django.contrib import admin
from .models import IssueSettings
from .models import BookSettings
from .models import NotificationSettings


admin.site.register(IssueSettings)
admin.site.register(BookSettings)
admin.site.register(NotificationSettings)