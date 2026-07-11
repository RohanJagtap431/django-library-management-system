from django.shortcuts import render, redirect
from .models import IssueSettings
from django.contrib import messages


def settings_page(request): 
    student_settings = IssueSettings.objects.get(member_type="student")
    teacher_settings = IssueSettings.objects.get(member_type="teacher")
    staff_settings = IssueSettings.objects.get(member_type="staff")
    
    if request.method == "POST":
        student_max_books = int(request.POST.get("student_max_books", student_settings.max_books))
        student_loan_period = int(request.POST.get("student_loan_period", student_settings.loan_period))
        student_fine_per_day = int(request.POST.get("student_fine_per_day", student_settings.fine_per_day))

        teacher_max_books = int(request.POST.get("teacher_max_books", teacher_settings.max_books))
        teacher_loan_period = int(request.POST.get("teacher_loan_period", teacher_settings.loan_period))
        teacher_fine_per_day = int(request.POST.get("teacher_fine_per_day", teacher_settings.fine_per_day))

        staff_max_books = int(request.POST.get("staff_max_books", staff_settings.max_books))
        staff_loan_period = int(request.POST.get("staff_loan_period", staff_settings.loan_period))
        staff_fine_per_day = int(request.POST.get("staff_fine_per_day", staff_settings.fine_per_day))
        
        
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
            
        if errors:
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
        
        student_settings.save()
        teacher_settings.save()
        staff_settings.save()
        
        messages.success(request, "Issue settings updated successfully.")
        return redirect("settings_page")
        
        
        
        
        
    context = {
        "student_settings": student_settings,
        "teacher_settings": teacher_settings,
        "staff_settings": staff_settings,
        
    }
    
    
    return render(request, 'settings/settings.html', context)






