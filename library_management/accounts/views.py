from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout



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