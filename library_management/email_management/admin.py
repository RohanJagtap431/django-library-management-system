from django.contrib import admin
from .models import EmailTemplate, EmailHistory

admin.site.register(EmailTemplate)

@admin.register(EmailHistory)
class EmailHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "member",
        "subject",
        "email_type",
        "status",
        "sent_at",
    )

    list_filter = (
        "email_type",
        "status",
        "sent_at",
    )

    search_fields = (
        "recipient",
        "subject",
        "member__full_name",
    )

    ordering = ("-sent_at",)