from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [ "member_id", "full_name", "email", "phone", "member_type", "status"]
    search_fields = ["member_id", "full_name", "email", "phone"]
    list_filter = ['member_type', 'gender', 'status', 'join_date']
    ordering = ['-join_date']
    list_per_page = 10

