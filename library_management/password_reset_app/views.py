from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from random import randint
import time



def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

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
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect("verify_otp")
    
    return render(request, "auth/forgot_password.html")

def verify_otp(request):
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
    return render(request, "auth/reset_password.html")

def password_success(request):
    return render(request, "auth/password_success.html")
