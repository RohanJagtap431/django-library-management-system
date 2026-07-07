from django.contrib import admin
from . models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["issue_id", "member", "book", "issue_date", "due_date", "return_date", "status", "fine"]
    list_filter = ["book", "member", "issue_date", "due_date", "return_date", "status"]
    search_fields = ["issue_id", "book__title", "book__isbn", "member__full_name", "member__member_id"]
    ordering = ['-created_at']
    list_per_page = 10
    list_display_links = ["issue_id"]
    readonly_fields = ["issue_id", "created_at", "updated_at"]