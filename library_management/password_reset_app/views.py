from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from random import randint
import time
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User



def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        print("Forgot Password Called")
        print("Email:", email)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "auth/forgot_password.html", {
                "error": "Email not found!"
            })

        otp = randint(100000, 999999)

        request.session["reset_otp"] = str(otp)
        request.session["reset_email"] = email
        request.session["otp_created_at"] = time.time()

        send_mail(
            subject="Library Management System - OTP",
            message=f"Your OTP is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        print("Mail sent successfully")

        return redirect("verify_otp")
    
    return render(request, "auth/forgot_password.html")

def verify_otp(request):
    if not request.session.get("reset_email"):
        return redirect("forgot_password")
    
    email = request.session.get("reset_email")

    masked_email = ""

    if email:
        username, domain = email.split("@")
        masked_email = username[:2] + "****" + username[-2:] + "@" + domain
    
    otp_time = request.session.get("otp_created_at")
        
    remaining_time = max(0, 180 - int(time.time() - otp_time))

    if otp_time:
        if time.time() - otp_time > 180:
            return render(
                request,
                "auth/verify_otp.html",
                {
                    "email": masked_email,
                    "error": "OTP has expired. Please resend OTP.",
                    "remaining_time": remaining_time,
                }
            )

    if request.method == "POST":


        user_otp = request.POST.get("otp")
        session_otp = request.session.get("reset_otp")

        if user_otp == session_otp:
            request.session["otp_verified"] = True
            return redirect("reset_password")
        else:
            return render(
                request,
                "auth/verify_otp.html",
                {
                    "email": masked_email,
                    "error": "Invalid OTP",
                    "remaining_time": remaining_time,
                }
            )

    return render(
        request,
        "auth/verify_otp.html",
        {
            "email": masked_email,
            "remaining_time": remaining_time,
        }
    )


def reset_password(request):
    if not request.session.get("otp_verified"):
        return redirect("forgot_password")
    
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        
        email = request.session.get("reset_email")
        
        if password1 != password2:
            return render(request, "auth/reset_password.html", {
                "error": "Passwords do not match"
            })
            
        user = User.objects.get(email=email)
        
        user.set_password(password1)
        user.save()
        
        request.session["password_changed"] = True
            
        request.session.pop("reset_email", None)
        request.session.pop("reset_otp", None)
        request.session.pop("otp_created_at", None)
        request.session.pop("otp_verified", None)

        return redirect("password_success")
        
    
    return render(request, "auth/reset_password.html")

def password_success(request):
    if not request.session.get("password_changed"):
        return redirect("login")

    request.session.pop("password_changed", None)

    return render(request, "auth/password_success.html")

def back_to_forgot_password(request):
    request.session.pop("reset_email", None)
    request.session.pop("reset_otp", None)
    request.session.pop("otp_created_at", None)
    request.session.pop("otp_verified", None)

    return redirect("forgot_password")


def back_to_login(request):
    request.session.pop("reset_email", None)
    request.session.pop("reset_otp", None)
    request.session.pop("otp_created_at", None)
    request.session.pop("otp_verified", None)

    return redirect("login")

