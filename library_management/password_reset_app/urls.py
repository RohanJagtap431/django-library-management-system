from django.urls import path
from . import views

urlpatterns = [
    path("", views.forgot_password, name="forgot_password"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("password-success/", views.password_success, name="password_success"),
    path("back-to-forgot-password/", views.back_to_forgot_password, name="back_to_forgot_password"),
    path("back-to-login/", views.back_to_login, name="back_to_login"),
]
