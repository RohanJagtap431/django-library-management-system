from django.shortcuts import render


def login_page(request):
    return render(request, 'auth/login.html')

def dashboard(request):
    return render(request, 'dashboard/dashboard.html')