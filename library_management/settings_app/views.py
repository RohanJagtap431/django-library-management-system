from django.shortcuts import render, redirect
from .models import IssueSettings, BookSettings, NotificationSettings, EmailSettings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def settings_page(request): 
    student_settings = IssueSettings.objects.get(member_type="student")
    teacher_settings = IssueSettings.objects.get(member_type="teacher")
    staff_settings = IssueSettings.objects.get(member_type="staff")
    
    book_settings = BookSettings.objects.first()
    notification_settings = NotificationSettings.objects.first()
    email_settings = EmailSettings.objects.first()
    
    if not email_settings:
        email_settings = EmailSettings.objects.create()
    
    if request.method == "POST":
        student_max_books = int(
            request.POST.get("student_max_books") or student_settings.max_books
        )
        student_loan_period = int(
            request.POST.get("student_loan_period") or student_settings.loan_period
        )
        student_fine_per_day = int(
            request.POST.get("student_fine_per_day") or student_settings.fine_per_day
        )

        teacher_max_books = int(
            request.POST.get("teacher_max_books") or teacher_settings.max_books
        )
        teacher_loan_period = int(
            request.POST.get("teacher_loan_period") or teacher_settings.loan_period
        )
        teacher_fine_per_day = int(
            request.POST.get("teacher_fine_per_day") or teacher_settings.fine_per_day
        )

        staff_max_books = int(
            request.POST.get("staff_max_books") or staff_settings.max_books
        )
        staff_loan_period = int(
            request.POST.get("staff_loan_period") or staff_settings.loan_period
        )
        staff_fine_per_day = int(
            request.POST.get("staff_fine_per_day") or staff_settings.fine_per_day
        )
        
        
        low_stock_alert_limit = int(
            request.POST.get("low_stock_alert_limit") or book_settings.low_stock_alert_limit
        )
        
        notification_tone = request.POST.get("notification_tone")
        
        errors = {}
        
        if student_max_books <= 0:
            errors["student_max_books"] = "Maximum books must be greater than 0."
            
        if student_loan_period <= 0:
            errors["student_loan_period"] = "Loan period must be greater than 0."
            
        if student_fine_per_day <= 0:
            errors["student_fine_per_day"] = "Fine per day cannot be negative." 
            
        
        if teacher_max_books <= 0:
            errors["teacher_max_books"] = "Maximum books must be greater than 0."
            
        if teacher_loan_period <= 0:
            errors["teacher_loan_period"] = "Loan period must be greater than 0."
            
        if teacher_fine_per_day <= 0:
            errors["teacher_fine_per_day"] = "Fine per day cannot be negative." 
            
            
        if staff_max_books <= 0:
            errors["staff_max_books"] = "Maximum books must be greater than 0."
            
        if staff_loan_period <= 0:
            errors["staff_loan_period"] = "Loan period must be greater than 0."
            
        if staff_fine_per_day <= 0:
            errors["staff_fine_per_day"] = "Fine per day cannot be negative." 
            
        if low_stock_alert_limit <= 0:
            errors["low_stock_alert_limit"] = "Low stock alert limit must be greater than 0."
            
        if errors:
            
            for error in errors.values():
                messages.error(request, error)
            
            return render(request, 'settings/settings.html', {
                "student_max_books": student_max_books,
                "student_loan_period": student_loan_period,
                "student_fine_per_day": student_fine_per_day,
                "staff_max_books": staff_max_books,
                "staff_loan_period": staff_loan_period,
                "staff_fine_per_day": staff_fine_per_day,
                "teacher_max_books": teacher_max_books,
                "teacher_loan_period": teacher_loan_period,
                "teacher_fine_per_day": teacher_fine_per_day,
            })
        
        
        student_settings.max_books = student_max_books
        student_settings.loan_period = student_loan_period
        student_settings.fine_per_day = student_fine_per_day
        
        teacher_settings.max_books = teacher_max_books
        teacher_settings.loan_period = teacher_loan_period
        teacher_settings.fine_per_day = teacher_fine_per_day

        staff_settings.max_books = staff_max_books
        staff_settings.loan_period = staff_loan_period
        staff_settings.fine_per_day = staff_fine_per_day
        
        book_settings.low_stock_alert_limit = low_stock_alert_limit
        
        low_stock_alert = "low_stock_alert" in request.POST
        notification_settings.low_stock_alert = low_stock_alert
        
        book_issue_alert = "book_issue_alert" in request.POST
        notification_settings.book_issue_alert = book_issue_alert
        
        book_return_alert = "book_return_alert" in request.POST
        notification_settings.book_return_alert = book_return_alert
        
        overdue_alert = "overdue_alert" in request.POST
        notification_settings.overdue_alert = overdue_alert

        fine_alert = "fine_alert" in request.POST
        notification_settings.fine_alert = fine_alert
        
        new_member_alert = "new_member_alert" in request.POST
        notification_settings.new_member_alert = new_member_alert

        notification_sound = "notification_sound" in request.POST
        notification_settings.notification_sound = notification_sound
        notification_settings.notification_tone = notification_tone
        
        show_badge_count = "show_badge_count" in request.POST
        notification_settings.show_badge_count = show_badge_count

        show_deskgtop_notification = "show_deskgtop_notification" in request.POST
        notification_settings.show_deskgtop_notification = show_deskgtop_notification
        
        new_book_alert = "new_book_alert" in request.POST
        notification_settings.new_book_alert = new_book_alert
        
        welcome_email = "welcome_email" in request.POST
        email_settings.welcome_email = welcome_email

        book_issue_email = "book_issue_email" in request.POST
        email_settings.book_issue_email = book_issue_email

        book_return_email = "book_return_email" in request.POST
        email_settings.book_return_email = book_return_email

        overdue_reminder = "overdue_reminder" in request.POST
        email_settings.overdue_reminder = overdue_reminder
        
        notification_settings.save()

        book_settings.save()
        
        email_settings.save()
        
        student_settings.save()
        teacher_settings.save()
        staff_settings.save()
        
        messages.success(request, "Settings updated successfully.")
        return redirect("settings_page")
        
        
        
        
        
    context = {
        "student_settings": student_settings,
        "teacher_settings": teacher_settings,
        "staff_settings": staff_settings,
        "book_settings": book_settings,
        "notification_settings": notification_settings,
        "email_settings": email_settings,
    }
    
    
    return render(request, 'settings/settings.html', context)






