from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.list_products, name='list-products'),  # Tambah endpoint products
    path('productions/', views.list_production, name='list-production'),  # Tambah 'productions/'
    path('productions/<int:pk>/', views.production_detail, name='detail-production'),
]