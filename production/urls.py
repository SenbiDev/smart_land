from django.urls import path
from . import views

urlpatterns = [
    # Endpoint Produk (List & Create)
    path('products/', views.list_create_products, name='list-create-products'),

    # Endpoint Produksi (List & Create) -> INI YANG MENGATASI 405
    path('productions/', views.list_create_productions, name='list-create-productions'),

    # Endpoint Detail (Update & Delete)
    path('productions/<int:pk>/', views.production_detail, name='detail-production'),
]