from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User



def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(
            request,
            username=username,
            password=password
        )
        
        if user:
            login(request, user)
            
            remember = request.POST.get("remember_me")
            
            if not remember:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            return redirect("dashboard")
    return render(request, "auth/login.html")

def logout_page(request):
    logout(request)
    return redirect("login")

@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("password1")
        new_password = request.POST.get("password2")
        confirm_password = request.POST.get("password3")

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, "Current password is Incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            
            
            messages.success(request, "Password changed successfully.")
            return redirect("change_password")
        
    return render(request, "profile/change_password.html")

@login_required(login_url="login")
def profile(request):
    return render(request, "profile/admin_profile.html")

@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        
        if username != user.username and User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("edit_profile")

        
        if email != user.email and User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("edit_profile")

        user.username = username
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "profile/edit_profile.html")