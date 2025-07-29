from django.urls import path
from .import views

urlpatterns = [
    path('expensess/', views.expense_list_create),
    path('expensesss/<int:pk>/', views.expense_detail_update_delete),
    path('expenses/<int:funding_id>/expense-summary/', views.funding_expense_summary),
]
