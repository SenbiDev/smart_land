from django.urls import path
from . import views

urlpatterns = [
    # Auth Endpoints
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.refresh_view, name='refresh'),
    
    # Endpoint Role (PENTING untuk User Management Frontend)
    path('roles/', views.role_list, name='role-list'), 

    # User Management (Superadmin)
    path('users/', views.user_list_create, name='user-list-create'),
    path('users/<int:pk>/', views.user_detail, name='user-detail'),
]