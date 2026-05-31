from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-login-otp/', views.VerifyLoginOTPView.as_view(), name='verify-login-otp'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]