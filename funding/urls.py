from django.urls import path
from . import views

urlpatterns = [
    path('fundings/', views.funding_list, name='funding-list'),
    path('fundings/<int:pk>/', views.funding_detail, name='funding-detail'),
]