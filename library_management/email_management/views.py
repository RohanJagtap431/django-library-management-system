from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def email_dashboard(request):
    return render(request, "email_management/email_dashboard.html")

