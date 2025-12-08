from django.urls import path
from . import views

urlpatterns = [
    # Perhatikan bagian views.list_investor
    path('investors/', views.list_investor, name='list-investor'),
    path('investors/<int:pk>/', views.investor_detail, name='investor-detail'),
]