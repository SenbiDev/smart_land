from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'), # Pakai Custom View
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.refresh_view, name='refresh'),
    path('users/', views.user_list_create, name='user-list'),
    path('users/<int:pk>/', views.user_detail, name='user-detail'),
    path('users/available-for-investor/', views.get_available_users_for_investor, name='available-users-investor'),
    path('roles/', views.role_list, name='role-list'), # Endpoint baru
]