from django.contrib import admin
from .models import IssueSettings
from .models import BookSettings


admin.site.register(IssueSettings)
admin.site.register(BookSettings)
