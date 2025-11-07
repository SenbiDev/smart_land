from django.urls import path
from .import views

urlpatterns = [
    path('expenses/', views.list_expense),
    path('expenses/<int:pk>/', views.expense_detail),
]