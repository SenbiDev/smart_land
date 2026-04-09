from django.urls import path
from . import views

urlpatterns = [
    # Auth Endpoints
    path('sso/google/', views.google_login_sso, name='sso-google'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email_view, name='verify-email'),
    path('resend-email-otp/', views.resend_email_otp_view, name='resend-email-otp'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.refresh_view, name='refresh'),
    
    # Endpoint Role (PENTING untuk User Management Frontend)
    path('roles/', views.role_list, name='role-list'), 

    # User Management (Superadmin)
    path('users/', views.user_list_create, name='user-list-create'),
    path('users/<int:pk>/', views.user_detail, name='user-detail'),
]