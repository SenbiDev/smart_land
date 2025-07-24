from django.urls import path
from . import views

urlpatterns = [
    path('profit-distributions/', views.profit_distribution_list, name='profit-distribution-list'),
    path('profit-distributions/<int:pk>/', views.profit_distribution_detail, name='profit-distribution-detail'),
]
