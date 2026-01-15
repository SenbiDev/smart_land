from django.urls import path
from . import views

urlpatterns = [
    path('sales/', views.list_sale, name='list-sale'), # Path ini akan menjadi /api/sales/sales/
    path('sales/create/', views.create_sale, name='create-sale'),
    path('sales/<int:pk>/', views.sale_detail, name='detail-sale'),
]