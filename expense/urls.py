from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.list_expense, name='list-expense'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense-detail'),
]